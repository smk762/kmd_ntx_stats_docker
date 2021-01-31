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

other_server = os.getenv("other_server")

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

notary_btc_addresses = list(addresses_dict.keys())
i = 1
num_addr = len(notary_btc_addresses)
print(num_addr)
notary_btc_addresses.append("non-NN")
for notary_address in notary_btc_addresses:
    try:
        existing_txids = get_existing_nn_btc_txids(cursor, notary_address)
        logger.info(f"{len(existing_txids)} existing txids in local DB detected for {notary_address}")
        logger.info(f"Getting txids stored on other server for {addresses_dict[notary_address]}")
        url = f"{other_server}/api/info/nn_btc_txid_list?notary={addresses_dict[notary_address]}"
        logger.info(url)
        r = requests.get(url)
        resp = r.json()
        txids = resp['results'][0]
        new_txids = []
        for txid in txids:
            if txid not in existing_txids:
                new_txids.append(txid)
        new_txids = list(set(new_txids))
        logger.info(f"{len(new_txids)} extra txids detected for {addresses_dict[notary_address]} on other server")
    except Exception as e:
        print(e)
        new_txids = []
    logger.info(str(len(new_txids))+" to process")

    j = 1
    for txid in new_txids:
        # Get data from other server

        print(f"{other_server}/api/info/nn_btc_txid?txid={txid}")
        r = requests.get(f"{other_server}/api/info/nn_btc_txid?txid={txid}")
        try:
            resp = r.json()
            if resp['count'] > 0:
                tx_addresses = []
                season = None
                for item in resp['results'][0]:
                    if item["address"] != '1P3rU1Nk1pmc2BiWC8dEy9bZa1ZbMp5jfg':
                        tx_addresses.append(item["address"])
                tx_addresses = list(set(tx_addresses))
                season = get_season_from_addresses(tx_addresses, resp['results'][0][0]["block_time"], "BTC")
                logger.info(f"Detected {season} from addresses")
                for item in resp['results'][0]:
                    if item["output_index"] is None:
                        output_index = -1
                    else:
                        output_index = item["output_index"]

                    if item["input_index"] is None or item["input_index"] == 1000:
                        input_index = -1
                    else:
                        input_index = item["input_index"]

                    if item["input_sats"] is None:
                        input_sats = -1
                    else:
                        input_sats = item["input_sats"]

                    if item["output_sats"] is None or item["output_index"] == 1000:
                        output_sats = -1
                    else:
                        output_sats = item["output_sats"]

                    if item["num_inputs"] is None:
                        num_inputs = 0
                    else:
                        num_inputs = item["num_inputs"]

                    if item["num_outputs"] is None:
                        num_outputs = 0
                    else:
                        num_outputs = item["num_outputs"]

                    if item["address"] in addresses_dict:
                        notary = addresses_dict[item["address"]]
                    else:
                        notary = item["notary"]

                    row_data = (
                        item["txid"],
                        item["block_hash"],
                        item["block_height"],
                        item["block_time"],
                        item["block_datetime"],
                        item["address"],
                        notary,
                        season,
                        item["category"],
                        input_index,
                        input_sats,
                        output_index,
                        output_sats,
                        item["fees"],
                        num_inputs,
                        num_outputs
                    )
                    logger.info(f"Adding {item['txid']} {item['category']} from other server for {notary}")
                    update_nn_btc_tx_row(conn, cursor, row_data)
        except Exception as e:
            print(e)
            print(r.text)
        j += 1
    i += 1

cursor.close()
conn.close()