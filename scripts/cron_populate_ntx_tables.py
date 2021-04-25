#!/usr/bin/env python3
import os
import sys
import json
import time
import random
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
from models import notarised_row, notarised_count_season_row, notarised_chain_season_row, notarised_count_daily_row, notarised_chain_daily_row, last_notarised_row, get_chain_epoch_score_at, get_chain_epoch_at


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

def run_updates():
    return __name__ == "__main__"

# Threaded update of daily aggregates for KMD notarisations for each chain
def thread_chain_ntx_daily_aggregate(season, day):

    chains_aggr_resp = get_chain_ntx_date_aggregates(day, season)
    logger.info(f"[get_chain_ntx_date_aggregates]: {chains_aggr_resp}")
    for item in chains_aggr_resp:
        try:
            row = notarised_chain_daily_row()
            row.chain = item[0]
            row.ntx_count = item[3]
            row.notarised_date = str(day)
            row.update()

        except Exception as e:
            logger.error("Exception in [thread_chain_ntx_daily_aggregate]: "+str(e))


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
            if chain == "GLEEC":
                ntx_row.server = get_gleec_ntx_server(ntx_row.txid)
            else:
                ntx_row.server = row_data[12]
            ntx_row.score_value = get_chain_epoch_score_at(ntx_row.season, ntx_row.server, ntx_row.chain, int(ntx_row.block_time))
            ntx_row.epoch = get_chain_epoch_at(ntx_row.season, ntx_row.server, ntx_row.chain, int(ntx_row.block_time))
            if ntx_row.score_value > 0:
                ntx_row.scored = True
            else:
                ntx_row.scored = False
            ntx_row.btc_validated = "N/A"
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
                if chain == "KMD":
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


def get_notary_season_count_pct(season):
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
                notary_season_counts[notary][chain] += 1


    notary_season_pct = {}
    for notary in notary_season_counts:

        chain_ntx_counts = notary_season_counts[notary]
        btc_count = 0
        antara_count = 0
        third_party_count = 0
        other_count = 0
        total_ntx_count = 0

        if notary not in notary_season_pct:
            notary_season_pct.update({notary:{}})
        for chain in chain_ntx_counts:
            if chain == "KMD":
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
            notary_season_pct[notary].update({chain:pct})
 
    return chain_ntx_counts, notary_season_pct


def update_season_notarised_counts(season):
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
            logger.info(f"last_ntx_result: {last_ntx_result}")
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


def get_notarisation_data(season, min_time=None, max_time=None, notary_name=None, chain_name=None, server_name=None, epoch_name=None):
    logger.info(f"Getting ntx data for {season}")

    sql = f"SELECT chain, notaries, \
                    season, server, epoch, score_value \
                     FROM notarised"
    where = []
    if season:
        where.append(f"season = '{season}'")
    if min_time:
        where.append(f"block_time >= {min_time}")
    if max_time:
        where.append(f"block_time <= {max_time}")
    if chain_name:
        where.append(f"chain = '{chain_name}'")
    if server_name:
        where.append(f"server = '{server_name}'")
    if epoch_name:
        where.append(f"epoch = '{epoch_name}'")

    if len(where) > 0:
        sql += " WHERE "
        sql += " AND ".join(where)
    sql += ";"

    logger.info(f"[get_notarisation_data] {where}")
    ntx_summary = {}
    chain_totals = {}
    
    try:
        CURSOR.execute(sql)
        results = CURSOR.fetchall()

        for item in results:
            chain = item[0]
            notaries = item[1]
            season = item[2]
            server = item[3]
            epoch = item[4]
            score_value = round(float(item[5]), 8)

            if "Unofficial" not in [season, server, epoch]:
                if chain in ["BTC", "LTC", "KMD"]:
                    server = chain

                if server not in chain_totals:
                    chain_totals.update({
                        server: {
                            chain: {
                                "count":0,
                                "total_score":0                        
                            }
                        }
                    })

                if chain not in chain_totals[server]:
                    chain_totals[server].update({
                        chain: {
                            "count":0,
                            "total_score":0
                        }
                    })

                chain_totals[server][chain]["count"] += 1
                chain_totals[server][chain]["total_score"] += score_value


                for notary in notaries:
                    if (notary_name is None or notary_name == notary) and (chain_name is None or chain_name == chain):
                        if notary not in ntx_summary:
                            ntx_summary.update({
                                notary:{
                                    "seasons": {}
                                }
                            })

                        if season not in ntx_summary[notary]["seasons"]:
                            ntx_summary[notary]["seasons"].update({
                                season: {
                                    "servers": {},
                                    "season_ntx_count":0,
                                    "season_score":0
                                }
                            })

                        if server not in ntx_summary[notary]["seasons"][season]["servers"]:
                            ntx_summary[notary]["seasons"][season]["servers"].update({
                                server: {
                                    "epochs": {},
                                    "server_ntx_count":0,
                                    "server_score":0                                    
                                }
                            })

                        if epoch not in ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"]:
                            ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"].update({
                                epoch:{
                                    "chains": {},
                                    "score_per_ntx":score_value,
                                    "epoch_ntx_count":0,
                                    "epoch_score":0
                                }
                            })

                        if chain not in ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"]:
                            ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"].update({
                                chain:{
                                    "chain_ntx_count":0,
                                    "chain_score":0
                                }
                            })


                        ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["chain_ntx_count"] += 1
                        ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["chain_score"] += score_value

                        ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["epoch_ntx_count"] += 1
                        ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["epoch_score"] += score_value

                        ntx_summary[notary]["seasons"][season]["servers"][server]["server_ntx_count"] += 1
                        ntx_summary[notary]["seasons"][season]["servers"][server]["server_score"] += score_value

                        ntx_summary[notary]["seasons"][season]["season_ntx_count"] += 1
                        ntx_summary[notary]["seasons"][season]["season_score"] += score_value


        return ntx_summary, chain_totals
        
    except Exception as e:
        logger.error(f"Error in [get_notarisation_data]: {e}")
        return ntx_summary, chain_totals


