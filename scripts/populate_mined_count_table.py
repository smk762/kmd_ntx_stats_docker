#!/usr/bin/env python3
import os
import json
import binascii
import time
import logging
import logging.handlers
from notary_pubkeys import known_addresses
from notary_info import notary_info, address_info, seasons_info
from rpclib import def_credentials
from os.path import expanduser
from dotenv import load_dotenv
import psycopg2

def get_mined_counts(season):
    sql = "SELECT name, COUNT(*), SUM(value), MAX(value), max(block_time), max(block) FROM mined WHERE block_time >= "+str(seasons_info[season]['start_time'])+" AND block_time <= "+str(seasons_info[season]['end_time'])+" GROUP BY name;"
    cursor.execute(sql)
    results = cursor.fetchall()
    time_stamp = int(time.time())
    for item in results:
        row_data = (item[0], season, int(item[1]), float(item[2]), float(item[3]), int(item[4]), int(item[5]), int(time_stamp))
        if item[0] in notary_info:
            print("Adding "+str(row_data)+" to get_mined_counts table")
        add_row_to_mined_count_tbl(row_data)

def add_row_to_mined_count_tbl(row_data):
    try:
        sql = "INSERT INTO mined_count"
        sql = sql+" (notary, season, count_mined, sum_mined, max_mined, max_block, last_mined, time_stamp)"
        sql = sql+" VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
load_dotenv()

conn = psycopg2.connect(
  host='localhost',
  user='postgres',
  password='postgres',
  port = "7654",
  database='postgres'
)
cursor = conn.cursor()

for season in seasons_info:
    get_mined_counts(season)

cursor.close()

conn.close()