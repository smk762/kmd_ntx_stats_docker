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
import table_lib
from decimal import *
from datetime import datetime as dt
import datetime
from dotenv import load_dotenv
from rpclib import def_credentials
from psycopg2.extras import execute_values
from electrum_lib import get_ac_block_info
from notary_lib import notary_info, seasons_info, known_addresses
from coins_lib import third_party_coins, antara_coins, ex_antara_coins, all_antara_coins, all_coins

'''
This script scans the blockchain for notarisation txids that are not already recorded in the database.
After updaing the "notarised" table, aggregations are performed to get counts for notaries and chains within each season.
It is intended to be run as a cronjob every 15-30 min
Script runtime is around 5-10 mins sepending on number of seasons to aggregate
'''

# set this to false when originally populating the table, or rescanning
skip_past_seasons = True
# set this to True to quickly update tables with most recent data
skip_until_yesterday = True

load_dotenv()

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

conn = table_lib.connect_db()
cursor = conn.cursor()

def update_daily_notarised_counts(season):
    # start on date of most recent season
    season_start_time = seasons_info[season]["start_time"]
    season_start_dt = dt.fromtimestamp(season_start_time)

    season_end_time = seasons_info[season]["end_time"]
    season_end_dt = dt.fromtimestamp(season_end_time)

    logger.info(season + " start: " + str(season_start_dt))
    logger.info(season + " end: " + str(season_end_dt))

    start = season_start_dt.date()
    end = datetime.date.today()
    if skip_until_yesterday:
        logger.info("Starting "+season+" scan from 24hrs ago...")
        start = end - datetime.timedelta(days=1)
    delta = datetime.timedelta(days=1)
    day = start
    while day <= end:
        if day >= season_start_dt.date() and day <= season_end_dt.date():
            logger.info("Getting daily "+season+" notary notarisations via get_ntx_for_day for "+str(day))
            results = table_lib.get_ntx_for_day(cursor, day)
            # Get list of chain/notary list dicts :p
            results_list = []
            time_stamp = int(time.time())
            for item in results:
                results_list.append({
                        "chain":item[0],
                        "notaries":item[1]
                    })
            # iterate over notaries list for each record and add to count for chain foreach notary
            notary_ntx_counts = {}
            logger.info("Aggregating "+str(len(results_list))+" rows from notarised table for "+str(day))
            for item in results_list:
                notaries = item['notaries']
                chain = item['chain']
                for notary in notaries:
                    if notary not in notary_ntx_counts:
                        notary_ntx_counts.update({notary:{}})
                    if chain not in notary_ntx_counts[notary]:
                        notary_ntx_counts[notary].update({chain:1})
                    else:
                        count = notary_ntx_counts[notary][chain]+1
                        notary_ntx_counts[notary].update({chain:count})

            # iterate over notary chain counts to calculate scoring category counts.
            node_counts = {}
            other_coins = []
            notary_ntx_pct = {}
            for notary in notary_ntx_counts:
                notary_ntx_pct.update({notary:{}})
                node_counts.update({notary:{
                        "btc_count":0,
                        "antara_count":0,
                        "third_party_count":0,
                        "other_count":0,
                        "total_ntx_count":0
                    }})
                for chain in notary_ntx_counts[notary]:
                    if chain == "KMD":
                        count = node_counts[notary]["btc_count"]+notary_ntx_counts[notary][chain]
                        node_counts[notary].update({"btc_count":count})
                    elif chain in all_antara_coins:
                        count = node_counts[notary]["antara_count"]+notary_ntx_counts[notary][chain]
                        node_counts[notary].update({"antara_count":count})
                    elif chain in third_party_coins:
                        count = node_counts[notary]["third_party_count"]+notary_ntx_counts[notary][chain]
                        node_counts[notary].update({"third_party_count":count})
                    else:
                        count = node_counts[notary]["other_count"]+notary_ntx_counts[notary][chain]
                        node_counts[notary].update({"other_count":count})
                        other_coins.append(chain)

                    count = node_counts[notary]["total_ntx_count"]+notary_ntx_counts[notary][chain]
                    node_counts[notary].update({"total_ntx_count":count})

            # get daily ntx total for each chain
            chain_totals = {}
            chains_aggr_resp = table_lib.get_chain_ntx_date_aggregates(cursor, day)
            for item in chains_aggr_resp:
                chain = item[0]
                max_block = item[1]
                max_blocktime = item[2]
                ntx_count = item[3]
                chain_totals.update({chain:ntx_count})
            logger.info("chain_totals: "+str(chain_totals))
            # calculate notary ntx percentage for chains and add row to db table.
            for notary in node_counts:
                for chain in notary_ntx_counts[notary]:
                    logger.info(notary+" count for "+chain+": "+str(notary_ntx_counts[notary][chain]))
                    logger.info("Total count for "+chain+": "+str(chain_totals[chain]))
                    pct = round(notary_ntx_counts[notary][chain]/chain_totals[chain]*100,2)
                    logger.info("Pct: "+str(pct))
                    notary_ntx_pct[notary].update({chain:pct})
                row_data = (notary, node_counts[notary]['btc_count'], node_counts[notary]['antara_count'], 
                            node_counts[notary]['third_party_count'], node_counts[notary]['other_count'], 
                            node_counts[notary]['total_ntx_count'], json.dumps(notary_ntx_counts[notary]),
                            json.dumps(notary_ntx_pct[notary]), time_stamp, season, day)
                logger.info("Adding counts for "+season+" "+notary+" for "+str(day)+" to notarised_count_daily table")
                table_lib.update_daily_notarised_count_tbl(conn, cursor, row_data)
        else:
            logger.info("Skipping "+str(day)+", ouside "+season+" range of "+str(season_start_dt)+" to "+str(season_end_dt))
        day += delta
    logger.info("Notarised blocks daily aggregation for "+season+" notaries finished...")

for season in seasons_info:
    # Some S1 OP_RETURNS are decoding incorrectly, so skip.
    if season != "Season_1":
        logger.info("Processing notarisations for "+season)
        update_daily_notarised_counts(season)

cursor.close()

conn.close()