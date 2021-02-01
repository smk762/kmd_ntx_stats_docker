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
from notary_lib import get_addresses_dict, get_nn_btc_tx_parts, connect_db
from lib_table_update import update_nn_btc_tx_row
from lib_table_select import get_existing_nn_btc_txids

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

load_dotenv()

conn = connect_db()
cursor = conn.cursor()

addresses_dict = get_addresses_dict()
notary_btc_addresses = list(addresses_dict.keys())

txids = get_existing_nn_btc_txids(cursor, None, "Sent")

for txid in txids:
    time.sleep(0.1)
    tx_vins, tx_vouts = get_nn_btc_tx_parts(txid)

    # Detect top up vins
    replenish_vins = False
    for vin in tx_vins:
        if vin["category"] == "Sent" and vin["notary"] in ["dragonhound_NA", "Replenish_Address"]:
            replenish_vins = True

    if replenish_vins:
        logger.info(f"")
        logger.info(f">>> Replenish txid detected: {txid}")
        for vin in tx_vins:
            if vin["notary"] != "dragonhound_NA":
                notary = "Replenish_Address"
            else:
                notary = "dragonhound_NA"
            category = "Top up sent"
            row_data = (
                vin["txid"],
                vin["block_hash"],
                vin["block_height"],
                vin["block_time"],
                vin["block_datetime"],
                vin["address"],
                notary,
                vin["season"],
                category,
                vin["input_index"],
                vin["input_sats"],
                vin["output_index"],
                vin["output_sats"],
                vin["fees"],
                vin["num_inputs"],
                vin["num_outputs"]
            )
            logger.info(f"Updating {notary} | {vin['address']} | {category}")
            update_nn_btc_tx_row(conn, cursor, row_data)

        for vout in tx_vouts:
            if vout["category"] == "Received":
                if vout["notary"] == "non-NN":
                    notary = "Replenish_Address"
                    category = "Replenish vout change"
                    row_data = (
                        vout["txid"],
                        vout["block_hash"],
                        vout["block_height"],
                        vout["block_time"],
                        vout["block_datetime"],
                        vout["address"],
                        notary,
                        vout["season"],
                        category,
                        vout["input_index"],
                        vout["input_sats"],
                        vout["output_index"],
                        vout["output_sats"],
                        vout["fees"],
                        vout["num_inputs"],
                        vout["num_outputs"]
                    )
                else:
                    notary = vout["notary"]
                    category = "Top up received"
                    row_data = (
                        vout["txid"],
                        vout["block_hash"],
                        vout["block_height"],
                        vout["block_time"],
                        vout["block_datetime"],
                        vout["address"],
                        notary,
                        vout["season"],
                        category,
                        vout["input_index"],
                        vout["input_sats"],
                        vout["output_index"],
                        vout["output_sats"],
                        vout["fees"],
                        vout["num_inputs"],
                        vout["num_outputs"]
                    )
                logger.info(f"Updating {notary} | {vout['address']} | {category}")
                update_nn_btc_tx_row(conn, cursor, row_data)
