#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
import logging.handlers
import psycopg2
import threading
from decimal import *
from datetime import datetime as dt
import datetime
from dotenv import load_dotenv
from rpclib import def_credentials
from psycopg2.extras import execute_values
from electrum_lib import get_ac_block_info
from notary_lib import *

'''
This script scans the blockchain for notarisation txids that are not already recorded in the database.
After updaing the "notarised" table, aggregations are performed to get counts for notaries and chains within each season.
It is intended to be run as a cronjob every 15-30 min
Script runtime is around 5-10 mins, except for initial population which is up to 1 day per season
'''

class daily_chain_thread(threading.Thread):
    def __init__(self, cursor, season, day):
        threading.Thread.__init__(self)
        self.season = season
        self.cursor = cursor
        self.day = day
    def run(self):
        thread_chain_ntx_daily_aggregate(self.cursor, self.season, self.day)

# set this to false when originally populating the table, or rescanning
skip_past_seasons = True

# set this to True to quickly update tables with most recent data
skip_until_yesterday = True

load_dotenv()

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

conn = connect_db()
cursor = conn.cursor()


# Seems to be two txids that are duplicate.
# TODO: scan to find out what the duplicate txids are and which blocks they are in


def get_season_from_notaries(notaries):
    seasons = list(notary_addresses.keys())[::-1]
    for season in seasons:
        notary_seasons = []
        for notary in notaries:
            if season.find("Third") == -1 and season.find(".5") == -1:
                season_notaries = list(notary_addresses[season].keys())
                if notary in season_notaries:
                    notary_seasons.append(season)
        if len(notary_seasons) == 13:
            return season
    return None
    
def update_notarisations():
    # Get chain and time of last ntx
    cursor.execute("SELECT notary, chain, block_height from last_notarised;")
    last_ntx = cursor.fetchall()
    notary_last_ntx = {}
    for item in last_ntx:
        notary = item[0]
        chain = item[1]
        block_height = item[2]
        if notary not in notary_last_ntx:
            notary_last_ntx.update({notary:{}})
        notary_last_ntx[notary].update({chain:block_height})

    # Get chain and time of last btc ntx
    cursor.execute("SELECT notary, block_height from last_notarised;")
    last_btc_ntx = cursor.fetchall()
    notary_last_btc_ntx = {}
    for item in last_btc_ntx:
        notary = item[0]
        block_height = item[1]
        if notary not in notary_last_btc_ntx:
            notary_last_btc_ntx.update({notary:{}})
        notary_last_btc_ntx.update({notary:block_height})

    records = []
    start = time.time()
    i = 1
    j = 0
    
    for txid in unrecorded_txids:
        row_data = get_ntx_data(txid)
        j += 1
        num_unrecorded_txids = len(unrecorded_txids)
        if row_data is not None:
            chain = row_data[0]
            block_height = row_data[1]
            block_time = row_data[2]
            txid = row_data[8]
            notaries = row_data[5]
            season = get_season_from_notaries(notaries)
            if not season:
                if chain not in ['KMD', 'BTC']:
                    for season_num in seasons_info:
                        if block_time < seasons_info[season_num]['end_time'] and block_time >= seasons_info[season_num]['start_time']:
                            season = season_num
                else:
                    for season_num in seasons_info:
                        if block_height < seasons_info[season_num]['end_block'] and block_height >= seasons_info[season_num]['start_block']:
                            season = season_num            

            # update last ntx or last btc if newer than in tables.
            for notary in notaries:
                last_ntx_row_data = (notary, chain, txid, block_height,
                                     block_time, season)
            
                if notary in notary_last_ntx:
                    if chain not in notary_last_ntx[notary]:
                        notary_last_ntx[notary].update({chain:0})
                    if block_height > notary_last_ntx[notary][chain]:
                        update_last_ntx_tbl(conn, cursor, last_ntx_row_data)
                else:
                    update_last_ntx_tbl(conn, cursor, last_ntx_row_data)
                if chain == 'KMD':
                    last_btc_ntx_row_data = (notary, txid, block_height,
                                         block_time, season)

                    if notary in notary_last_btc_ntx:
                        if block_height > notary_last_btc_ntx[notary]:
                            update_last_btc_ntx_tbl(conn, cursor, last_btc_ntx_row_data)
                    else:
                        update_last_btc_ntx_tbl(conn, cursor, last_btc_ntx_row_data)
            

            records.append(row_data)
            if len(records) == 1:
                now = time.time()
                pct = len(records)*j/num_unrecorded_txids*100
                runtime = int(now-start)
                est_end = int(100/pct*runtime)
                pct = round(j/num_unrecorded_txids*100,3)
                logger.info(str(pct)+"% :"+str(j)+"/"+str(num_unrecorded_txids)+" records added to db ["+str(runtime)+"/"+str(est_end)+" sec]")
                # logger.info("records: "+str(records))
                logger.info("-----------------------------")
                execute_values(cursor, "INSERT INTO notarised (chain, block_height, block_time, block_datetime, \
                                        block_hash, notaries, ac_ntx_blockhash, ac_ntx_height, txid, opret, \
                                        season) VALUES %s", records)
                conn.commit()
                records = []
                i += 1
                if i%5 == 0:
                    cursor.execute("SELECT COUNT(*) from notarised;")
                    block_count = cursor.fetchone()
                    logger.info("notarisations in database: "+str(block_count[0])+"/"+str(len(all_txids)))
    execute_values(cursor, "INSERT INTO notarised (chain, block_height, block_time, block_datetime, block_hash, \
                            notaries, ac_ntx_blockhash, ac_ntx_height, txid, opret, season) VALUES %s", records)

    conn.commit()
    logger.info("Notarised blocks updated!")
    logger.info("NTX Address transactions processed: "+str(len(unrecorded_txids)))
    logger.info(str(len(unrecorded_txids))+" notarised TXIDs added to table")


