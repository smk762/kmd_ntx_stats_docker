#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
import logging.handlers
import psycopg2
import requests
from dotenv import load_dotenv
from lib_const import *
from lib_notary import *

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

load_dotenv()
other_server = os.getenv("other_server")
this_server = os.getenv("this_server")

conn = connect_db()
cursor = conn.cursor()

for notary in NOTARIES["Season_4"]:
    url = f"{other_server}/api/info/nn_btc_txid_list?notary={notary}"
    r = requests.get(url)
    try:
        resp = r.json()
        txid_list = resp["results"][0]
        for txid in txid_list:
            txid_del = tx_row()
            txid_del.txid = txid
            txid_del.delete()

            txid_url = f"{other_server}/api/info/nn_btc_txid?txid={txid}"
            r = requests.get(txid_url)
            try:
                resp = r.json()
                tx_resp = resp["results"][0]
                for row in tx_resp:
                    txid_data = tx_row()
                    txid_data.txid = txid
                    txid_data.block_hash = row["block_hash"]
                    txid_data.block_height = row["block_height"]
                    txid_data.block_time = row["block_time"]
                    txid_data.block_datetime = row["block_datetime"]
                    txid_data.address = row["address"]
                    txid_data.notary = row["notary"]
                    txid_data.category = row["category"]
                    txid_data.season = row["season"]
                    txid_data.input_index = row["input_index"]
                    txid_data.input_sats = row["input_sats"]
                    txid_data.output_index = row["output_index"]
                    txid_data.output_sats = row["output_sats"]
                    txid_data.fees = row["fees"]
                    txid_data.num_inputs = row["num_inputs"]
                    txid_data.num_outputs = row["num_outputs"]
                    txid_data.update()
            except:
                logger.error(f"Something wrong with API? {txid_url}")
    except:
        logger.error(f"Something wrong with API? {url}")


cursor.close()
conn.close()