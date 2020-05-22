#!/usr/bin/env python3
import os
import sys
import json
import binascii
import time
import logging
import logging.handlers
import psycopg2
import threading
import table_lib
from decimal import *
from datetime import datetime as dt
import datetime
from dotenv import load_dotenv
from rpclib import def_credentials
from psycopg2.extras import execute_values
from electrum_lib import get_ac_block_info
from address_lib import notary_info, seasons_info, known_addresses
from coins_lib import third_party_coins, antara_coins, ex_antara_coins, all_antara_coins, all_coins

class daily_chain_thread(threading.Thread):
    def __init__(self, cursor, season, day):
        threading.Thread.__init__(self)
        self.season = season
        self.cursor = cursor
        self.day = day
    def run(self):
        thread_chain_ntx_daily_aggregate(self.cursor, self.season, self.day)
'''
This script scans the blockchain for notarisation txids that are not already recorded in the database.
After updaing the "notarised" table, aggregations are performed to get counts for notaries and chains within each season.
It is intended to be run as a cronjob every 15-30 min
Script runtime is around 5-10 mins sepending on number of seasons to aggregate
'''

# set this to false when originally populating the table, or rescanning
skip_past_seasons = True
# set this to True to quickly update tables with most recent data
skip_until_yesterday = True

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def get_ntx_txids(ntx_addr, start, end):
    return rpc["KMD"].getaddresstxids({"addresses": [ntx_addr], "start":start, "end":end})
    
def get_ticker(scriptPubKeyBinary):
    chain = ''
    while len(chain) < 1:
        for i in range(len(scriptPubKeyBinary)):
            if chr(scriptPubKeyBinary[i]).encode() == b'\x00':
                j = i+1
                while j < len(scriptPubKeyBinary)-1:
                    chain += chr(scriptPubKeyBinary[j])
                    j += 1
                    if chr(scriptPubKeyBinary[j]).encode() == b'\x00':
                        break
                break
    if chr(scriptPubKeyBinary[-4])+chr(scriptPubKeyBinary[-3])+chr(scriptPubKeyBinary[-2]) =="KMD":
        chain = "KMD"
    return str(chain)

def get_ntx_data(txid):
    raw_tx = rpc["KMD"].getrawtransaction(txid,1)
    block_hash = raw_tx['blockhash']
    dest_addrs = raw_tx["vout"][0]['scriptPubKey']['addresses']
    block_time = raw_tx['blocktime']
    block_datetime = dt.utcfromtimestamp(raw_tx['blocktime'])
    this_block_height = raw_tx['height']
    for season_num in seasons_info:
        if block_time < seasons_info[season_num]['end_time']:
            season = season_num
            break
    if len(dest_addrs) > 0:
        if ntx_addr in dest_addrs:
            if len(raw_tx['vin']) == 13:
                notary_list = []
                for item in raw_tx['vin']:
                    if "address" in item:
                        if item['address'] in known_addresses:
                            notary = known_addresses[item['address']]
                            notary_list.append(notary)
                        else:
                            notary_list.append(item['address'])
                notary_list.sort()
                opret = raw_tx['vout'][1]['scriptPubKey']['asm']
                logger.info(opret)
                if opret.find("OP_RETURN") != -1:
                    scriptPubKey_asm = opret.replace("OP_RETURN ","")
                    ac_ntx_blockhash = lil_endian(scriptPubKey_asm[:64])
                    try:
                        ac_ntx_height = int(lil_endian(scriptPubKey_asm[64:72]),16) 
                    except:
                        logger.info(scriptPubKey_asm)
                        sys.exit()
                    scriptPubKeyBinary = binascii.unhexlify(scriptPubKey_asm[70:])
                    chain = get_ticker(scriptPubKeyBinary)
                    if chain.endswith("KMD"):
                        chain = "KMD"
                    if chain == "KMD":
                        btc_txid = lil_endian(scriptPubKey_asm[72:136])
                    elif chain not in noMoM:
                        # not sure about this bit, need another source to validate the data
                        try:
                            start = 72+len(chain)*2+4
                            end = 72+len(chain)*2+4+64
                            MoM_hash = lil_endian(scriptPubKey_asm[start:end])
                            MoM_depth = int(lil_endian(scriptPubKey_asm[end:]),16)
                        except Exception as e:
                            logger.debug(e)
                    # some decodes have a null char error, this gets rid of that so populate script doesnt error out 
                    if chain.find('\x00') != -1:
                        chain = chain.replace('\x00','')
                    # (some s1 op_returns seem to be decoding differently/wrong. This ignores them)
                    if chain.upper() == chain:
                        row_data = (chain, this_block_height, block_time, block_datetime,
                                    block_hash, notary_list, ac_ntx_blockhash, ac_ntx_height,
                                    txid, opret, season)
                        return row_data
                else:
                    # no opretrun in tx, and shouldnt polute the DB.
                    row_data = ("not_opret", this_block_height, block_time, block_datetime,
                                block_hash, notary_list, "unknown", 0, txid, "unknown", season)
                    return None
                
            else:
                # These are related to easy mining, and shouldnt polute the DB.
                row_data = ("low_vin", this_block_height, block_time, block_datetime,
                            block_hash, [], "unknown", 0, txid, "unknown", season)
                return None
        else:
            # These are outgoing, and should not polute the DB.
            row_data = ("not_dest", this_block_height, block_time, block_datetime,
                        block_hash, [], "unknown", 0, txid, "unknown", season)
            return None

