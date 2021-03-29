#!/usr/bin/env python3
import json
import time
import logging
import logging.handlers
import requests
from lib_const import NOTARY_BTC_ADDRESSES, OTHER_SERVER
from lib_notary import get_new_notary_txids
from models import tx_row
from lib_const import *

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# seasons = get_notarised_seasons()

season = "Season_4"
chains = get_notarised_chains(season)
existing_notarised_txids = get_existing_notarised_txids()

i = 0
for chain in chains:

    i += 1
    logger.info(f">>> Categorising {chain} for {season} {i}/{len(chains)}")

    existing_notarised_txids = get_existing_notarised_txids(chain, season)

    txid_list_url = f"{OTHER_SERVER}/api/info/chain_notarisation_txid_list?chain={chain}&season={season}"
    txid_list = requests.get(txid_list_url).json()["notarisation_txid_list"]

    logger.info(f"Processing ETA: {0.03*len(txid_list)} sec")
    time.sleep(0.02)

    new_txids = list(set(existing_notarised_txids)-set(txid_list))

    j = 0
    for txid in new_txids:
        j += 1
        logger.info(f">>> Importing {txid} {j}/{len(num_txid)}")
        txid_url = f"{OTHER_SERVER}/api/info/notarisation_txid?txid={txid}"
        time.sleep(0.02)
        r = requests.get(txid_url)
        try:
            txid_info = r.json()
            tx_resp = resp["results"][0]
                row = notarised_row()
                row.chain = txid_info["chain"]
                row.block_height = txid_info["block_height"]
                row.block_time = txid_info["block_time"]
                row.block_datetime = txid_info["block_datetime"]
                row.block_hash = txid_info["block_hash"]
                row.notaries = txid_info["notaries"]
                row.notary_addresses = txid_info["notary_addresses"]
                row.ac_ntx_blockhash = txid_info["ac_ntx_blockhash"]
                row.ac_ntx_height = txid_info["ac_ntx_height"]
                row.txid = txid_info["txid"]
                row.opret = txid_info["opret"]
                row.season = txid_info["season"]
                row.server = txid_info["server"]
                row.score_value = txid_info["score_value"]
                row.scored = txid_info["scored"]
                row.btc_validated = txid_info["btc_validated"]
                row.update()
        except:
            logger.error(f"Something wrong with API? {txid_url}")

CURSOR.close()
CONN.close()

'''
                runtime = int(time.time()-start)
                pct = round(i/num_unrecorded_KMD_txids*100,3)
                est_end = int(100/pct*runtime)
                if row.season == "Season_5_Testnet":
                    logger.info(f"{row.season} NTX {row.notaries}")
                logger.info(str(pct)+"% :"+str(i)+"/"+str(num_unrecorded_KMD_txids)+
                         " records added to db ["+str(runtime)+"/"+str(est_end)+" sec]")
'''