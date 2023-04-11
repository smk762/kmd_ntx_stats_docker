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
import lib_electrum as electrum

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

VERSION_TIMESPANS_URL = "https://raw.githubusercontent.com/KomodoPlatform/dPoW/master/doc/seed_version_epochs.json"
VERSION_DATA = requests.get(VERSION_TIMESPANS_URL).json()
SCRIPT_PATH = os.path.abspath(os.path.dirname(sys.argv[0]))

# Date:   Mon Nov 14 13:40:18 2022 +0300 6e4de5d21
# Date:   Wed Aug 10 18:42:54 2022 +0700 0f6c72615
# Date:   Mon Jul 11 11:11:34 2022 +0300 ce32ab8da
# Date:   Tue Jun 21 15:04:00 2022 +0700 b8598439a

'''
This script collects seednode stats for notaries using the correct version.
At the end of the season, or after an update, run with the `rectify_scores` param to update the scores.
'''

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
    active_versions = []
    for version in VERSION_DATA:
        if int(ts) > VERSION_DATA[version]["start"] and int(ts) < VERSION_DATA[version]["end"]:
            active_versions.append(version)
    return active_versions


def get_seedinfo_from_json():
    file = f'{SCRIPT_PATH}/notary_seednodes.json'
    print(file)
    with open(file, 'r') as f:
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
            print(notary)
            r = mm2_proxy('add_node_to_version_stat', params)

def remove_notaries(notary_seeds):
    # Add to tracking
    for season in notary_seeds:
        for notary in notary_seeds[season]:
            params = {
                "mmrpc": "2.0",
                "params": {
                    "name": notary
                }
            }
            print(notary)
            r = mm2_proxy('remove_node_from_version_stat', params)


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
    rows = CURSOR.execute("DELETE FROM seednode_version_stats;")
    CONN.commit()
    print('Deleted', CURSOR.rowcount, 'records from seednode_version_stats PgSQL table.')


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

def deregister_nodes_from_db(notary_seeds):
    for season in notary_seeds:
        for notary in notary_seeds[season]:
	        cursor.execute(f"DELETE FROM nodes where name = '{notary}';")
	        cursor.commit()

def update_seednode_version_stats_row(row_data):
    try:
        timestamp = row_data[3]
        season = validate.get_season(timestamp)
        sql = f"INSERT INTO seednode_version_stats \
                    (name, season, version, timestamp, error, score) \
                VALUES (%s, %s, %s, %s, %s, %s) \
                ON CONFLICT ON CONSTRAINT unique_mm2_version_stat \
                DO UPDATE SET \
                    season='{season}', version='{row_data[2]}', \
                    timestamp='{timestamp}', error='{row_data[4]}', \
                    score='{row_data[5]}';"

        CURSOR.execute(sql, row_data)
        CONN.commit()

    except Exception as e:
        logger.error(f"Exception in [update_seednode_version_stats_row]: {e}")
        logger.error(f"[update_seednode_version_stats_row] sql: {sql}")
        logger.error(f"[update_seednode_version_stats_row] row_data: {row_data}")
        CONN.rollback()

def rectify_scores():
    for commithash in VERSION_DATA:
        start_time = VERSION_DATA[commithash]["start"]
        end_time = VERSION_DATA[commithash]["end"]
        print(f"\n======= commithash: {commithash} =======")
        print(f"start_time: {start_time}")
        print(f"end_time: {end_time}")

        sql = f"SELECT * FROM seednode_version_stats WHERE version LIKE '%{commithash}%' AND timestamp < {end_time} AND timestamp > {start_time};"
        CURSOR.execute(sql)
        print(f"Records valid for scoring: {CURSOR.rowcount}")
        sql = f"UPDATE seednode_version_stats SET score = 0.2 WHERE version LIKE '%{commithash}%' AND timestamp < {end_time} AND timestamp > {start_time};"
        CURSOR.execute(sql)
        CONN.commit()

        sql = f"SELECT * FROM seednode_version_stats WHERE version LIKE '%{commithash}%' AND timestamp > {end_time};"
        CURSOR.execute(sql)
        print(f"Records after end time: {CURSOR.rowcount}")
        sql = f"UPDATE seednode_version_stats SET score = 0 WHERE version LIKE '%{commithash}%' AND timestamp > {end_time};"
        CURSOR.execute(sql)
        CONN.commit()