def update_latest_ntx(season, server):

    sql = "SELECT chain, MAX(block_time) \
           FROM notarised WHERE \
           season = '"+str(season)+"' \
           AND server = '"+str(server)+"' \
           GROUP BY chain;"

    try:
        CURSOR.execute(sql)
        resp = CURSOR.fetchall()

        for item in resp:
            chain = item[0]
            block_time = item[1]
            sql = "SELECT block_height, txid, notaries \
                   FROM notarised WHERE season='"+season+"' AND server='"+server+"' AND \
                   chain='"+str(chain)+"' AND block_time="+str(block_time)+";"

            try:

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
                        row.server = server
                        row.update()

            except Exception as e:
                logger.error(f"Exception in [update_latest_ntx]: {e}")

    except Exception as e:
        logger.error(f"Exception in [update_latest_ntx]: {e}")


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
            
    ntx_summary, chain_totals = get_notarisation_data(season)
    chain_ntx_counts, notary_season_pct = get_notary_season_count_pct(season)
    for notary in ntx_summary:

        for summary_season in ntx_summary[notary]["seasons"]:
            logger.info(f"Getting season summary for {notary} {summary_season}")


            if notary in KNOWN_NOTARIES:

                season_ntx_count_row = notarised_count_season_row()
                season_ntx_count_row.notary = notary
                season_ntx_count_row.season = summary_season
                servers = ntx_summary[notary]["seasons"][summary_season]['servers']

                if "KMD" in servers:
                    season_ntx_count_row.btc_count = servers['KMD']['server_ntx_count']

                elif "LTC" in servers:
                    season_ntx_count_row.btc_count = servers['LTC']['server_ntx_count']

                else: 
                    season_ntx_count_row.btc_count = 0

                if 'Main' in servers:
                    season_ntx_count_row.antara_count = servers['Main']['server_ntx_count']

                else:
                    season_ntx_count_row.antara_count = 0

                if 'Third_Party' in servers:
                    season_ntx_count_row.third_party_count = servers['Third_Party']['server_ntx_count']

                else:
                    season_ntx_count_row.third_party_count = 0

                season_ntx_count_row.other_count = 0
                season_ntx_count_row.total_ntx_count = ntx_summary[notary]["seasons"][summary_season]['season_ntx_count']

                season_ntx_count_row.season_score = ntx_summary[notary]["seasons"][summary_season]["season_score"]
                season_ntx_count_row.chain_ntx_counts = json.dumps(ntx_summary[notary])
                season_ntx_count_row.chain_ntx_pct = json.dumps(notary_season_pct[notary])
                season_ntx_count_row.time_stamp = time.time()
                season_ntx_count_row.update()


def rescan_notaries(season):
    sql = f"SELECT chain, block_height, block_time, block_datetime, block_hash, \
            notaries, notary_addresses, ac_ntx_blockhash, \
            ac_ntx_height, txid, opret, season,\
            server, epoch, score_value, scored, btc_validated \
            FROM notarised"
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
            notaries = item[5][:]
            for notary in notaries:
                if len(notary) > 20:
                    # e.g. record input as address before pubkey added
                    try:
                        notaries.remove(notary)
                        notaries.append(KNOWN_ADDRESSES[notary])
                        logger.warning(f"!!!! {item[9]} Invalid notary {notary} set to {KNOWN_ADDRESSES[notary]}")
                    except:
                        logger.warning(f"!!!! {item[9]} Invalid notary {notary}")
            if notaries != item[5]:
                row = notarised_row()
                row.chain = item[0]
                row.block_height = item[1]
                row.block_time = item[2]
                row.block_datetime = item[3]
                row.block_hash = item[4]
                row.notaries = notaries
                row.notary_addresses = item[6]
                row.ac_ntx_blockhash = item[7]
                row.ac_ntx_height = item[8]
                row.txid = item[9]
                row.opret = item[10]
                row.season = item[11]
                row.server = item[12]
                row.epoch = item[13]
                row.score_value = item[14]
                row.scored = item[15]
                row.btc_validated = item[16]
                row.update()

    except Exception as e:
        logger.error(f"Exception in [rescan_notaries]: {e}")

if __name__ == "__main__":

    # Uncomment if record contains address rather than notary in [notaries] list (e.g. saved before pubkeys updated)
    # rescan_notaries(SEASON)

    TIP = int(RPC["KMD"].getblockcount())

    seasons = get_notarised_seasons()
    logger.info(f"Preparing to populate NTX tables...")

    for season in seasons:
        if season in ["Season_1", "Season_2", "Season_3", "Unofficial", "Season_5_Testnet"]:
            logger.warning(f"Skipping season: {season}")
        else:
            scan_rpc_for_ntx(season)

            # TODO: add season / server / epoch to the aggregate tables
            update_daily_notarised_counts(season)
            update_daily_notarised_chains(season)

            update_season_notarised_counts(season)
            season_servers = get_notarised_servers(season)
            for server in season_servers:
                update_latest_ntx(season, server)



