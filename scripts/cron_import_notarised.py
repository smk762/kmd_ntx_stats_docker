#!/usr/bin/env python3
import json
import time
import random
import logging
import logging.handlers
import requests
from lib_const import NOTARY_BTC_ADDRESSES, OTHER_SERVER
from lib_notary import *
from models import notarised_row, get_chain_epoch_score_at, get_chain_epoch_at
from lib_const import *
from lib_api import get_btc_tx_info
from lib_table_select import get_existing_notarised_txids, get_notarised_chains, get_notarised_seasons

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

seasons = get_notarised_seasons()

for season in seasons:
    if season not in ["Season_1", "Season_2", "Season_3", "Unofficial"]: 
        chains = get_notarised_chains(season)

        i = 0
        while len(chains) > 0:
            chain = random.choice(chains)

            i += 1
            logger.info(f">>> Importing {chain} for {season} ({i} processed, {len(chains)} remaining )")

            existing_notarised_txids = get_existing_notarised_txids(chain, season)
            logger.info(f"existing_notarised_txids: {len(existing_notarised_txids)}")

            import_txids_url = f"{OTHER_SERVER}/api/info/chain_notarisation_txid_list?chain={chain}&season={season}"
            import_txids = requests.get(import_txids_url).json()["notarisation_txid_list"]
            logger.info(f"import_txids: {len(import_txids)}")

            
            new_txids = list(set(import_txids)-set(existing_notarised_txids))
            logger.info(f"new_txids: {len(new_txids)}")

            logger.info(f"Processing ETA: {0.03*len(new_txids)} sec")
            time.sleep(0.02)
            
            j = 0
            for txid in new_txids:
                j += 1
                logger.info(f">>> Importing {txid} {j}/{len(new_txids)}")
                txid_url = f"{OTHER_SERVER}/api/info/notarisation_txid?txid={txid}"
                time.sleep(0.02)
                r = requests.get(txid_url)
                try:
                    txid_info = r.json()
                    ntx_row = notarised_row()
                    ntx_row.chain = txid_info["chain"]
                    ntx_row.block_height = txid_info["block_height"]
                    ntx_row.block_time = txid_info["block_time"]
                    ntx_row.block_datetime = txid_info["block_datetime"]
                    ntx_row.block_hash = txid_info["block_hash"]
                    ntx_row.notaries = txid_info["notaries"]
                    ntx_row.ac_ntx_blockhash = txid_info["ac_ntx_blockhash"]
                    ntx_row.ac_ntx_height = txid_info["ac_ntx_height"]
                    ntx_row.txid = txid_info["txid"]
                    ntx_row.opret = txid_info["opret"]
                    ntx_row.epoch = txid_info["epoch"]
                    ntx_row.btc_validated = txid_info["btc_validated"]

                    if len(txid_info["notary_addresses"]) == 0:

                        if ntx_row.chain == "BTC":
                            url = f"{THIS_SERVER}/api/info/nn_btc_txid?txid={txid}"
                            local_info = requests.get(url).json()["results"][0]
                            local_addresses = []
                            for item in local_info:
                                if item["input_index"] != -1:
                                    local_addresses.append(item["address"])
                            ntx_row.notary_addresses = local_addresses
                            ntx_row.season, ntx_row.server = get_season_from_addresses(ntx_row.notary_addresses, ntx_row.block_time, "BTC", "BTC", txid, ntx_row.notaries)

                        elif ntx_row.chain == "LTC":
                            url = f"{THIS_SERVER}/api/info/nn_ltc_txid?txid={txid}"
                            local_info = requests.get(url).json()["results"][0]
                            local_addresses = []
                            for item in local_info:
                                if item["input_index"] != -1:
                                    local_addresses.append(item["address"])
                            ntx_row.notary_addresses = local_addresses
                            ntx_row.season, ntx_row.server = get_season_from_addresses(ntx_row.notary_addresses, ntx_row.block_time, "LTC", "LTC", txid, ntx_row.notaries)

                        else:
                            row_data = get_notarised_data(txid)
                            ntx_row.notary_addresses = row_data[6]
                            ntx_row.season = row_data[11]
                            ntx_row.server = row_data[12]                
                            ntx_row.season, ntx_row.server = get_season_from_addresses(ntx_row.notary_addresses, ntx_row.block_time)
                            
                    else:
                        ntx_row.notary_addresses = txid_info["notary_addresses"]
                        ntx_row.season = txid_info["season"]
                        ntx_row.server = txid_info["server"]

                    if ntx_row.chain == "GLEEC":
                        ntx_row.server = get_gleec_ntx_server(ntx_row.txid)

                    ntx_row.score_value = get_chain_epoch_score_at(ntx_row.season, ntx_row.server, ntx_row.chain, int(ntx_row.block_time))
                    ntx_row.epoch = get_chain_epoch_at(ntx_row.season, ntx_row.server, ntx_row.chain, int(ntx_row.block_time))
                    if ntx_row.score_value > 0:
                        ntx_row.scored = True
                    else:
                        ntx_row.scored = False
                    ntx_row.btc_validated = "N/A"

                    ntx_row.update()
                except Exception as e:
                    logger.error(e)
                    logger.error(f"Something wrong with API? {txid_url}")

            chains.remove(chain)

CURSOR.close()
CONN.close()

'''
                runtime = int(time.time()-start)
                pct = round(i/num_unrecorded_KMD_txids*100,3)
                est_end = int(100/pct*runtime)
                if ntx_row.season == "Season_5_Testnet":
                    logger.info(f"{ntx_row.season} NTX {ntx_row.notaries}")
                logger.info(str(pct)+"% :"+str(i)+"/"+str(num_unrecorded_KMD_txids)+
                         " records added to db ["+str(runtime)+"/"+str(est_end)+" sec]")
'''