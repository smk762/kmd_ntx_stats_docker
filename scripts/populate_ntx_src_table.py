#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
import logging.handlers
import psycopg2
import threading
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
Script runtime is around 5-10 mins sepending on number of seasons to aggregate
'''

# set this to True to quickly update tables with most recent data
skip_until_yesterday = False

load_dotenv()

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
    # Get chain and time of last ntx
    cursor.execute("SELECT notary, chain, block_height from last_notarised;")
    last_ntx = cursor.fetchall()
    notary_last_ntx = {}
    for item in last_ntx:
        notary = item[0]
        chain = item[1]
        block_height = item[2]
        if notary not in notary_last_ntx:
            notary_last_ntx.update({notary:{}})
        notary_last_ntx[notary].update({chain:block_height})

    # Get chain and time of last btc ntx
    cursor.execute("SELECT notary, block_height from last_notarised;")
    last_btc_ntx = cursor.fetchall()
    notary_last_btc_ntx = {}
    for item in last_btc_ntx:
        notary = item[0]
        block_height = item[1]
        if notary not in notary_last_btc_ntx:
            notary_last_btc_ntx.update({notary:{}})
        notary_last_btc_ntx.update({notary:block_height})

    records = []
    start = time.time()
    i = 1
    for txid in unrecorded_txids:
        row_data = ntx_lib.get_ntx_data(txid)
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

            # update last ntx or last btc if newer than in tables.
            for notary in notaries:
                last_ntx_row_data = (notary, chain, txid, block_height,
                                     block_time, season)

                if notary in notary_last_ntx:
                    if chain not in notary_last_ntx[notary]:
                        notary_last_ntx[notary].update({chain:0})
                    if block_height > notary_last_ntx[notary][chain]:
                        table_lib.update_last_ntx_tbl(conn, cursor, last_ntx_row_data)
                else:
                    table_lib.update_last_ntx_tbl(conn, cursor, last_ntx_row_data)

                if chain == 'KMD':
                    last_btc_ntx_row_data = (notary, txid, block_height,
                                         block_time, season)

                    
                    if notary in notary_last_btc_ntx:
                        if block_height > notary_last_btc_ntx[notary]:
                            table_lib.update_last_btc_ntx_tbl(conn, cursor, last_btc_ntx_row_data)
                    else:
                        table_lib.update_last_btc_ntx_tbl(conn, cursor, last_btc_ntx_row_data)

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
    execute_values(cursor, "INSERT INTO notarised (chain, block_height, block_time, block_datetime, block_hash, \
                            notaries, ac_ntx_blockhash, ac_ntx_height, txid, opret, season) VALUES %s", records)

    conn.commit()
    logger.info("Notarised blocks updated!")
    logger.info("NTX Address transactions processed: "+str(len(unrecorded_txids)))
    logger.info(str(len(unrecorded_txids))+" notarised TXIDs added to table")



update_notarisations()

cursor.close()

conn.close()
