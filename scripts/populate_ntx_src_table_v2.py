#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
import logging.handlers
import psycopg2
import threading
import requests
from decimal import *
from datetime import datetime as dt
import datetime
from dotenv import load_dotenv
from rpclib import def_credentials
from psycopg2.extras import execute_values
import ntx_lib 
import table_lib
from electrum_lib import get_ac_block_info
from notary_lib import *
from coins_lib import third_party_coins, antara_coins, ex_antara_coins, all_antara_coins, all_coins

'''
This script scans the blockchain for notarisation txids that are not already recorded in the database.
After updaing the "notarised" table, aggregations are performed to get counts for notaries and chains within each season.
It is intended to be run as a cronjob every 15-30 min
Script runtime is around 5-10 mins, except for initial population which is up to 1 day per season
'''

# set this to True to quickly update tables with most recent data
skip_until_yesterday = False

load_dotenv()
coins_data = requests.get("http://notary.earth:8762/api/info/coins/?dpow_active=1").json()['results'][0]
coins_list = list(coins_data.keys())

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

conn = table_lib.connect_db()
cursor = conn.cursor()

rpc = {}
rpc["KMD"] = def_credentials("KMD")

ntx_addr = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'

season = get_season(time.time())
tip = int(rpc["KMD"].getblockcount())
recorded_txids = []
start_block = seasons_info[season]["start_block"]
if skip_until_yesterday:
    start_block = tip - 24*60*1
all_txids = []
chunk_size = 100000

logger.info("Getting existing TXIDs from database...")
cursor.execute("SELECT txid from notarised;")
existing_txids = cursor.fetchall()


while tip - start_block > chunk_size:
    logger.info("Getting notarization TXIDs from block chain data for blocks " \
           +str(start_block+1)+" to "+str(start_block+chunk_size)+"...")
    all_txids += ntx_lib.get_ntx_txids(ntx_addr, start_block+1, start_block+chunk_size)
    start_block += chunk_size
all_txids += ntx_lib.get_ntx_txids(ntx_addr, start_block+1, tip)

for txid in existing_txids:
    recorded_txids.append(txid[0])
unrecorded_txids = set(all_txids) - set(recorded_txids)
logger.info("TXIDs in chain: "+str(len(all_txids)))
logger.info("TXIDs in chain (set): "+str(len(set(all_txids))))
logger.info("TXIDs in database: "+str(len(recorded_txids)))
logger.info("TXIDs in database (set): "+str(len(set(recorded_txids))))
logger.info("TXIDs not in database: "+str(len(unrecorded_txids)))

# Seems to be two txids that are duplicate.
# TODO: scan to find out what the duplicate txids are and which blocks they are in

def update_notarisations():

    records = []
    start = time.time()
    i = 1

    for chain in coins_list:
        block = tip
        print(chain)
        while block > start_block:
            ntx_info = rpc["KMD"].scanNotarisationsDB(str(block-1), chain)
            if ntx_info is None:
                break
            txid = ntx_info['hash']
            block = ntx_info['height']
            if txid not in recorded_txids:
                opreturn = ntx_info['opreturn']
                print(block)
                row_data = ntx_lib.get_ntx_data_v2(txid)
                if row_data is not None:
                    chain = row_data[0]
                    block_height = row_data[1]
                    block_time = row_data[2]
                    txid = row_data[8]
                    notaries = row_data[5]
                    for season_num in seasons_info:
                        if block_time < seasons_info[season_num]['end_time']:
                            season = season_num
                            break

                    records.append(row_data)
                    if len(records) == 10:
                        now = time.time()
                        pct = len(records)*i/len(unrecorded_txids)*100
                        runtime = int(now-start)
                        est_end = int(100/pct*runtime)
                        pct = round(len(records)*i/len(unrecorded_txids)*100,3)
                        logger.info(str(pct)+"% :"+str(len(records)*i)+"/"+str(len(unrecorded_txids))+" records added to db ["+str(runtime)+"/"+str(est_end)+" sec]")
                        # logger.info("records: "+str(records))
                        logger.info("-----------------------------")
                        execute_values(cursor, "INSERT INTO notarised (chain, block_height, block_time, block_datetime, \
                                                block_hash, notaries, ac_ntx_blockhash, ac_ntx_height, txid, opret, \
                                                season) VALUES %s", records)
                        conn.commit()
                        records = []
                        i += 1
                        if i%5 == 0:
                            cursor.execute("SELECT COUNT(*) from notarised;")
                            block_count = cursor.fetchone()
                            logger.info("notarisations in database: "+str(block_count[0])+"/"+str(len(all_txids)))
            else:
                print("skipping "+str(block))

    execute_values(cursor, "INSERT INTO notarised (chain, block_height, block_time, block_datetime, block_hash, \
                            notaries, ac_ntx_blockhash, ac_ntx_height, txid, opret, season) VALUES %s", records)

    conn.commit()
    logger.info("Notarised blocks updated!")
    logger.info("NTX Address transactions processed: "+str(len(unrecorded_txids)))
    logger.info(str(len(unrecorded_txids))+" notarised TXIDs added to table")



update_notarisations()

cursor.close()

conn.close()
