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
from rpclib import def_credentials
from psycopg2.extras import execute_values
from electrum_lib import get_ac_block_info
from notary_lib import *

'''
This script scans the blockchain for notarisation txids that are not already recorded in the database.
After updaing the "notarised" table, aggregations are performed to get counts for notaries and chains within each season.
It is intended to be run as a cronjob every 15-30 min
Script runtime is around 5-10 mins, except for initial population which is up to 1 day per season
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

conn = connect_db()
cursor = conn.cursor()

rpc = {}
rpc["KMD"] = def_credentials("KMD")

ntx_addr = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'

season = get_season(time.time())
tip = int(rpc["KMD"].getblockcount())
recorded_txids = []
start_block = seasons_info[season]["start_block"]-3000
if skip_until_yesterday:
    start_block = tip - 24*60
all_txids = []
chunk_size = 100000

logger.info("Getting existing TXIDs from database...")
cursor.execute("SELECT txid from notarised;")
existing_txids = cursor.fetchall()


while tip - start_block > chunk_size:
    logger.info("Getting notarization TXIDs from block chain data for blocks " \
           +str(start_block+1)+" to "+str(start_block+chunk_size)+"...")
    all_txids += get_ntx_txids(ntx_addr, start_block+1, start_block+chunk_size)
    start_block += chunk_size
all_txids += get_ntx_txids(ntx_addr, start_block+1, tip)

for txid in existing_txids:
    recorded_txids.append(txid[0])
unrecorded_txids = set(all_txids) - set(recorded_txids)
logger.info("TXIDs in chain: "+str(len(all_txids)))
logger.info("TXIDs in chain (set): "+str(len(set(all_txids))))
logger.info("TXIDs in database: "+str(len(recorded_txids)))
logger.info("TXIDs in database (set): "+str(len(set(recorded_txids))))
logger.info("TXIDs not in database: "+str(len(unrecorded_txids)))


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

    start = time.time()
    i = 1
    j = 0
    for txid in all_txids:
        row_data = get_ntx_data(txid)
        j += 1
        num_unrecorded_txids = len(all_txids)
        cursor.execute("DELETE FROM notarised WHERE txid = '"+txid+"';")
        conn.commit()

        if row_data is not None:
            chain = row_data[0]
            block_height = row_data[1]
            block_time = row_data[2]
            txid = row_data[8]
            notaries = row_data[5]
            ntx_season = row_data[10]
            if not ntx_season:
                if chain not in ['KMD', 'BTC']:
                    for season_num in seasons_info:
                        if block_time < seasons_info[season_num]['end_time'] and block_time >= seasons_info[season_num]['start_time']:
                            ntx_season = season_num
                else:
                    for season_num in seasons_info:
                        if block_height < seasons_info[season_num]['end_block'] and block_height >= seasons_info[season_num]['start_block']:
                            ntx_season = season_num
            print(ntx_season+" | "+chain+" | "+str(block_height)+" | "+str(notaries)+" | ")            # update last ntx or last btc if newer than in tables.
            for notary in notaries:
                last_ntx_row_data = (notary, chain, txid, block_height,
                                     block_time, ntx_season)
            
                if notary in notary_last_ntx:
                    if chain not in notary_last_ntx[notary]:
                        notary_last_ntx[notary].update({chain:0})
                    if block_height > notary_last_ntx[notary][chain]:
                        update_last_ntx_tbl(conn, cursor, last_ntx_row_data)
                else:
                    update_last_ntx_tbl(conn, cursor, last_ntx_row_data)
                if chain == 'KMD':
                    last_btc_ntx_row_data = (notary, txid, block_height,
                                         block_time, ntx_season)

                    if notary in notary_last_btc_ntx:
                        if block_height > notary_last_btc_ntx[notary]:
                            update_last_btc_ntx_tbl(conn, cursor, last_btc_ntx_row_data)
                    else:
                        update_last_btc_ntx_tbl(conn, cursor, last_btc_ntx_row_data)
            
            sql = "INSERT INTO notarised (chain, block_height, block_time, block_datetime, block_hash, \
                                          notaries, ac_ntx_blockhash, ac_ntx_height, txid, opret, season) \
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            cursor.execute(sql, row_data)
            conn.commit()

    logger.info("Notarised blocks updated!")
    logger.info("NTX Address transactions processed: "+str(len(all_txids)))
    logger.info(str(len(all_txids))+" notarised TXIDs added to table")

update_notarisations()

cursor.close()

conn.close()
