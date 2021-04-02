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
from lib_electrum import get_ac_block_info
from lib_const import *
from lib_notary import *
from lib_table_update import *
from lib_table_select import *
from lib_api import *
from models import notarised_row, notarised_count_season_row, notarised_chain_season_row, notarised_count_daily_row, notarised_chain_daily_row, last_notarised_row

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

'''
This script scans the blockchain for notarisation txids that are not already recorded in the database.
After updaing the "notarised" table, aggregations are performed to get counts for notaries and chains within each season.
It is intended to be run as a cronjob every 15-30 min
Script runtime is around 5-10 mins, except for initial population which is up to 1 day per season
'''

# Threading function to get daily aggregates
class daily_chain_thread(threading.Thread):

    def __init__(self, season, day):
        threading.Thread.__init__(self)
        self.season = season
        self.day = day

    def run(self):
        thread_chain_ntx_daily_aggregate(self.season, self.day)

# Threaded update of daily aggregates for KMD notarisations for each chain
def thread_chain_ntx_daily_aggregate(season, day):

    chains_aggr_resp = get_chain_ntx_date_aggregates(day, season)
    for item in chains_aggr_resp:
        try:
            row = notarised_chain_daily_row()
            row.chain = item[0]
            row.ntx_count = item[3]
            row.notarised_date = str(day)
            row.update()

        except Exception as e:
            logger.warning("Error in thread_chain_ntx_daily_aggregate: "+str(e))
            logger.warning("Error in thread_chain_ntx_daily_aggregate: "+str(item))
            logger.warning("Error in thread_chain_ntx_daily_aggregate: "+str(day))

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

            if chain != 'KMD': # KMD -> BTC notarisations are requested via BTC blockchain APIs
                row = notarised_row()
                row.chain = chain
                row.block_height = row_data[1]
                row.block_time = row_data[2]
                row.block_datetime = row_data[3]
                row.block_hash = row_data[4]
                row.notaries = row_data[5]
                row.notary_addresses = row_data[6]
                row.ac_ntx_blockhash = row_data[7]
                row.ac_ntx_height = row_data[8]
                row.txid = row_data[9]
                row.opret = row_data[10]
                row.season = row_data[11]
                if chain == "GLEEC":
                    row.server = get_gleec_ntx_server(row.txid)
                else:
                    row.server = row_data[12]
                row.score_value = get_dpow_score_value(row.season, row.server, row.chain, row.block_time)
                if row.score_value > 0:
                    row.scored = True
                else:
                    row.scored = False
                
                row.btc_validated =  "N/A"
                row.update()

                runtime = int(time.time()-start)
                try:
                    pct = round(i/num_unrecorded_KMD_txids*100,3)
                    est_end = int(100/pct*runtime)
                    if row.season == "Season_5_Testnet":
                        logger.info(f"{row.season} NTX {row.notaries}")
                    logger.info(str(pct)+"% :"+str(i)+"/"+str(num_unrecorded_KMD_txids)+
                             " records added to db ["+str(runtime)+"/"+str(est_end)+" sec]")
                except:
                    pass

    logger.info("Notarised blocks updated!")

def update_daily_notarised_chains(season):

    season_start_dt = dt.fromtimestamp(SEASONS_INFO[season]["start_time"])
    season_end_dt = dt.fromtimestamp(SEASONS_INFO[season]["end_time"])

    logger.info("Aggregating Notarised blocks for chains...")
    logger.info(season + " start: " + str(season_start_dt))
    logger.info(season + " end: " + str(season_end_dt))

    # Define timespan
    day = season_start_dt.date()
    end = datetime.date.today()
    delta = datetime.timedelta(days=1)
    if SKIP_UNTIL_YESTERDAY:
        logger.info("Starting "+season+" scan from 24hrs ago...")
        day = end - delta
    else:
        logger.info("Starting "+season+" scan from start of "+season)
        day = season_start_dt.date()

    # calc daily aggregates for timespan
    while day <= end:
        thread_list = []
        while day <= end:
            logger.info("Aggregating chain notarisations for "+str(day))
            thread_list.append(daily_chain_thread(season, day))
            day += delta
        for thread in thread_list:
            time.sleep(5)
            thread.start()
        day += delta
    logger.info("Notarised daily aggregation for "+season+" chains finished...")