def update_daily_notarised_chains(season):
    logger.info("Aggregating Notarised blocks for chains...")

    season_start_time = seasons_info[season]["start_time"]
    season_start_dt = dt.fromtimestamp(season_start_time)

    season_end_time = seasons_info[season]["end_time"]
    season_end_dt = dt.fromtimestamp(season_end_time)

    logger.info(season + " start: " + str(season_start_dt))
    logger.info(season + " end: " + str(season_end_dt))

    day = season_start_dt.date()
    end = datetime.date.today()
    delta = datetime.timedelta(days=1)
    if skip_until_yesterday:
        logger.info("Starting "+season+" scan from 24hrs ago...")
        day = end - delta
    else:
        logger.info("Starting "+season+" scan from start of "+season)
        day = season_start_dt.date()

    while day <= end:
        thread_list = []
        while day <= end:
            logger.info("Aggregating chain notarisations for "+str(day))
            thread_list.append(daily_chain_thread(cursor, season, day))
            day += delta
        for thread in thread_list:
            time.sleep(5)
            thread.start()
        logger.info("Notarised blocks for daily chains aggregation complete!")
        day += delta
    logger.info("Notarised daily aggregation for "+season+" chains finished...")

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

def update_daily_notarised_counts(season):
    # start on date of most recent season
    season_start_time = seasons_info[season]["start_time"]
    season_start_dt = dt.fromtimestamp(season_start_time)

    season_end_time = seasons_info[season]["end_time"]
    season_end_dt = dt.fromtimestamp(season_end_time)

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
        # Get list of chain/notary list dicts :p
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
                if chain == "KMD":
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
                #logger.info(notary+" count for "+chain+": "+str(notary_ntx_counts[notary][chain]))
                #logger.info("Total count for "+chain+": "+str(chain_totals[chain]))
                pct = round(notary_ntx_counts[notary][chain]/chain_totals[chain]*100,2)
                #logger.info("Pct: "+str(pct))
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
            if chain == "KMD":
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


rpc = {}
rpc["KMD"] = def_credentials("KMD")

ntx_addr = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'

season = get_season(time.time())
tip = int(rpc["KMD"].getblockcount())


recorded_txids = []
start_block = seasons_info[season]["start_block"]
if skip_until_yesterday:
    start_block = tip - 24*60
all_txids = []
chunk_size = 100000

logger.info("Getting existing TXIDs from database...")
cursor.execute("SELECT txid from notarised;")
existing_txids = cursor.fetchall()


while tip - start_block > chunk_size:
    logger.info("Getting notarization TXIDs from block chain data for blocks " \
           +str(start_block+1)+" to "+str(start_block+chunk_size)+"...")
    all_txids += get_ntx_txids(ntx_addr, start_block+1, start_block+chunk_size)
    start_block += chunk_size
all_txids += get_ntx_txids(ntx_addr, start_block+1, tip)

for txid in existing_txids:
    recorded_txids.append(txid[0])
unrecorded_txids = set(all_txids) - set(recorded_txids)
logger.info("TXIDs in chain: "+str(len(all_txids)))
logger.info("TXIDs in chain (set): "+str(len(set(all_txids))))
logger.info("TXIDs in database: "+str(len(recorded_txids)))
logger.info("TXIDs in database (set): "+str(len(set(recorded_txids))))
logger.info("TXIDs not in database: "+str(len(unrecorded_txids)))

if skip_past_seasons:
    logger.info("Processing notarisations for "+season)
    update_notarisations()
    update_daily_notarised_counts(season)
    update_daily_notarised_chains(season)
    update_season_notarised_counts(season)
else:
    for season in seasons_info:
        # Some S1 OP_RETURNS are decoding incorrectly, so skip.
        if season != "Season_1":
            logger.info("Processing notarisations for "+season)
            update_notarisations()
            update_daily_notarised_counts(season)
            update_daily_notarised_chains(season)
            update_season_notarised_counts(season)






cursor.close()

conn.close()
