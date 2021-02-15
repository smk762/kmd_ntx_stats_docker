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
from dotenv import load_dotenv
from lib_rpc import def_credentials
from lib_electrum import get_ac_block_info
from lib_const import *
from lib_notary import *
from lib_table_update import *
from lib_table_select import *
from lib_api import *

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

load_dotenv()

# set this to False in .env when originally populating the table, or rescanning
skip_past_seasons = (os.getenv("skip_past_seasons") == 'True')

# set this to True in .env to quickly update tables with most recent data
skip_until_yesterday = (os.getenv("skip_until_yesterday") == 'True')

'''
This script scans the blockchain for notarisation txids that are not already recorded in the database.
After updaing the "notarised" table, aggregations are performed to get counts for notaries and chains within each season.
It is intended to be run as a cronjob every 15-30 min
Script runtime is around 5-10 mins, except for initial population which is up to 1 day per season
'''

# Threading function to get daily aggregates
class daily_chain_thread(threading.Thread):

    def __init__(self, cursor, season, day):
        threading.Thread.__init__(self)
        self.season = season
        self.cursor = cursor
        self.day = day

    def run(self):
        thread_chain_ntx_daily_aggregate(self.cursor, self.season, self.day)

# Threaded update of daily aggregates for KMD notarisations for each chain
def thread_chain_ntx_daily_aggregate(cursor, season, day):

    chains_aggr_resp = get_chain_ntx_date_aggregates(cursor, day)
    for item in chains_aggr_resp:
        try:
            chain = item[0]
            max_block = item[1]
            max_blocktime = item[2]
            ntx_count = item[3]
            if ntx_count != 0:
                row_data = (chain, ntx_count, str(day))
                logger.info("Adding daily counts for "+chain+" on "+str(day)+" to notarised_chain table")
                update_daily_notarised_chain_tbl(conn, cursor, row_data)
                logger.info("OK in thread_chain_ntx_daily_aggregate: "+str(item)+" on "+str(day))
        except Exception as e:
            logger.warning("Error in thread_chain_ntx_daily_aggregate: "+str(e))
            logger.warning("Error in thread_chain_ntx_daily_aggregate: "+str(item))
            logger.warning("Error in thread_chain_ntx_daily_aggregate: "+str(day))

# Process KMD notarisation transactions from KMD OpReturns
def update_KMD_notarisations(unrecorded_KMD_txids):
    logger.info("Updating KMD notarisations...")

    i = 0
    records = []
    start = time.time()
    notary_last_ntx = get_notary_last_ntx(cursor)
    num_unrecorded_KMD_txids = len(unrecorded_KMD_txids)
    
    for txid in unrecorded_KMD_txids:
        row_data = get_ntx_data(txid)
        i += 1

        if row_data is not None: # ignore TXIDs that are not notarisations
            chain = row_data[0]

            if chain != 'KMD': # KMD -> BTC notarisations are requested via BTC blockchain APIs
                records.append(row_data)
                runtime = int(time.time()-start)
                pct = round(i/num_unrecorded_KMD_txids*100,3)
                est_end = int(100/pct*runtime)
                logger.info(str(pct)+"% :"+str(i)+"/"+str(num_unrecorded_KMD_txids)+
                         " records added to db ["+str(runtime)+"/"+str(est_end)+" sec]")
                update_ntx_records(conn, cursor, records)
                records = []

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
    if skip_until_yesterday:
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
            thread_list.append(daily_chain_thread(cursor, season, day))
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

    if skip_until_yesterday:
        logger.warning("Starting "+season+" scan from 24hrs ago...")
        day = end - delta
    else:
        logger.warning("Starting "+season+" scan from start of "+season)
        day = season_start_dt.date()

    while day <= end:
        logger.info("Getting daily "+season+" notary notarisations via get_ntx_for_day for "+str(day))
        results = get_ntx_for_day(cursor, day)
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
                elif chain in all_antara_coins:
                    count = node_counts[notary]["antara_count"]+notary_ntx_counts[notary][chain]
                    node_counts[notary].update({"antara_count":count})
                elif chain in third_party_coins:
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
        chains_aggr_resp = get_chain_ntx_date_aggregates(cursor, day)

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

            row_data = (notary, node_counts[notary]['btc_count'], node_counts[notary]['antara_count'], 
                        node_counts[notary]['third_party_count'], node_counts[notary]['other_count'], 
                        node_counts[notary]['total_ntx_count'], json.dumps(notary_ntx_counts[notary]),
                        json.dumps(notary_ntx_pct[notary]), time_stamp, season, day)

            logger.info("Adding counts for "+season+" "+notary+" for "+str(day)+" to notarised_count_daily table")
            update_daily_notarised_count_tbl(conn, cursor, row_data)

        day += delta
    logger.info("Notarised blocks daily aggregation for "+season+" notaries finished...")