load_dotenv()

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

conn = table_lib.connect_db()
cursor = conn.cursor()

rpc = {}
rpc["KMD"] = def_credentials("KMD")

ntx_addr = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'

noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'AYA']

tip = int(rpc["KMD"].getblockcount())
recorded_txids = []
start_block = 0
if skip_past_seasons:
    start_block = seasons_info[list(seasons_info.keys())[-1]]["start_block"]
if skip_until_yesterday:
    start_block = tip - 24*60*1
all_txids = []
chunk_size = 100000

logger.info("Getting existing TXIDs from database...")
cursor.execute("SELECT txid from notarised;")
existing_txids = cursor.fetchall()


while tip - start_block > chunk_size:
    logger.info("Getting notarization TXIDs from block chain data for blocks "+str(start_block+1)+" to "+str(start_block+chunk_size)+"...")
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

# Seems to be two txids that are duplicate.
# TODO: scan to find out what the duplicate txids are and which blocks they are in

def update_notarisations():
    records = []
    start = time.time()
    i = 1
    for txid in unrecorded_txids:
        row_data = get_ntx_data(txid)
        if row_data is not None:
            logger.info(row_data)
            records.append(row_data)
            if len(records) == 1:
                now = time.time()
                pct = round(len(records)*i/len(unrecorded_txids)*100,3)
                runtime = int(now-start)
                est_end = int(100/pct*runtime)
                logger.info(str(pct)+"% :"+str(len(records)*i)+"/"+str(len(unrecorded_txids))+" records added to db ["+str(runtime)+"/"+str(est_end)+" sec]")
                logger.info("records: "+str(records))
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

def update_season_notarised_chains(season):
    logger.info("Aggregating Notarised blocks for chains...")
    conn = table_lib.connect_db()
    cursor = conn.cursor()
    # ignore S1 as some chain names are not properly decoding from opret
    if season != 'Season_1':
        logger.info("Aggregating chain notarisations for "+season)
        chains_aggr_resp = table_lib.get_chain_ntx_season_aggregates(cursor, season)

        ac_block_info = get_ac_block_info()

        chain_json = {}
        for item in chains_aggr_resp:
            chain = item[0]
            block_height = item[1]
            kmd_ntx_time = item[2]
            ntx_count = item[3]

            chains_resp = table_lib.get_latest_chain_ntx_info(cursor, chain, block_height)
            chain_json.update({
                chain:{
                    "ntx_count": ntx_count,
                    "block_height": block_height,
                    "kmd_ntx_blocktime": kmd_ntx_time,
                    "kmd_ntx_blockhash": chains_resp[3],
                    "kmd_ntx_txid": chains_resp[4],
                    "opret": chains_resp[2],
                    "ac_ntx_blockhash": chains_resp[0],
                    "ac_ntx_height": chains_resp[1]
                }
            })
            if chain in ac_block_info:
                chain_json[chain].update({
                    "ac_block_height": ac_block_info[chain]['height'],
                    "ntx_lag": ac_block_info[chain]['height'] - chains_resp[1]
                })
            else:
                chain_json[chain].update({
                    "ac_block_height": "no data",
                    "ntx_lag": "no data"
                })
            row_data = ( chain, ntx_count, block_height, chain_json[chain]['kmd_ntx_blockhash'], chain_json[chain]['kmd_ntx_txid'],
                         chain_json[chain]['kmd_ntx_blocktime'], chain_json[chain]['opret'], chain_json[chain]['ac_ntx_blockhash'],
                         chain_json[chain]['ac_ntx_height'], chain_json[chain]['ac_block_height'],
                         chain_json[chain]['ntx_lag'], season)
            logger.info("Adding counts for "+chain+" to "+season+" notarised_chain table")
            table_lib.update_season_notarised_chain_tbl(conn, cursor, row_data)
    logger.info("Notarised blocks for "+season+" chains aggregation complete!")

