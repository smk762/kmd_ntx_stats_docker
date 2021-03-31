#!/usr/bin/env python3
import json
import time
import logging
import logging.handlers
import requests
from lib_const import NOTARY_LTC_ADDRESSES, OTHER_SERVER
from lib_notary import get_new_notary_txids
from models import ltc_tx_row
from lib_const import *

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

seasons = get_notarised_seasons()

for season in seasons:
    if season not in ["Season_1", "Season_2", "Season_3"]: 

        i = 0
        num_addr = len(NOTARY_LTC_ADDRESSES[season])
        for notary_address in NOTARY_LTC_ADDRESSES[season]:
            i += 1
            logger.info(f">>> Categorising {notary_address} for {season} {i}/{num_addr}")
            txid_list = get_new_notary_txids(notary_address, "LTC")
            logger.info(f"Processing ETA: {0.02*len(txid_list)} sec")

            j = 0
            num_txid = len(txid_list)
            for txid in txid_list:
                j += 1
                logger.info(f">>> Categorising {txid} for {j}/{num_txid}")
                txid_url = f"{OTHER_SERVER}/api/info/nn_ltc_txid?txid={txid}"
                time.sleep(0.02)
                r = requests.get(txid_url)
                try:
                    resp = r.json()
                    tx_resp = resp["results"][0]
                    for row in tx_resp:
                        txid_data = ltc_tx_row()
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
                        txid_data.insert()
                except:
                    logger.error(f"Something wrong with API? {txid_url}")

CURSOR.close()
CONN.close()