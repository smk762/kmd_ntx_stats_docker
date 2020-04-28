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
    last_block = cursor.fetchone()
    logger.info("Last block recorded was "+str(last_block[0]))
    return last_block[0]

def add_row_to_mined_tbl(row_data):
    try:
        sql = "INSERT INTO mined"
        sql = sql+" (block, block_time, value, address, name)"
        sql = sql+" VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0


def get_miners(start, end):
    count = 0
    for block in range(start, end):
        blockinfo = rpc["KMD"].getblock(str(block), 2)
        blocktime = blockinfo['time']
        for tx in blockinfo['tx']:
            if 'coinbase' in tx['vin'][0]:
                if 'addresses' in tx['vout'][0]['scriptPubKey']:
                    address = tx['vout'][0]['scriptPubKey']['addresses'][0]
                    if address in known_addresses:
                        name = known_addresses[address]
                    else:
                        name = "UNKNOWN"
                else:
                    address = "N/A"
                    name = "non-standard"

                value = tx['vout'][0]['value']
                logger.info(str(value)+" KMD mined by ["+name+"] in block "+str(block)+" at "+str(blocktime))
                row_data = (block, blocktime, value, address, name)
                count += add_row_to_mined_tbl(row_data)

def get_mined_counts():
    sql = "SELECT name, SUM(value), MAX(value), max(block_time) FROM mined WHERE block >= "+str(startblock)+" GROUP BY name;"
    cursor.execute(sql)
    results = cursor.fetchall()
    results_list = []
    print("Aggregating "+str(len(results))+" rows from mined table")
    timestamp = int(time.time())
    for item in results:
        row_data = (item[0], float(item[1]), float(item[2]), int(item[3]), int(timestamp))
        print("Adding "+item[0]+" to get_mined_counts table")
        add_row_to_mined_count_tbl(row_data)

def add_row_to_mined_count_tbl(row_data):
    try:
        sql = "INSERT INTO mined_count"
        sql = sql+" (notary, sum_mined, max_mined, last_mined, timestamp)"
        sql = sql+" VALUES (%s, %s, %s, %s, %s);"
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

rpc = {}
rpc["KMD"] = def_credentials("KMD")

ntx_data = {}
ntx_addr = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'
try:
    startblock = get_max_col_val_in_table("block", "mined")-1
except:
    startblock = 1444000 # season start block
endblock = 7113400 # season end block (or tip if mid season)
tip = int(rpc["KMD"].getblockcount())
#startblock = tip - 2000
if endblock > tip:
    endblock = tip

get_miners(startblock, endblock)
get_mined_counts()