def update_season_notarised_counts(season):
    # ignore S1 as some opret is not decoding chain correctly
    if season != "Season_1":
        logger.info("Aggregating "+season+" Notarised blocks for notaries...")
        results = table_lib.select_from_table(cursor, "notarised", "chain, notaries",
                  "season='"+season+"';"
                  )
        results_list = []
        time_stamp = int(time.time())
        for item in results:
            results_list.append({
                    "chain":item[0],
                    "notaries":item[1]
                })
        chain_ntx_counts = {}
        logger.info("Aggregating "+str(len(results_list))+" rows from notarised table for "+season)
        for item in results_list:
            notaries = item['notaries']
            chain = item['chain']
            for notary in notaries:
                if notary in seasons_info[season]['notaries']:
                    if notary not in chain_ntx_counts:
                        chain_ntx_counts.update({notary:{}})
                    if chain not in chain_ntx_counts[notary]:
                        chain_ntx_counts[notary].update({chain:1})
                    else:
                        count = chain_ntx_counts[notary][chain]+1
                        chain_ntx_counts[notary].update({chain:count})
        node_counts = {}
        other_coins = []
        chain_ntx_pct = {}
        for notary in chain_ntx_counts:
            chain_ntx_pct.update({notary:{}})
            node_counts.update({notary:{
                    "btc_count":0,
                    "antara_count":0,
                    "third_party_count":0,
                    "other_count":0,
                    "total_ntx_count":0
                }})
            for chain in chain_ntx_counts[notary]:
                if chain == "KMD":
                    count = node_counts[notary]["btc_count"]+chain_ntx_counts[notary][chain]
                    node_counts[notary].update({"btc_count":count})
                elif chain in all_antara_coins:
                    count = node_counts[notary]["antara_count"]+chain_ntx_counts[notary][chain]
                    node_counts[notary].update({"antara_count":count})
                elif chain in third_party_coins:
                    count = node_counts[notary]["third_party_count"]+chain_ntx_counts[notary][chain]
                    node_counts[notary].update({"third_party_count":count})
                else:
                    count = node_counts[notary]["other_count"]+chain_ntx_counts[notary][chain]
                    node_counts[notary].update({"other_count":count})
                    other_coins.append(chain)

                count = node_counts[notary]["total_ntx_count"]+chain_ntx_counts[notary][chain]
                node_counts[notary].update({"total_ntx_count":count})

        chain_totals = {}
        chains_aggr_resp = table_lib.get_chain_ntx_season_aggregates(cursor, season)
        for item in chains_aggr_resp:
            chain = item[0]
            ntx_count = item[3]
            chain_totals.update({chain:ntx_count})

        for notary in node_counts:
            for chain in chain_ntx_counts[notary]:
                pct = round(chain_ntx_counts[notary][chain]/chain_totals[chain]*100,2)
                chain_ntx_pct[notary].update({chain:pct})
            row_data = (notary, node_counts[notary]['btc_count'], node_counts[notary]['antara_count'], 
                        node_counts[notary]['third_party_count'], node_counts[notary]['other_count'], 
                        node_counts[notary]['total_ntx_count'], json.dumps(chain_ntx_counts[notary]),
                        json.dumps(chain_ntx_pct[notary]), time_stamp, season)
            logger.info("Adding counts for "+notary+" to notarised_count_season table")
            table_lib.update_season_notarised_count_tbl(conn, cursor, row_data)
    logger.info("Notarised blocks "+season+" aggregation for notaries finished...")