def update_daily_notarised_counts(season):

    # start on date of most recent season
    season_start_dt = dt.fromtimestamp(SEASONS_INFO[season]["start_time"])
    season_end_dt = dt.fromtimestamp(SEASONS_INFO[season]["end_time"])

    logger.info(season + " start: " + str(season_start_dt))
    logger.info(season + " end: " + str(season_end_dt))

    day = season_start_dt.date()
    end = datetime.date.today()
    delta = datetime.timedelta(days=1)

    if SKIP_UNTIL_YESTERDAY:
        logger.warning("Starting "+season+" scan from 24hrs ago...")
        day = end - delta
    else:
        logger.warning("Starting "+season+" scan from start of "+season)
        day = season_start_dt.date()

    while day <= end:
        logger.info("Getting daily "+season+" notary notarisations via get_ntx_for_day for "+str(day))
        results = get_ntx_for_day(day, season)
        results_list = []
        time_stamp = int(time.time())

        for item in results:
            results_list.append({
                    "chain":item[0],
                    "notaries":item[1]
                })

        # iterate over notaries list for each record and add to count for chain foreach notary
        notary_ntx_counts = {}
        logger.info("Aggregating "+str(len(results_list))+" rows from notarised table for "+str(day))

        for item in results_list:
            notaries = item['notaries']
            chain = item['chain']

            for notary in notaries:
                if notary not in notary_ntx_counts:
                    notary_ntx_counts.update({notary:{}})
                if chain not in notary_ntx_counts[notary]:
                    notary_ntx_counts[notary].update({chain:1})
                else:
                    count = notary_ntx_counts[notary][chain]+1
                    notary_ntx_counts[notary].update({chain:count})

        # iterate over notary chain counts to calculate scoring category counts.
        node_counts = {}
        other_coins = []
        notary_ntx_pct = {}

        for notary in notary_ntx_counts:
            notary_ntx_pct.update({notary:{}})
            node_counts.update({notary:{
                    "btc_count":0,
                    "antara_count":0,
                    "third_party_count":0,
                    "other_count":0,
                    "total_ntx_count":0
                }})

            for chain in notary_ntx_counts[notary]:
                if chain == "BTC":
                    count = node_counts[notary]["btc_count"]+notary_ntx_counts[notary][chain]
                    node_counts[notary].update({"btc_count":count})
                elif chain in ALL_ANTARA_COINS:
                    count = node_counts[notary]["antara_count"]+notary_ntx_counts[notary][chain]
                    node_counts[notary].update({"antara_count":count})
                elif chain in THIRD_PARTY_COINS:
                    count = node_counts[notary]["third_party_count"]+notary_ntx_counts[notary][chain]
                    node_counts[notary].update({"third_party_count":count})
                else:
                    count = node_counts[notary]["other_count"]+notary_ntx_counts[notary][chain]
                    node_counts[notary].update({"other_count":count})
                    other_coins.append(chain)

                count = node_counts[notary]["total_ntx_count"]+notary_ntx_counts[notary][chain]
                node_counts[notary].update({"total_ntx_count":count})

        # get daily ntx total for each chain
        chain_totals = {}
        chains_aggr_resp = get_chain_ntx_date_aggregates(day, season)

        for item in chains_aggr_resp:
            chain = item[0]
            max_block = item[1]
            max_blocktime = item[2]
            ntx_count = item[3]
            chain_totals.update({chain:ntx_count})

        logger.info("chain_totals: "+str(chain_totals))

        # calculate notary ntx percentage for chains and add row to db table.
        for notary in node_counts:
            for chain in notary_ntx_counts[notary]:
                pct = round(notary_ntx_counts[notary][chain]/chain_totals[chain]*100,2)
                notary_ntx_pct[notary].update({chain:pct})
            row = notarised_count_daily_row()
            row.notary = notary
            row.btc_count = node_counts[notary]['btc_count']
            row.antara_count = node_counts[notary]['antara_count']
            row.third_party_count = node_counts[notary]['third_party_count']
            row.other_count = node_counts[notary]['other_count']
            row.total_ntx_count = node_counts[notary]['total_ntx_count']
            row.chain_ntx_counts = json.dumps(notary_ntx_counts[notary])
            row.chain_ntx_pct = json.dumps(notary_ntx_pct[notary])
            row.season = season
            row.notarised_date = day
            row.update()

        day += delta
    logger.info("Notarised blocks daily aggregation for "+season+" notaries finished...")

