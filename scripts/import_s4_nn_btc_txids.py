#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
import logging.handlers
import psycopg2
import requests
import threading
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

# set this to False in .env when originally populating the table, or rescanning
skip_past_seasons = (os.getenv("skip_past_seasons") == 'True')

# set this to True in .env to quickly update tables with most recent data
skip_until_yesterday = (os.getenv("skip_until_yesterday") == 'True')

conn = connect_db()
cursor = conn.cursor()

#other_server = "http://116.203.120.91:8762"
other_server = "http://stats.kmd.io"

addresses_dict = {}
try:
    addresses = requests.get(f"{other_server}/api/source/addresses/?chain=BTC&season=Season_4").json()
    for item in addresses['results']:
        print(item)
        addresses_dict.update({item["address"]:item["notary"]})
    addresses_dict.update({BTC_NTX_ADDR:"BTC_NTX_ADDR"})
except Exception as e:
    logger.error(e)
    logger.info("Addresses API might be down!")

notary_btc_addresses = addresses_dict.keys()
i = 1
num_addr = len(notary_btc_addresses)
print(num_addr)


try:
    existing_txids = get_existing_nn_btc_txids(cursor)
    logger.info("Getting txids stored n other server")
    r = requests.get(f"{other_server}/api/info/nn_btc_txid_list")
    resp = r.json()
    txids = resp['results'][0]
    new_txids = []
    for txid in txids:
        if txid not in existing_txids:
            new_txids.append(txid)
    logger.info(str(len(new_txids))+" extra txids detected")
except Exception as e:
    print(e)
    new_txids = []
logger.info(str(len(new_txids))+" to process")

j = 1
for txid in new_txids:
    # Get data from other server

    r = requests.get(f"{other_server}/api/info/nn_btc_txid?txid={txid}")
    resp = r.json()
    if resp['count'] > 0:
        for item in resp['results'][0]:
            if item["output_index"] is None:
                output_index = 1000
            else:
                output_index = item["output_index"]
            if item["input_index"] is None:
                input_index = 1000
            else:
                input_index = item["input_index"]
            row_data = (
                item["txid"],
                item["block_hash"],
                item["block_height"],
                item["block_time"],
                item["block_datetime"],
                item["address"],
                item["notary"],
                item["season"],
                item["category"],
                input_index,
                item["input_sats"],
                output_index,
                item["output_sats"],
                item["fees"],
                item["num_inputs"],
                item["num_outputs"]
            )
            logger.info(f"Adding {item['txid']} from other server")
            update_nn_btc_tx_row(conn, cursor, row_data)
    j += 1
i += 1

cursor.close()
conn.close()

