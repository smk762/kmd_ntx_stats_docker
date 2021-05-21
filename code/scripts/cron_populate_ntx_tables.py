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
from models import notarised_row, notarised_count_season_row, notarised_chain_season_row, notarised_count_daily_row, notarised_chain_daily_row, get_chain_epoch_score_at, get_chain_epoch_at


'''
This script scans the blockchain for notarisation txids that are not already recorded in the database.
After updaing the "notarised" table, aggregations are performed to get counts for notaries and chains within each season.
It is intended to be run as a cronjob every 15-30 min
Script runtime is around 5-10 mins, except for initial population which is up to 1 day per season
'''

# Process KMD notarisation transactions from KMD OpReturns
def update_KMD_notarisations(unrecorded_KMD_txids):
    logger.info(f"Updating KMD {len(unrecorded_KMD_txids)} notarisations...")

    i = 0
    start = time.time()
    notary_last_ntx = get_notary_last_ntx()
    num_unrecorded_KMD_txids = len(unrecorded_KMD_txids)
    
    for txid in unrecorded_KMD_txids:
        row_data = get_notarised_data(txid)
        i += 1


        if row_data is not None: # ignore TXIDs that are not notarisations
            chain = row_data[0]

            ntx_row = notarised_row()
            ntx_row.chain = chain
            ntx_row.block_height = row_data[1]
            ntx_row.block_time = row_data[2]
            ntx_row.block_datetime = row_data[3]
            ntx_row.block_hash = row_data[4]
            ntx_row.notaries = row_data[5]
            ntx_row.notary_addresses = row_data[6]
            ntx_row.ac_ntx_blockhash = row_data[7]
            ntx_row.ac_ntx_height = row_data[8]
            ntx_row.txid = row_data[9]
            ntx_row.opret = row_data[10]
            ntx_row.season = row_data[11]
            ntx_row.score_value = get_chain_epoch_score_at(ntx_row.season, ntx_row.server, ntx_row.chain, int(ntx_row.block_time))
            ntx_row.epoch = get_chain_epoch_at(ntx_row.season, ntx_row.server, ntx_row.chain, int(ntx_row.block_time))
            if chain == "GLEEC":
                ntx_row.server = get_gleec_ntx_server(ntx_row.txid)
                if ntx_row.server == "Third_Party":
                    ntx_row.chain == "GLEEC-OLD"
            else:
                ntx_row.server = row_data[12]

            if ntx_row.score_value > 0:
                ntx_row.scored = True
            else:
                ntx_row.scored = False
            ntx_row.update()


            runtime = int(time.time()-start)
            try:
                pct = round(i/num_unrecorded_KMD_txids*100,3)
                est_end = int(100/pct*runtime)
                logger.info(str(pct)+"% :"+str(i)+"/"+str(num_unrecorded_KMD_txids)+
                         " records added to db ["+str(runtime)+"/"+str(est_end)+" sec]")
            except:
                pass


    logger.info("Notarised blocks updated!")


def scan_rpc_for_ntx(season):
    start_block = SEASONS_INFO[season]["start_block"]
    end_block = SEASONS_INFO[season]["end_block"]

    if SKIP_UNTIL_YESTERDAY:
        start_block = TIP - 24*60*2
        logger.info(f"Processing notarisations for {season}, blocks {start_block} - {end_block}")
        unrecorded_KMD_txids = get_unrecorded_KMD_txids(TIP, season)
        unrecorded_KMD_txids.sort()
        update_KMD_notarisations(unrecorded_KMD_txids)

    else:
        windows = []
        chunk_size = 50000

        for i in range(start_block, end_block, chunk_size):
            windows.append((i, i+chunk_size))

        if OTHER_SERVER.find("stats") == -1:
            windows.reverse()
        
        logger.info(f"Processing notarisations for {season}, blocks {start_block} - {end_block}")
        
        while len(windows) > 0:
            window = random.choice(windows)

            logger.info(f"Processing notarisations for blocks {window[0]} - {window[1]}")
            unrecorded_KMD_txids = get_unrecorded_KMD_txids(TIP, season, window[0], window[1])
            unrecorded_KMD_txids.sort()
            update_KMD_notarisations(unrecorded_KMD_txids)

            windows.remove(window)
            