def update_season_notarised_counts(season):
    logger.info("Getting "+season+" season_notarised_counts")

    ac_block_heights = get_ac_block_info()
    chain_season_ntx_result = get_chain_ntx_season_aggregates(season)
    total_chain_season_ntx = {}

    for item in chain_season_ntx_result:
        chain = item[0]
        count = item[3]
        total_chain_season_ntx.update({
            chain:count
        })

    notary_season_counts = {}
    results = get_ntx_for_season(season)

    for item in results:
        chain = item[0]
        notaries = item[1]

        for notary in notaries:
            if notary not in notary_season_counts:
                notary_season_counts.update({notary:{}})

            if chain not in notary_season_counts[notary]:
                notary_season_counts[notary].update({chain:1})
            else:
                val = notary_season_counts[notary][chain] + 1
                notary_season_counts[notary].update({chain:val})


    for notary in notary_season_counts:
        chain_ntx_counts = notary_season_counts[notary]
        btc_count = 0
        antara_count = 0
        third_party_count = 0
        other_count = 0
        total_ntx_count = 0

        notary_season_pct = {}
        for chain in chain_ntx_counts:
            if chain == "BTC":
                btc_count += chain_ntx_counts[chain]
                total_ntx_count += chain_ntx_counts[chain]
            elif chain in THIRD_PARTY_COINS:
                third_party_count += chain_ntx_counts[chain]
                total_ntx_count += chain_ntx_counts[chain]
            elif chain in ANTARA_COINS:
                antara_count += chain_ntx_counts[chain]
                total_ntx_count += chain_ntx_counts[chain]
            else:
                other_count += chain_ntx_counts[chain]

            pct = round(chain_ntx_counts[chain]/total_chain_season_ntx[chain]*100,3)
            notary_season_pct.update({chain:pct})

        row = notarised_count_season_row()
        row.notary = notary
        row.btc_count = btc_count
        row.antara_count = antara_count
        row.third_party_count = third_party_count
        row.other_count = other_count
        row.total_ntx_count = total_ntx_count
        row.chain_ntx_counts = json.dumps(chain_ntx_counts)
        row.chain_ntx_pct = json.dumps(notary_season_pct)
        row.season = season
        row.update()


    results = get_chain_ntx_season_aggregates(season)

    for item in results:
        chain = item[0]
        block_height = item[1]
        max_time = item[2]
        ntx_count = item[3]
        cols = 'block_hash, txid, block_time, opret, ac_ntx_blockhash, ac_ntx_height'
        conditions = "block_height="+str(block_height)+" AND chain='"+chain+"'"
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
        row.update()
    logger.info(f"{season} season_notarised_counts complete")


def update_latest_ntx(season):

    sql = "SELECT chain, MAX(block_time) \
           FROM notarised WHERE \
           season = '"+str(season)+"' \
           GROUP BY chain;"
    CURSOR.execute(sql)
    resp = CURSOR.fetchall()

    for item in resp:
        chain = item[0]
        block_time = item[1]
        sql = "SELECT block_height, txid, notaries \
               FROM notarised WHERE season='"+season+"' AND \
               chain='"+str(chain)+"' AND block_time="+str(block_time)+";"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()

        for x in rows:
            block_height = x[0]
            txid = x[1]
            notaries = x[2]
            for notary in notaries:
                row = last_notarised_row()
                row.notary = notary
                row.chain = chain
                row.txid = txid
                row.block_height = block_height
                row.block_time = block_time
                row.season = season
                row.update()


tip = int(RPC["KMD"].getblockcount())

seasons = get_notarised_seasons()

for season in seasons:
    if season not in ["Season_1", "Season_2", "Season_3", "Unofficial"]:

        if season == get_season(time.time()) and season.find("Testnet") == -1:

            start_block = SEASONS_INFO[season]["start_block"]
            end_block = SEASONS_INFO[season]["end_block"]

            if SKIP_UNTIL_YESTERDAY:
                start_block = tip - 24*60*2
                logger.info(f"Processing notarisations for {season}, blocks {start_block} - {end_block}")
                unrecorded_KMD_txids = get_unrecorded_KMD_txids(tip, season)
                unrecorded_KMD_txids.sort()
                update_KMD_notarisations(unrecorded_KMD_txids)

            else:

                windows = []
                chunk_size = 50000
                for i in range(start_block, end_block, chunk_size):
                    windows.append((i, i+chunk_size))

                logger.info(f"Processing notarisations for {season}, blocks {start_block} - {end_block}")
                for x in windows:
                    logger.info(f"Processing notarisations for blocks {x[0]} - {x[1]}")
                    unrecorded_KMD_txids = get_unrecorded_KMD_txids(tip, season, x[0], x[1])
                    unrecorded_KMD_txids.sort()
                    update_KMD_notarisations(unrecorded_KMD_txids)

            # TODO: add season / server / epoch to the aggregate tables
            # update_daily_notarised_counts(season)
            # update_daily_notarised_chains(season)

            update_season_notarised_counts(season)
            update_latest_ntx(season)


CURSOR.close()
CONN.close()


