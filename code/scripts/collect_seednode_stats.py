#!/usr/bin/env python3
import os
import csv
import sys
import json
import requests
import sqlite3
from dotenv import load_dotenv
from lib_db import CONN, CURSOR
from psycopg2.extras import execute_values

import requests
import logging
import logging.handlers

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


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

def get_seedinfo_from_csv():
	notary_seeds = []
	with open('notary_seednodes.csv', 'r') as file:
	    csv_file = csv.DictReader(file)
	    for row in csv_file:
	    	notary_seeds.append(dict(row))
	return notary_seeds

def add_notaries(notary_seeds):
	# Add to tracking
	for notary in notary_seeds:
		params = {
			"mmrpc": "2.0",
			"params": {
				"name":notary["notary"],
				"address":notary["3P IP Address"],
				"peer_id":notary["PeerID"]
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
	print('Deleted', CURSOR.rowcount, 'records from the table.')

def get_version_stats_from_sqlite_db(from_time=0, version=None):
	sql = f"SELECT * FROM stats_nodes WHERE version = '{version}' and timestamp > {from_time}"
	if not version:
		sql = f"SELECT * FROM stats_nodes WHERE version != '' and timestamp > {from_time}"
	rows = cursor.execute(sql).fetchall()
	resp = []
	for row in rows:
	    resp.append(dict(row))
	return resp

def get_registered_nodes_from_db():
        rows = cursor.execute("SELECT * FROM nodes;").fetchall()
        for row in rows:
            print(dict(row))	

def update_mm2_version_stats_row(row_data):
    try:
        sql = f"INSERT INTO mm2_version_stats \
                    (name, version, timestamp, error) \
                VALUES (%s, %s, %s, %s);"
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
    try:
        results = CURSOR.fetchall()
        return results
    except:
        return ()

def get_pgsql_latest():
    sql = f"SELECT MAX(timestamp) FROM mm2_version_stats;"
    CURSOR.execute(sql)
    try:
        results = CURSOR.fetchone()[0]
        return results
    except:
        return 0

def migrate_sqlite_to_pgsql(ts):
	print(f"Migrating to pgsql from {ts}")
	rows = get_version_stats_from_sqlite_db()
	if ts:
		rows = get_version_stats_from_sqlite_db(ts)
	for row in rows:
		if row["version"] != '':
			row_data = (row["name"], row["version"], row["timestamp"], row["error"])
			update_mm2_version_stats_row(row_data)


if __name__ == '__main__':
	logger.info(f"Local MM2 version: {get_local_version().json()}")
	if len(sys.argv) > 1:
		if sys.argv[1] == 'empty':
			empty_pg_table()
		elif sys.argv[1] == 'start':
			start_stats_collection()
		elif sys.argv[1] == 'nodes':
			get_registered_nodes_from_db()
		elif sys.argv[1] == 'register':
			notary_seeds = get_seedinfo_from_csv()
			add_notaries(notary_seeds)
		elif sys.argv[1] == 'migrate':
			latest_record = get_pgsql_latest()
			logger.info(f"Latest entry in pgsql db: {latest_record}")
			migrate_sqlite_to_pgsql(latest_record)
		elif sys.argv[1] == 'sqlite_data':
			sqlite_version_stats = get_version_stats_from_sqlite_db(0)
			print(f"sqlite_version_stats: {sqlite_version_stats}")
		elif sys.argv[1] == 'pgsql_data':
			pgsql_version_stats = get_version_stats_from_pgsql_db(0)
			print(f"pgsql_version_stats: {pgsql_version_stats}")
		else:
			print("invalid param, must be in [empty, start, nodes, register, migrate, sqlite_data, pgsql_data]")
	else:
		print("no param given, must be in [empty, start, nodes, register, migrate, sqlite_data, pgsql_data]")
	conn.close()
	CONN.close()

