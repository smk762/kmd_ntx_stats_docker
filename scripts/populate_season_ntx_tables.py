#!/usr/bin/env python3
import os
import sys
import json
import binascii
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
from electrum_lib import get_ac_block_info
from notary_lib import *


'''
This script scans the blockchain for notarisation txids that are not already recorded in the database.
After updaing the "notarised" table, aggregations are performed to get counts for notaries and chains within each season.
It is intended to be run as a cronjob every 15-30 min
Script runtime is around 5-10 mins sepending on number of seasons to aggregate
'''

# set this to false when originally populating the table, or rescanning
skip_past_seasons = True

load_dotenv()

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

conn = connect_db()
cursor = conn.cursor()

def update_season_notarised_counts(season):
    ac_block_heights = get_ac_block_info()
    chain_season_ntx_result = get_chain_ntx_season_aggregates(cursor, season)
    total_chain_season_ntx = {}
    for item in chain_season_ntx_result:
        chain = item[0]
        count = item[3]
        total_chain_season_ntx.update({
            chain:count
        })
    notary_season_counts = {}
    logger.info("Getting "+season+" notary notarisations")
    results = get_ntx_for_season(cursor, season)
    for item in results:
        chain = item[0]
        notaries = item[1]
        for notary in notaries:
            if notary not in notary_season_counts:
                notary_season_counts.update({notary:{}})
            if chain not in notary_season_counts[notary]:
                notary_season_counts[notary].update({chain:1})
            else:
                val = notary_season_counts[notary][chain] + 1
                notary_season_counts[notary].update({chain:val})


    for notary in notary_season_counts:
        chain_ntx_counts = notary_season_counts[notary]
        btc_count = 0
        antara_count = 0
        third_party_count = 0
        other_count = 0
        total_ntx_count = 0

        notary_season_pct = {}
        for chain in chain_ntx_counts:
            if chain == "KMD":
                btc_count += chain_ntx_counts[chain]
                total_ntx_count += chain_ntx_counts[chain]
            elif chain in third_party_coins:
                third_party_count += chain_ntx_counts[chain]
                total_ntx_count += chain_ntx_counts[chain]
            elif chain in antara_coins:
                antara_count += chain_ntx_counts[chain]
                total_ntx_count += chain_ntx_counts[chain]
            else:
                other_count += chain_ntx_counts[chain]                
            pct = round(chain_ntx_counts[chain]/total_chain_season_ntx[chain]*100,3)
            notary_season_pct.update({chain:pct})
        time_stamp = time.time()
        row_data = (notary, btc_count, antara_count, \
                    third_party_count, other_count, \
                    total_ntx_count, json.dumps(chain_ntx_counts), \
                    json.dumps(notary_season_pct), time_stamp, season)
        update_season_notarised_count_tbl(conn, cursor, row_data)

    results = get_chain_ntx_season_aggregates(cursor, season)
    for item in results:
        chain = item[0]
        block_height = item[1]
        max_time = item[2]
        ntx_count = item[3]
        cols = 'block_hash, txid, block_time, opret, ac_ntx_blockhash, ac_ntx_height'
        conditions = "block_height="+str(block_height)+" AND chain='"+chain+"'"
        last_ntx_result = select_from_table(cursor, 'notarised', cols, conditions)[0]
        kmd_ntx_blockhash = last_ntx_result[0]
        kmd_ntx_txid = last_ntx_result[1]
        kmd_ntx_blocktime = last_ntx_result[2]
        opret = last_ntx_result[3]
        ac_ntx_blockhash = last_ntx_result[4]
        ac_ntx_height = last_ntx_result[5]
        if chain in ac_block_heights:
            ac_block_height = ac_block_heights[chain]['height']
            ntx_lag = ac_block_height - ac_ntx_height
        else:
            ac_block_height = 0
            ntx_lag = "-"
        row_data = (chain, ntx_count, block_height, kmd_ntx_blockhash,\
                    kmd_ntx_txid, kmd_ntx_blocktime, opret, ac_ntx_blockhash, \
                    ac_ntx_height, ac_block_height, ntx_lag, season)

        update_season_notarised_chain_tbl(conn, cursor, row_data)
        
if skip_past_seasons:
    season = get_season(int(time.time()))
    update_season_notarised_counts(season)
else:
    for season in seasons_info:
        # Some S1 OP_RETURNS are decoding incorrectly, so skip.
        if season != "Season_1":
            logger.info("Processing notarisations for "+season)
            update_season_notarised_counts(season)

cursor.close()

conn.close()