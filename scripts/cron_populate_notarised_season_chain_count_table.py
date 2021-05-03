#!/usr/bin/env python3
import os
import sys
import json
import random
import psycopg2
import threading
from decimal import *
from datetime import datetime as dt
import datetime
import dateutil.parser as dp
from lib_electrum import get_ac_block_info
from lib_const import *
from lib_notary import *
from lib_table_update import *
from lib_table_select import *
from lib_api import *
from lib_helper import *
from models import *


def update_notarised_chain_season(season):
    logger.info("Getting "+season+" season_notarised_counts")
    ac_block_heights = get_ac_block_info()

    results = get_chain_ntx_season_aggregates(season)

    for item in results:
        chain = item[0]
        block_height = item[1]
        max_time = item[2]
        ntx_count = item[3]
        cols = 'block_hash, txid, block_time, opret, ac_ntx_blockhash, ac_ntx_height'
        conditions = "block_height="+str(block_height)+" AND chain='"+chain+"'"
        try:
            last_ntx_result = select_from_table('notarised', cols, conditions)[0]
            kmd_ntx_blockhash = last_ntx_result[0]
            kmd_ntx_txid = last_ntx_result[1]
            kmd_ntx_blocktime = last_ntx_result[2]
            opret = last_ntx_result[3]
            ac_ntx_blockhash = last_ntx_result[4]
            ac_ntx_height = last_ntx_result[5]

            if chain in ac_block_heights:
                ac_block_height = ac_block_heights[chain]['height']
                ntx_lag = ac_block_height - ac_ntx_height
            else:
                ac_block_height = 0
                ntx_lag = "-"

            if run_updates():
                row = notarised_chain_season_row()
                row.chain = chain
                row.ntx_count = ntx_count
                row.block_height = block_height
                row.kmd_ntx_blockhash = kmd_ntx_blockhash
                row.kmd_ntx_txid = kmd_ntx_txid
                row.kmd_ntx_blocktime = kmd_ntx_blocktime
                row.opret = opret
                row.ac_ntx_blockhash = ac_ntx_blockhash
                row.ac_ntx_height = ac_ntx_height
                row.ac_block_height = ac_block_height
                row.ntx_lag = ntx_lag
                row.season = season
                row.server = server
                row.update()
        except Exception as e:
            logger.error(f"Exception in [update_season_notarised_counts] : {e}")



    logger.info(f"{season} season_notarised_counts complete")




def run_updates():
    return __name__ == "__main__"

if __name__ == "__main__":

    # Uncomment if record contains address rather than notary in [notaries] list (e.g. saved before pubkeys updated)
    # rescan_notaries(SEASON)

    start = time.time()
    seasons = get_notarised_seasons()
    end = time.time()
    logger.info(f">>> {end-start} sec to complete [get_notarised_seasons]")

    logger.info(f"Preparing to populate NTX tables...")

    for season in seasons:
        if season in ["Season_1", "Season_2", "Season_3", "Unofficial", "Season_5_Testnet"]:
            logger.warning(f"Skipping season: {season}")
        else:

            start = end
            update_notarised_chain_season(season)
            end = time.time()
            logger.info(f">>> {end-start} sec to complete [update_notarised_chain_season({season})]")
            