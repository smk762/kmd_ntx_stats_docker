#!/usr/bin/env python3
import os
import sys
import time
from decimal import *
from datetime import datetime as dt
import datetime
from lib_const import *
from decorators import *
from models import mined_row, daily_mined_count_row, season_mined_count_row
from lib_query import *
import lib_api as api
import lib_validate
import lib_helper

script_path = os.path.abspath(os.path.dirname(sys.argv[0]))

def get_mined_row(block_height, coin="KMD", prices=dict):
    row = mined_row()
    blockinfo = RPC[coin].getblock(str(block_height), 2)

    for tx in blockinfo['tx']:
        if len(tx['vin']) > 0:
            if 'coinbase' in tx['vin'][0]:
                
                if 'addresses' in tx['vout'][0]['scriptPubKey']:
                    address = tx['vout'][0]['scriptPubKey']['addresses'][0]
                else:
                    address = "N/A"

                row.block_height = block_height
                row.block_time = blockinfo['time']
                row.address = address
                row.txid = tx['txid']
                row.diff = blockinfo['difficulty']
                row.value = Decimal(tx['vout'][0]['value'])

                season = lib_validate.get_season(row.block_time)
                date = f"{dt.fromtimestamp(row.block_time)}".split(" ")[0]

                if season in prices:
                    if date in prices[season]:
                        row.usd_price = Decimal(prices[season][date]['usd'])
                        row.btc_price = Decimal(prices[season][date]['btc'])

                break
    return row


def update_mined_row(block_height, coin="KMD", prices=dict):
    row = get_mined_row(block_height, coin, prices)
    if row.address not in ['', 'N/A']:
        row.update()


@print_runtime
def update_mined_table(season, coin="KMD", start_block=None):

    tip = int(RPC[coin].getblockcount())
    if not start_block:
        start_block = tip - 100

    all_blocks = [*range(start_block,tip,1)] 
    recorded_blocks = [block[0] for block in select_from_table('mined', 'block_height')]
    unrecorded_blocks = set(all_blocks) - set(recorded_blocks)
    rescan_blocks = list(set(list(unrecorded_blocks) + [*range(start_block,tip,1)]))
    logger.info(f"[update_mined_table] {len(recorded_blocks)} in mined table in db")
    logger.info(f"[update_mined_table] {len(unrecorded_blocks)} not in mined table in db")
    logger.info(f"[update_mined_table] {len(rescan_blocks)} blocks to scan")

    try:
        with open(f"{script_path}/prices_history.json", "r") as j:
            prices = json.load(j)
    except Exception as e:
        print(e)
        prices = {}

    for block in rescan_blocks:
        update_mined_row(block, "KMD", prices)


@print_runtime
def update_mined_count_daily_table(season, rescan=None):

    try:
        with open(f"{script_path}/prices_history.json", "r") as j:
            prices = json.load(j)
    except Exception as e:
        print(e)
        prices = {}

    season_notaries = SEASONS_INFO[season]["notaries"]
    season_start_dt = dt.fromtimestamp(SEASONS_INFO[season]["start_time"])
    start = season_start_dt.date()
    end = datetime.date.today()
    delta = datetime.timedelta(days=1)
    now = int(time.time())

    if not rescan:
        start = end - datetime.timedelta(days=30)

    logger.info(f"[process_mined_aggregates] Aggregating daily mined counts from {start} to {end}")
    print(f"[process_mined_aggregates] Aggregating daily mined counts from {start} to {end}")

    while start <= end:

        if f"{start}" not in prices[season] or start >= end - delta:
            prices[season].update({f"{start}":{}})
            logger.info(f"Updating [kmd_price] for {start}")
            date = f"{start}".split("-")
            date.reverse()
            date = "-".join(date)
            api_prices = api.get_kmd_price(date)
            prices[season][f"{start}"].update(api_prices)
            time.sleep(1)

        logger.info(f"[process_mined_aggregates] Aggregating daily mined counts for {start}")
        results = get_mined_date_aggregates(start)

        for item in results:
            if len(item) > 0:
                row = daily_mined_count_row()
                row.notary = item[0]
                row.blocks_mined = int(item[1])
                row.sum_value_mined = float(item[2])
                row.mined_date = start
                row.time_stamp = now
                row.update()
                if row.notary in season_notaries:
                    season_notaries.remove(row.notary)

        for remaining_notary in season_notaries:
            row = daily_mined_count_row()
            row.notary = remaining_notary
            row.blocks_mined = 0
            row.sum_value_mined = 0
            row.mined_date = start
            row.time_stamp = now
            row.update()

        start += delta

    logger.info("[process_mined_aggregates] Finished!")
    with open(f"{script_path}/prices_history.json", "w+") as j:
        json.dump(prices, j, indent=4)


@print_runtime
def update_mined_count_season_table(season):
    season_notaries = SEASONS_INFO[season]["notaries"]

    for item in get_season_mined_counts(season):
        if item[0] in SEASONS_INFO[season]["notaries"]:
            if item[1] not in SEASONS_INFO[season]["servers"]["KMD"]["addresses"]["KMD"]:
                continue

        if item[1] in KNOWN_ADDRESSES or int(item[2]) > 25:
            row = season_mined_count_row()
            row.season = season
            row.name = item[0]
            row.address = item[1]
            row.blocks_mined = int(item[2])
            row.sum_value_mined = float(item[3])
            row.max_value_mined = float(item[4])
            row.max_value_txid = get_max_value_mined_txid(item[4], season)
            row.last_mined_blocktime = int(item[5])
            row.last_mined_block = int(item[6])
            row.update()
            if row.name in season_notaries:
                season_notaries.remove(row.name)

    for remaining_notary in season_notaries:
        row = season_mined_count_row()
        row.address = lib_helper.get_address_from_notary(season, remaining_notary, "KMD")
        row.blocks_mined = 0
        row.season = season
        row.sum_value_mined = 0
        row.max_value_mined = 0
        row.max_value_txid = ''
        row.last_mined_blocktime = 0
        row.last_mined_block = 0
        row.update()


# TODO: this should update, not clear
def update_known_address(address):

    sql = f"SELECT block_height, block_time, block_datetime, value, address, name, txid, season \
            FROM mined WHERE name='{address}' OR name='{address}' ORDER BY block_height;"
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    
    row = season_mined_count_row()
    row.address = address
    row.delete_address()
    row.name = address
    row.delete_name()

    row = mined_row()
    row.name = address
    row.delete_name()
    row.address = address
    row.delete_address()

'''
# DEPRECATE LATER (unused?)

def get_daily_mined_counts(day):
    result = 0
    results = get_mined_date_aggregates(day)
    time_stamp = int(time.time())
    for item in results:
        row = daily_mined_count_row()
        row.notary = item[0]
        if row.notary in KNOWN_NOTARIES:
            row.blocks_mined = int(item[1])
            row.sum_value_mined = float(item[2])
            row.mined_date = str(day)
            row.update()
    return result
    
'''