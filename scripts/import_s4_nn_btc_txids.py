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

def import_nn_btc_txids(existing_txids):
    r = requests.get("http://notary.earth:8762/api/source/nn_btc_txids/?season=Season_4")
    # r = requests.get("http://stats.kmd.io/api/source/nn_btc_txids/?season=Season_4")
    resp = r.json()
    while resp["next"] is not None:

        results = resp["results"]
        next_page = resp["next"]
        for item in results:
            if item["txid"] not in existing_txids:
                row_data = ()

                update_nn_btc_tx_row(conn, cursor, row_data)
                time.sleep(0.1)
                logger.info("Updated "+item['txid'])
            else:
                logger.info("Skipping "+item['txid'])

        r = requests.get(resp["next"])
        resp = r.json()

    results = resp["results"]
    for item in results:
        if item["txid"] not in existing_txids:
            row_data = ()

            update_nn_btc_tx_row(conn, cursor, row_data)
            time.sleep(0.1)
            logger.info("Updated "+item['txid'])
        else:
            logger.info("Skipping "+item['txid'])

conn = connect_db()
cursor = conn.cursor()

existing_txids = get_existing_nn_btc_txids(cursor)

import_nn_btc_txids(existing_txids)

cursor.close()
conn.close()