def update_daily_notarised_chains(season):
    logger.info("Aggregating Notarised blocks for chains...")
    # start on date of most recent season
    if season != 'Season_1':
        season_start_time = seasons_info[season]["start_time"]
        season_start_dt = dt.fromtimestamp(season_start_time)
        start = season_start_dt.date()
        end = datetime.date.today()
        if skip_until_yesterday:
            start = end - datetime.timedelta(days=1)
        delta = datetime.timedelta(days=1)

        logger.info("Aggregating daily chain notarisations from "+str(start)+" to "+str(end))
        day = start

        thread_list = []
        while day <= end:
            logger.info("Aggregating chain notarisations for "+str(day))
            thread_list.append(daily_chain_thread(cursor, season, day))
            day += delta
        for thread in thread_list:
            time.sleep(10)
            thread.start()
    logger.info("Notarised blocks for daily chains aggregation complete!")

def thread_chain_ntx_daily_aggregate(cursor, season, day):
    chains_aggr_resp = table_lib.get_chain_ntx_date_aggregates(cursor, day)
    for item in chains_aggr_resp:
        print(chains_aggr_resp)
        chain = item[0]
        ntx_count = item[3]
        if ntx_count != 0:
            row_data = (chain, ntx_count, str(day))
            logger.info("Adding daily counts for "+chain+" on "+str(day)+" to notarised_chain table")
            table_lib.update_daily_notarised_chain_tbl(conn, cursor, row_data)

def update_daily_notarised_counts(season):
    # start on date of most recent season
    season_start_time = seasons_info[season]["start_time"]
    season_start_dt = dt.fromtimestamp(season_start_time)
    start = season_start_dt.date()
    end = datetime.date.today()
    if skip_until_yesterday:
        start = end - datetime.timedelta(days=1)
    delta = datetime.timedelta(days=1)
    logger.info("Aggregating daily notary notarisations from "+str(start)+" to "+str(end))
    day = start
    # ignore S1 as some opret is not decoding chain correctly
    while day <= end:
        results = table_lib.get_ntx_for_day(cursor, day)

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
        chains_aggr_resp = table_lib.get_chain_ntx_date_aggregates(cursor, day)
        for item in chains_aggr_resp:
            chain = item[0]
            ntx_count = item[3]
            chain_totals.update({chain:ntx_count})

        # calculate notary ntx percentage for chains and add row to db table.
        for notary in node_counts:
            for chain in notary_ntx_counts[notary]:
                pct = round(notary_ntx_counts[notary][chain]/chain_totals[chain]*100,2)
                notary_ntx_pct[notary].update({chain:pct})
            row_data = (notary, node_counts[notary]['btc_count'], node_counts[notary]['antara_count'], 
                        node_counts[notary]['third_party_count'], node_counts[notary]['other_count'], 
                        node_counts[notary]['total_ntx_count'], json.dumps(notary_ntx_counts[notary]),
                        json.dumps(notary_ntx_pct[notary]), time_stamp, season, day)
            logger.info("Adding counts for "+notary+" for "+str(day)+" to notarised_count_daily table")
            table_lib.update_daily_notarised_count_tbl(conn, cursor, row_data)
        day += delta
    logger.info("Notarised blocks daily aggregation for notaries finished...")

update_notarisations()
if skip_past_seasons:
        season = list(seasons_info.keys())[-1]
        update_daily_notarised_chains(season)
        update_daily_notarised_counts(season)
        update_season_notarised_chains(season)
        update_season_notarised_counts(season)
else:
    for season in seasons_info:
        # Some S1 OP_RETURNS are decoding incorrectly, so skip.
        if season != "Season_1":
            update_season_notarised_chains(season)
            update_season_notarised_counts(season)
            update_daily_notarised_chains(season)
            update_daily_notarised_counts(season)

cursor.close()

conn.close()