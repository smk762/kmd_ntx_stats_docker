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

def update_season_notarised_counts(season):
    logger.info("Getting "+season+" notary notarisations")
    results = table_lib.get_chain_ntx_season_aggregates(cursor, season)
    print(results)

for season in seasons_info:
    # Some S1 OP_RETURNS are decoding incorrectly, so skip.
    if season != "Season_1":
        logger.info("Processing notarisations for "+season)
        update_season_notarised_counts(season)

cursor.close()

conn.close()