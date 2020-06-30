#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
import logging.handlers
import psycopg2
import requests
from decimal import *
from datetime import datetime as dt
import datetime
import dateutil.parser as dp
from dotenv import load_dotenv
from rpclib import def_credentials
from electrum_lib import get_ac_block_info
from lib_const import *
from notary_lib import *
from lib_table_update import *
from lib_table_select import *
from lib_api import *

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

load_dotenv()

def import_btc_ntx(existing_txids):
    r = requests.get("http://notary.earth:8762/api/source/notarised/?season=Season_4&chain=BTC")
    resp = r.json()
    while resp["next"] is not None:

        results = resp["results"]
        next_page = resp["next"]
        for item in results:
            if item["txid"] not in existing_txids:
                row_data = (item["chain"], item["block_height"], item["block_time"],
                            item["block_datetime"], item["block_hash"],
                            item["notaries"], item["ac_ntx_blockhash"], item["ac_ntx_height"],
                            item["txid"], item["opret"], item["season"], "true")

                update_ntx_row(conn, cursor, row_data)
                time.sleep(0.1)
                logger.info("Updated "+item['txid'])
            else:
                logger.info("Skipping "+item['txid'])

        r = requests.get(resp["next"])
        resp = r.json()

    results = resp["results"]
    for item in results:
        if item["txid"] not in existing_txids:
            row_data = (item["chain"], item["block_height"], item["block_time"],
                        item["block_datetime"], item["block_hash"],
                        item["notaries"], item["ac_ntx_blockhash"], item["ac_ntx_height"],
                        item["txid"], item["opret"], item["season"], "true")

            update_ntx_row(conn, cursor, row_data)
            time.sleep(0.1)
            logger.info("Updated "+item['txid'])
        else:
            logger.info("Skipping "+item['txid'])

conn = connect_db()
cursor = conn.cursor()

existing_txids = get_exisiting_btc_ntxids(cursor)

import_btc_ntx(existing_txids)

cursor.close()
conn.close()
