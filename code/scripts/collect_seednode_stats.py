#!/usr/bin/env python3
import os
import csv
import sys
import json
import time
import requests
import sqlite3
from dotenv import load_dotenv
from lib_db import CONN, CURSOR
from psycopg2.extras import execute_values

import requests
import logging
import logging.handlers

from lib_helper import *
import lib_validate as validate

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

VERSION_TIMESPANS_URL = "https://raw.githubusercontent.com/smk762/DragonhoundTools/master/atomicdex/seednode_version.json"

# ENV VARS
load_dotenv()
MM2_USERPASS = os.getenv("MM2_USERPASS")
MM2_IP = "http://127.0.0.1:7783"
DB_PATH = os.getenv("DB_PATH")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


def mm2_proxy(method, params=None):
	if not params:
		params = {}
	params.update({
		"method": method,
		"userpass": MM2_USERPASS,
		})
	r = requests.post(MM2_IP, json.dumps(params))
	print(r.json())
	return r


def get_active_mm2_versions(ts):
	data = requests.get(VERSION_TIMESPANS_URL).json()
	active_versions = []
	for version in data:
		if int(ts) > data[version]["start"] and int(ts) < data[version]["end"]:
			active_versions.append(version)
	return active_versions


def get_seedinfo_from_csv():
	notary_seeds = []
	with open('notary_seednodes.csv', 'r') as file:
	    csv_file = csv.DictReader(file)
	    for row in csv_file:
	    	notary_seeds.append(dict(row))
	return notary_seeds


def get_seedinfo_from_json():
	notary_seeds = []
	with open('notary_seednodes.json', 'r') as f:
		return json.load(f)


def add_notaries(notary_seeds):
	# Add to tracking
	for season in notary_seeds:
		for notary in notary_seeds[season]:
			params = {
				"mmrpc": "2.0",
				"params": {
					"name": notary,
					"address": notary_seeds[season][notary]["IP"],
					"peer_id": notary_seeds[season][notary]["PeerID"]
				}
			}
			r = mm2_proxy('add_node_to_version_stat', params)


def get_local_version():
    return mm2_proxy('version')


def start_stats_collection():
	# set to every 30 minutes
	params = {
		"mmrpc": "2.0",
		"params": {
			"interval":1800,
		}
	}
	print("Starting stats collection...")
	r = mm2_proxy('start_version_stat_collection', params)


def empty_pg_table():
	rows = CURSOR.execute("DELETE FROM mm2_version_stats;")
	CONN.commit()
	print('Deleted', CURSOR.rowcount, 'records from mm2_version_stats PgSQL table.')


def empty_sqlite_table(table):
	rows = cursor.execute(f"DELETE FROM {table};")
	conn.commit()
	print('Deleted', cursor.rowcount, 'records from the table.')


def get_version_stats_from_sqlite_db(from_time=0, version=None):
	sql = f"SELECT * FROM stats_nodes WHERE version = '{version}' and timestamp > {from_time}"
	if not version:
		sql = f"SELECT * FROM stats_nodes WHERE version != '' and timestamp > {from_time}"
	print(sql)
	rows = cursor.execute(sql).fetchall()
	resp = []
	for row in rows:
	    resp.append(dict(row))
	print(f"{len(resp)} records returned")
	return resp


def get_version_stats_from_db():
	rows = cursor.execute("SELECT * FROM stats_nodes WHERE version != ''").fetchall()
	for row in rows:
	    print(dict(row))

def get_registered_nodes_from_db():
        rows = cursor.execute("SELECT * FROM nodes;").fetchall()
        print("---------")
        for row in rows:
            print(dict(row))	
        print("---------")


def update_mm2_version_stats_row(row_data):
    try:
        sql = f"INSERT INTO mm2_version_stats \
                    (name, season, version, timestamp, error, score) \
                VALUES (%s, %s, %s, %s, %s, %s);"
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        #logger.error(f"Exception in [update_mm2_version_stats_row]: {e}")
        #logger.error(f"[update_mm2_version_stats_row] sql: {sql}")
        #logger.error(f"[update_mm2_version_stats_row] row_data: {row_data}")
        CONN.rollback()


def get_version_stats_from_pgsql_db():
    sql = f"SELECT * FROM mm2_version_stats;"
    CURSOR.execute(sql)
    return get_results_or_none(CURSOR)

def get_pgsql_latest():
    sql = f"SELECT MAX(timestamp) FROM mm2_version_stats;"
    CURSOR.execute(sql)
    try:
        results = CURSOR.fetchone()[0]
        return results
    except:
        return 0


def round_ts_to_hour(timestamp):
	return round(int(timestamp)/3600)*3600

def get_version_score(version, timestamp):
	active_versions_at = get_active_mm2_versions(timestamp)
	if version in active_versions_at:
		return 0.2
	return 0


def migrate_sqlite_to_pgsql(ts):
	print(f"Migrating to pgsql from {ts}")
	rows = get_version_stats_from_sqlite_db()
	if ts:
		rows = get_version_stats_from_sqlite_db(ts)
	for row in rows:
		print(row)
		if row["version"] != '':
			hr_timestamp = round_ts_to_hour(row["timestamp"])

			season = validate.get_season(hr_timestamp)
			score = get_version_score(row["version"], hr_timestamp)
			row_data = (row["name"], season, row["version"], hr_timestamp, row["error"], score)
			print(row_data)
			update_mm2_version_stats_row(row_data)


if __name__ == '__main__':

	active_versions = get_active_mm2_versions(time.time())
	logger.info(f"Local MM2 version: {get_local_version().json()}")
	print(f"active_versions: {active_versions}")

	if len(sys.argv) > 1:

		# Clears tables
		if sys.argv[1] == 'empty':
			empty_pg_table()

		# Starts stats collection in sqliteDB
		# mm2 Dockerfile takes care of this in init.sh
		elif sys.argv[1] == 'start':
			start_stats_collection()

		# Returns registered nodes
		elif sys.argv[1] == 'nodes':
			get_registered_nodes_from_db()

		# Run manually to register nodes via CSV file
		elif sys.argv[1] == 'register':
			notary_seeds = get_seedinfo_from_json()
			add_notaries(notary_seeds)

		# This is what gets cron'd
		elif sys.argv[1] == 'migrate':
			latest_record = get_pgsql_latest()
			logger.info(f"Latest entry in pgsql db: {latest_record}")
			migrate_sqlite_to_pgsql(latest_record)

		# outputs SQLite data
		elif sys.argv[1] == 'sqlite_data':
			sqlite_version_stats = get_version_stats_from_sqlite_db(0)
			print(f"sqlite_version_stats: {sqlite_version_stats}")

		# outputs pgSQL data
		elif sys.argv[1] == 'pgsql_data':
			pgsql_version_stats = get_version_stats_from_pgsql_db(0)
			print(f"pgsql_version_stats: {pgsql_version_stats}")

		else:
			print("invalid param, must be in [empty, start, nodes, register, migrate, sqlite_data, pgsql_data]")

	else:
		print("no param given, must be in [empty, start, nodes, register, migrate, sqlite_data, pgsql_data]")

	#get_version_stats_from_db()
	conn.close()
	CONN.close()
