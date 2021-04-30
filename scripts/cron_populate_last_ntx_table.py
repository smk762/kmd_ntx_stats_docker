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
from lib_const import *
from lib_table_select import *
from models import  last_notarised_row


def update_latest_ntx(season, server, notary, chain):

    sql = "SELECT MAX(block_time) \
           FROM notarised WHERE \
           season = '"+str(season)+"' \
           AND server = '"+str(server)+"' \
           AND chain = '"+str(chain)+"' \
           AND notaries @> "+"'{\""+notary+"\"}'";

    try:
        CURSOR.execute(sql)
        resp = CURSOR.fetchone()
        print(f"[update_latest_ntx] {season} {server} {notary} {chain} Max block_time resp: {resp}")
        block_time = resp[0]
        if block_time:
            sql = "SELECT block_height, txid \
                   FROM notarised WHERE season='"+season+"' AND server='"+server+"' AND \
                   chain='"+str(chain)+"' AND block_time="+str(block_time)+";"

            try:

                CURSOR.execute(sql)
                x = CURSOR.fetchone()
                block_height = x[0]
                txid = x[1]
                row = last_notarised_row()
                row.notary = notary
                row.chain = chain
                row.txid = txid
                row.block_height = block_height
                row.block_time = block_time
                row.season = season
                row.server = server
                row.update()

            except Exception as e:
                logger.error(f"Exception in [update_latest_ntx] where block_time: {e}")
        else:
            row = last_notarised_row()
            row.notary = notary
            row.chain = chain
            row.txid = "N/A"
            row.block_height = 0
            row.block_time = 0
            row.season = season
            row.server = server
            row.update()



    except Exception as e:
        logger.error(f"Exception in [update_latest_ntx] max block_time: {e}")


if __name__ == "__main__":

    # Uncomment if record contains address rather than notary in [notaries] list (e.g. saved before pubkeys updated)
    # rescan_notaries(SEASON)

    TIP = int(RPC["KMD"].getblockcount())

    seasons = get_notarised_seasons()
    logger.info(f"Preparing to populate NTX tables...")

    for season in seasons:
        start = time.time()
        if season in ["Season_1", "Season_2", "Season_3", "Unofficial", "Season_5_Testnet"]:
            logger.warning(f"Skipping season: {season}")
        else:
            season_servers = get_notarised_servers(season)
            for server in season_servers:
                season_server_chains = get_notarised_chains(season, server)
                for chain in season_server_chains:
                    for notary in NOTARY_PUBKEYS[season]:
                        update_latest_ntx(season, server, notary, chain)
                        #update_latest_ltc_ntx(season, notary)
                        #update_latest_btc_ntx(season, notary)
            end = time.time()
            logger.info(f">>> {end-start} sec to complete [update_latest_ntx({season})]")