def update_season_notarised_counts(season):

    ac_block_heights = get_ac_block_info()
    chain_season_ntx_result = get_chain_ntx_season_aggregates(cursor, season)
    total_chain_season_ntx = {}

    for item in chain_season_ntx_result:
        chain = item[0]
        count = item[3]
        total_chain_season_ntx.update({
            chain:count
        })

    notary_season_counts = {}
    logger.info("Getting "+season+" notary notarisations")
    results = get_ntx_for_season(cursor, season)

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
            elif chain in third_party_coins:
                third_party_count += chain_ntx_counts[chain]
                total_ntx_count += chain_ntx_counts[chain]
            elif chain in antara_coins:
                antara_count += chain_ntx_counts[chain]
                total_ntx_count += chain_ntx_counts[chain]
            else:
                other_count += chain_ntx_counts[chain]

            pct = round(chain_ntx_counts[chain]/total_chain_season_ntx[chain]*100,3)
            notary_season_pct.update({chain:pct})

        time_stamp = time.time()
        row_data = (notary, btc_count, antara_count, \
                    third_party_count, other_count, \
                    total_ntx_count, json.dumps(chain_ntx_counts), \
                    json.dumps(notary_season_pct), time_stamp, season)

        update_season_notarised_count_tbl(conn, cursor, row_data)

    results = get_chain_ntx_season_aggregates(cursor, season)

    for item in results:
        chain = item[0]
        block_height = item[1]
        max_time = item[2]
        ntx_count = item[3]
        cols = 'block_hash, txid, block_time, opret, ac_ntx_blockhash, ac_ntx_height'
        conditions = "block_height="+str(block_height)+" AND chain='"+chain+"'"
        last_ntx_result = select_from_table(cursor, 'notarised', cols, conditions)[0]
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

        row_data = (chain, ntx_count, block_height, kmd_ntx_blockhash,\
                    kmd_ntx_txid, kmd_ntx_blocktime, opret, ac_ntx_blockhash, \
                    ac_ntx_height, ac_block_height, ntx_lag, season)

        update_season_notarised_chain_tbl(conn, cursor, row_data)

def update_latest_ntx(cursor):
    season = get_season(time.time())
    # agg = get_chain_ntx_season_aggregates(cursor, season)

    sql = "SELECT chain, MAX(block_time) \
           FROM notarised WHERE \
           season = '"+str(season)+"' \
           GROUP BY chain;"
    cursor.execute(sql)
    resp = cursor.fetchall()

    for item in resp:
        chain = item[0]
        block_time = item[1]
        sql = "SELECT block_height, txid, notaries \
               FROM notarised WHERE season='"+season+"' AND \
               chain='"+str(chain)+"' AND block_time="+str(block_time)+";"
        cursor.execute(sql)
        rows = cursor.fetchall()

        for x in rows:
            print(item)
            block_height = x[0]
            txid = x[1]
            notaries = x[2]
            for notary in notaries:
                last_ntx_row_data = (notary, chain, txid, block_height,
                                     block_time, season)
                update_last_ntx_tbl(conn, cursor, last_ntx_row_data)

rpc = {}
rpc["KMD"] = def_credentials("KMD")

season = get_season(time.time())
tip = int(rpc["KMD"].getblockcount())

conn = connect_db()
cursor = conn.cursor()


if skip_past_seasons:
    logger.info("Processing notarisations for "+season)
    update_BTC_notarisations(conn, cursor, 634000)
    unrecorded_KMD_txids = get_unrecorded_KMD_txids(cursor, tip, season)
    update_KMD_notarisations(unrecorded_KMD_txids)

    update_daily_notarised_counts(season)
    update_daily_notarised_chains(season)

    update_season_notarised_counts(season)

else:
    for season in SEASONS_INFO:
        # Some S1 OP_RETURNS are decoding incorrectly, so skip.
        if season != "Season_1":
            logger.info("Processing notarisations for "+season)

            # TODO: Need to define season BTC start/end blocks!
            update_BTC_notarisations(conn, cursor, 634000) 

            unrecorded_KMD_txids = get_unrecorded_KMD_txids(cursor, tip, season)
            update_KMD_notarisations(unrecorded_KMD_txids)

            update_daily_notarised_counts(season)
            update_daily_notarised_chains(season)

            update_season_notarised_counts(season)

notarised_chains = get_notarised_chains(cursor)
notarised_seasons = get_notarised_seasons(cursor)

update_latest_ntx(cursor)
update_ntx_tenure(notarised_chains, notarised_seasons)

cursor.close()
conn.close()
