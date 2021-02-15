#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
import logging
import logging.handlers
import psycopg2
import threading
from decimal import *
from datetime import datetime as dt
import datetime
from dotenv import load_dotenv
from lib_rpc import def_credentials
from psycopg2.extras import execute_values
from lib_electrum import get_ac_block_info
from lib_notary import *

'''
This script scans the blockchain for notarisation txids that are not already recorded in the database.
After updaing the "notarised" table, aggregations are performed to get counts for notaries and chains within each season.
It is intended to be run as a cronjob every 15-30 min
Script runtime is around 5-10 mins, except for initial population which is up to 1 day per season
'''

load_dotenv()

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

conn = connect_db()
cursor = conn.cursor()


chains = []
cursor.execute("SELECT DISTINCT chain FROM notarised;")
chain_results = cursor.fetchall()
for result in chain_results:
    chains.append(result[0])

seasons = []
cursor.execute("SELECT DISTINCT season FROM notarised;")
season_results = cursor.fetchall()
for result in season_results:
    seasons.append(result[0])

for chain in chains:
    for season in seasons:
        cursor.execute("SELECT MAX(block_height), MAX(block_time), \
                        MIN(block_height), MIN(block_time), COUNT(*) \
                        FROM notarised WHERE chain = '"+chain+"' \
                        AND season = '"+season+"';")
        ntx_results = cursor.fetchone()
        print(chain+" "+season+": "+str(ntx_results))
        max_blk = ntx_results[0]
        max_blk_time = ntx_results[1]
        min_blk = ntx_results[2]
        min_blk_time = ntx_results[3]
        ntx_count = ntx_results[4]
        if max_blk is not None:
            row_data = (chain, min_blk, max_blk, min_blk_time, max_blk_time, ntx_count, season)

            sql = "INSERT INTO notarised_tenure (chain, first_ntx_block, \
                last_ntx_block, first_ntx_block_time, last_ntx_block_time, ntx_count, season) \
                VALUES (%s, %s, %s, %s, %s, %s, %s) \
                ON CONFLICT ON CONSTRAINT unique_chain_season_tenure DO UPDATE SET \
                first_ntx_block='"+str(row_data[1])+"', last_ntx_block="+str(row_data[2])+", \
                first_ntx_block_time="+str(row_data[3])+", last_ntx_block_time="+str(row_data[4])+", \
                ntx_count="+str(row_data[5])+";"
            cursor.execute(sql, row_data)
            conn.commit()

            logger.info(chain+" "+season+" notarised tenure updated!")


cursor.close()

conn.close()
