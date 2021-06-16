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
from lib_helper import get_chain_server, get_season_notaries
from lib_table_select import *
from models import  last_notarised_row


def update_latest_ntx(season):

    chains = get_notarised_chains(season)
    season_last_ntx = get_season_last_ntx(season)
    notaries = get_season_notaries(season)
    for chain in chains:
        server = get_chain_server(chain, season)

        logger.info(f"[update_latest_ntx] {chain}")
        for notary in notaries:
            if notary not in season_last_ntx:
                season_last_ntx.update({
                    notary:{}
                })
            if chain not in season_last_ntx[notary]:
                season_last_ntx[notary].update({chain:0})

            sql = "SELECT MAX(block_height) \
                   FROM notarised \
                   WHERE season = '"+str(season)+"' \
                   AND chain = '"+str(chain)+"' \
                   AND notaries @> "+"'{\""+notary+"\"}'";

            try:
                #logger.info(f"[update_latest_ntx] {sql}")
                CURSOR.execute(sql)
                resp = CURSOR.fetchone()
                block_height = resp[0]
                if block_height:
                    if block_height > season_last_ntx[notary][chain]:
                        sql = "SELECT block_time, txid \
                               FROM notarised \
                               WHERE chain='"+str(chain)+"' \
                               AND block_height="+str(block_height)+";"

                        try:
                            logger.info(f"[update_latest_ntx] {sql}")
                            CURSOR.execute(sql)
                            x = CURSOR.fetchone()
                            block_time = x[0]
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

    for season in SEASONS_INFO:
        if season not in EXCLUDED_SEASONS:
            start = time.time()
            update_latest_ntx(season)
            end = time.time()
            logger.info(f">>> {end-start} sec to complete [update_latest_ntx({season})]")
    CURSOR.close()
    CONN.close()



