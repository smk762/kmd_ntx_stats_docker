#!/usr/bin/env python3
import os
import json
import binascii
import time
import logging
import logging.handlers
from notary_pubkeys import known_addresses
from rpclib import def_credentials
from os.path import expanduser
from dotenv import load_dotenv
import psycopg2

startblock = 1444000

def get_max_col_val_in_table(col, table):
    sql = "SELECT MAX("+col+") FROM "+table+";"
    cursor.execute(sql)
    max_val = cursor.fetchone()
    logger.info("Max "+col+" value is "+str(max_val))
    return max_val

def get_mined_counts():
    sql = "SELECT name, SUM(value), MAX(value) FROM mined WHERE block >= "+str(startblock)+" GROUP BY name;"
    cursor.execute(sql)
    results = cursor.fetchall()
    results_list = []
    print("Aggregating "+str(len(results))+" rows from mined table")
    for item in results:
        results_list.append({
                "name":item[0],
                "sum":float(item[1]),
                "max":float(item[2]),
            })
    logger.info("Results: "+str(results_list))
    return results_list

def update_table(results_list):
    timestamp = int(time.time())
    for item in results_list:
        row_data = (item['name'], item['sum'], item['max'], timestamp)
        print("Adding "+item['name']+" to get_mined_counts table")
        add_row_to_mined_count_tbl(row_data)

def add_row_to_mined_count_tbl(row_data):
    try:
        sql = "INSERT INTO mined_count"
        sql = sql+" (notary, sum_mined, max_mined, timestamp)"
        sql = sql+" VALUES (%s, %s, %s, %s);"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

home = expanduser("~")

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

results_list = get_mined_counts()
update_table(results_list)

cursor.close();

conn.close();