def get_version_stats_from_pgsql_db():
    sql = f"SELECT * FROM seednode_version_stats;"
    CURSOR.execute(sql)
    return get_results_or_none(CURSOR)


def get_version_list_from_pgsql_db():
    sql = f"SELECT DISTINCT version FROM seednode_version_stats;"
    CURSOR.execute(sql)
    return get_results_or_none(CURSOR)


def get_pgsql_latest():
    sql = f"SELECT MAX(timestamp) FROM seednode_version_stats;"
    CURSOR.execute(sql)
    try:
        results = CURSOR.fetchone()[0]
        return results
    except:
        return 0


def round_ts_to_hour(timestamp):
    return round(int(timestamp)/3600)*3600


def get_version_score(version, timestamp, notary, season, wss_detected=False):
    active_versions_at = get_active_mm2_versions(timestamp)
    print(f"mm2 active versions: {active_versions_at}")
    for v in active_versions_at:
        if version.find(v) > -1:
            if wss_detected:
                return 0.2
            if test_wss(notary, season):
                return 0.2
            return 0.01
    return 0


def test_wss(notary, season):
    
    if season in notary_seeds:
        url = notary_seeds[season][notary]["IP"]
        peer_id = notary_seeds[season][notary]["PeerID"]
        data = {"userpass": "userpass"}
        resp = electrum.get_from_electrum_ssl(url, 38900, "version", data)
        if str(resp).find("read operation timed out") > -1:
            print(f"{notary}: WSS connection detected...")
            return True
        else:
            print(f"{notary}: {resp}")
        return False


def migrate_sqlite_to_pgsql(ts):
    print(f"Migrating to pgsql from {ts}")
    wss_confirmed = []
    rows = get_version_stats_from_sqlite_db()

    if ts:
        rows = get_version_stats_from_sqlite_db(ts)

    for row in rows:
        print(row)
        if row["version"] != '':
            wss_detected = False
            hr_timestamp = round_ts_to_hour(row["timestamp"])   
            season = validate.get_season(hr_timestamp)

            if row["name"] not in wss_confirmed:
                if test_wss(row["name"], season):
                    wss_confirmed.append(row["name"])

            if row["name"] in wss_confirmed:
                wss_detected = True
            
            score = get_version_score(row["version"], hr_timestamp, row["name"], season, wss_detected)
            row_data = (row["name"], season, row["version"], hr_timestamp, row["error"], score)

            print(row_data)
            update_seednode_version_stats_row(row_data)

def import_seednode_stats(season):
    resp = requests.get("http://stats.kmd.io/api/source/seednode_version_stats/").json()

    for i in resp["results"]:
        row_data = (i["name"], i["season"], i["version"], i["timestamp"], i["error"], i["score"])
        print(row_data)
        update_seednode_version_stats_row(row_data)

    if resp["next"]:
        while resp["next"]:
            resp = requests.get(resp["next"]).json()

            for i in resp["results"]:
                row_data = (i["name"], i["season"], i["version"], i["timestamp"], i["error"], i["score"])
                print(row_data)
                update_seednode_version_stats_row(row_data)




if __name__ == '__main__':

    notary_seeds = get_seedinfo_from_json()
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

        # Run manually to register nodes via JSON file
        elif sys.argv[1] == 'register':
            remove_notaries(notary_seeds)
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
            pgsql_version_stats = get_version_stats_from_pgsql_db()
            print(f"pgsql_version_stats: {pgsql_version_stats}")

        # outputs pgSQL data
        elif sys.argv[1] == 'versions_list':
            pgsql_version_list = get_version_list_from_pgsql_db()
            print(f"pgsql_version_list: {pgsql_version_list}")

        # outputs pgSQL data
        elif sys.argv[1] == 'rectify_scores':
            result = rectify_scores()

        # tests WSS connection
        elif sys.argv[1] == 'wss_test':
            for season in notary_seeds:
                for notary in notary_seeds[season]:
                    test_wss(notary, season)
                
        # import data from other server
        elif sys.argv[1] == 'import':
            for season in notary_seeds:
                import_seednode_stats(season)
                

        else:
            print("invalid param, must be in [empty, start, nodes, register, migrate, sqlite_data, pgsql_data, wss_test, import]")

    else:
        print("no param given, must be in [empty, start, nodes, register, migrate, sqlite_data, pgsql_data, wss_test, import]")

    #get_version_stats_from_db()
    conn.close()
    CONN.close()