def rescan_chain(season, chain):
    if chain in ["KMD", "BTC", "LTC"]:
        if chain in ["LTC", "BTC"]:
            score = False
            score_value = 0
        else:
            score = True
            score_value = 0.0325
        chain = chain
        season = season
        server = chain
        epoch = chain

        sql = f"UPDATE notarised SET score={score}, score_value={score_value}, \
                season='{season}', server='{server}', epoch='{epoch}'  \
                WHERE \
                chain = '{chain}' \
                AND block_time >= {SEASONS_INFO[season]['start_time']} \
                AND block_time <= {SEASONS_INFO[season]['end_time']};"
        try:
            CURSOR.execute(sql, row_data)
            CONN.commit()
        except Exception as e:
            logger.debug(e)
            logger.debug(sql)
            CONN.rollback()


def rescan_notaries(season):
    sql = f"SELECT chain, block_height, block_time, block_datetime, \
            block_hash, notaries, notary_addresses, ac_ntx_blockhash, \
            ac_ntx_height, txid, opret, season,\
            server, epoch, score_value, scored \
            FROM notarised \
            ORDER BY block_time asc"
    where = []
    if season:
        where.append(f"season = '{season}'")

    if len(where) > 0:
        sql += " WHERE "
        sql += " AND ".join(where)
    sql += ";"

    try:
        CURSOR.execute(sql)
        results = CURSOR.fetchall()
        for item in results:
            notary_addresses = item[6][:]
            notary_addresses.sort()
            notaries = item[5][:]
            notaries.sort()
            row = notarised_row()
            row.chain = item[0]
            row.block_height = item[1]
            row.block_time = item[2]
            row.block_datetime = item[3]
            row.block_hash = item[4]
            row.notaries = notaries
            row.notary_addresses = notary_addresses
            row.ac_ntx_blockhash = item[7]
            row.ac_ntx_height = item[8]
            row.txid = item[9]
            row.opret = item[10]
            row.season = item[11]
            row.server = item[12]
            row.epoch = item[13]
            row.score_value = item[14]
            row.scored = item[15]
            row.update()

    except Exception as e:
        logger.error(f"Exception in [rescan_notaries]: {e}")

def run_updates():
    return __name__ == "__main__"

if __name__ == "__main__":

    # Uncomment if record contains address rather than notary in [notaries] list (e.g. saved before pubkeys updated)
    # rescan_notaries(SEASON)

    for chain in ["LTC","BTC","KMD"]:
        sql = f"UPDATE notarised SET epoch = '{chain}', server = '{chain}' WHERE chain = '{chain}';"
        print(sql)
        CURSOR.execute(sql)
        CONN.commit()



    TIP = int(RPC["KMD"].getblockcount())

    seasons = get_notarised_seasons()
    logger.info(f"Preparing to populate NTX tables...")

    for season in seasons:
        if season in ["Season_1", "Season_2", "Season_3", "Unofficial", "Season_5_Testnet"]:
            logger.warning(f"Skipping season: {season}")
        else:
    
            if 'post_season_end_time' in SEASONS_INFO[season]:
                sql = f"UPDATE notarised SET epoch = 'Unofficial' WHERE season = '{season}' \
                        AND block_time >= {SEASONS_INFO[season]['end_time']} \
                        AND block_time <= {SEASONS_INFO[season]['post_season_end_time']};"
                print(sql)
                CURSOR.execute(sql)
                CONN.commit()

            start = time.time()
            scan_rpc_for_ntx(season)
            end = time.time()
            logger.info(f">>> {end-start} sec to complete [scan_rpc_for_ntx({season})]")
