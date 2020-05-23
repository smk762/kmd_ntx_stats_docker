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

class daily_chain_thread(threading.Thread):
    def __init__(self, cursor, season, day):
        threading.Thread.__init__(self)
        self.season = season
        self.cursor = cursor
        self.day = day
    def run(self):
        thread_chain_ntx_daily_aggregate(self.cursor, self.season, self.day)
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

def update_daily_notarised_chains(season):
    logger.info("Aggregating Notarised blocks for chains...")

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
            thread_list = []
            while day <= end:
                logger.info("Aggregating chain notarisations for "+str(day))
                thread_list.append(daily_chain_thread(cursor, season, day))
                day += delta
            for thread in thread_list:
                time.sleep(10)
                thread.start()
            logger.info("Notarised blocks for daily chains aggregation complete!")
        else:
            logger.info("Skipping "+str(day)+", ouside "+season+" range of "+str(season_start_dt)+" to "+str(season_end_dt))
        day += delta
    logger.info("Notarised daily aggregation for "+season+" chains finished...")

def thread_chain_ntx_daily_aggregate(cursor, season, day):
    chains_aggr_resp = table_lib.get_chain_ntx_date_aggregates(cursor, day)
    for item in chains_aggr_resp:
        try:
            chain = item[0]
            max_block = item[1]
            max_blocktime = item[2]
            ntx_count = item[3]
            if ntx_count != 0:
                row_data = (chain, ntx_count, str(day))
                logger.info("Adding daily counts for "+chain+" on "+str(day)+" to notarised_chain table")
                table_lib.update_daily_notarised_chain_tbl(conn, cursor, row_data)
                logger.info("OK in thread_chain_ntx_daily_aggregate: "+str(item)+" on "+str(day))
        except Exception as e:
            logger.warning("Error in thread_chain_ntx_daily_aggregate: "+str(e))
            logger.warning("Error in thread_chain_ntx_daily_aggregate: "+str(item))
            logger.warning("Error in thread_chain_ntx_daily_aggregate: "+str(day))

for season in seasons_info:
    # Some S1 OP_RETURNS are decoding incorrectly, so skip.
    if season != "Season_1":
        logger.info("Processing notarisations for "+season)
        update_daily_notarised_chains(season)
