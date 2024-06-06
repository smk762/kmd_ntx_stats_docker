#!/usr/bin/env python3
import os
import sys
import json
import time
import random
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

def get_mined_row(row, block_tx, coin="KMD", prices=None):
    for tx in block_tx:
        if len(tx['vin']) > 0:
            if 'coinbase' in tx['vin'][0]:

                if 'addresses' in tx['vout'][0]['scriptPubKey']:
                    address = tx['vout'][0]['scriptPubKey']['addresses'][0]
                else:
                    address = "N/A"

                row.address = address
                row.txid = tx['txid']
                row.value = Decimal(tx['vout'][0]['value'])
    return row


def update_mined_rows(rescan_blocks, coin="KMD", prices=None):
    for block in rescan_blocks:
        row = mined_row()
        blockinfo = RPC[coin].getblock(str(block), 2)
        row.block_time = blockinfo['time']
        row.diff = blockinfo['difficulty']
        row.block_height = block

        season = lib_validate.get_season(row.block_time)
        date = f"{dt.utcfromtimestamp(row.block_time)}".split(" ")[0]
        date = date.split("-")
        date.reverse()
        date = "-".join(date)
        print(date)
        print(season)
        #print(prices)

        if season not in prices:
            prices.update({season: {}})

        if f"{date}" not in prices[season]:
            prices[season].update({f"{date}": {}})

        if 'btc' not in prices[season][f"{date}"]:
            api_prices = api.get_kmd_price(date)
            if api_prices:
                price_updated = True
                if "btc" in api_prices:
                    prices[season][f"{date}"].update(api_prices)
                    print(prices[season][f"{date}"])
                #print(prices[season][f"{date}"])
                time.sleep(1)
            else:
                prices[season][f"{date}"].update({"btc":0,"usd":0})

        #print(prices[season][date])
        if 'usd' in prices[season][date]:
            row.usd_price = Decimal(prices[season][date]['usd'])
        if 'btc' in prices[season][date]:
            row.btc_price = Decimal(prices[season][date]['btc'])

        row = get_mined_row(row, blockinfo['tx'], coin, prices)
        if row.address not in ['', 'N/A']:
            row.update()

    with open(f"{script_path}/prices_history.json", "w+") as j:
        json.dump(prices, j, indent=4)


@print_runtime
def update_mined_table(season, coin="KMD", start_block=None):

    tip = int(RPC[coin].getblockcount())
    if not start_block:
        start_block = tip - 150

    all_blocks = [*range(1,tip,1)]
    recorded_blocks = [block[0] for block in select_from_table('mined', 'block_height')]
    unrecorded_blocks = set(all_blocks) - set(recorded_blocks)
    rescan_blocks = list(set(list(unrecorded_blocks)))
    random.shuffle(rescan_blocks)
    logger.info(f"[update_mined_table] {len(recorded_blocks)} in mined table in db")
    logger.info(f"[update_mined_table] {len(unrecorded_blocks)} not in mined table in db")
    logger.info(f"[update_mined_table] {len(rescan_blocks)} blocks to scan")

    try:
        with open(f"{script_path}/prices_history.json", "r") as j:
            prices = json.load(j)
    except Exception as e:
        print(e)
        prices = {}
    update_mined_rows(rescan_blocks, "KMD", prices)


@print_runtime
def update_mined_count_daily_table(season, rescan=None, since_genesis=False):

    try:
        with open(f"{script_path}/prices_history.json", "r") as j:
            prices = json.load(j)
    except Exception as e:
        print(e)
        prices = {}

    if season != "since_genesis":
        season_notaries = SEASONS_INFO[season]["notaries"]
        season_start_dt = dt.utcfromtimestamp(SEASONS_INFO[season]["start_time"])
        start = season_start_dt.date()
    else:
        start = datetime.date(2016, 9, 13)

    end = datetime.date.today()
    delta = datetime.timedelta(days=1)
    now = int(time.time())

    if not rescan:
        start = end - datetime.timedelta(days=30)

    logger.info(f"[process_mined_aggregates] Aggregating daily mined counts from {start} to {end}")
    print(f"[process_mined_aggregates] Aggregating daily mined counts from {start} to {end}")

    while start <= end:
        date = f"{start}".split("-")
        date.reverse()
        date = "-".join(date)

        if season not in prices:
            prices.update({season: {}})

        if f"{date}" not in prices[season]:
            prices[season].update({f"{date}": {}})

        if 'btc' not in prices[season][f"{date}"]:
            api_prices = api.get_kmd_price(date)
            if api_prices:
                prices[season][f"{date}"].update(api_prices)
                time.sleep(1)
            else:
                prices[season][f"{date}"].update({"btc":0,"usd":0})

        logger.info(f"[process_mined_aggregates] Aggregating daily mined counts for {start}")
        results = get_mined_date_aggregates(start)

        for item in results:
            if len(item) > 0:
                row = daily_mined_count_row()
                row.notary = item[0]
                row.blocks_mined = int(item[1])
                row.sum_value_mined = float(item[2])
                row.mined_date = start
                row.timestamp = dt(*start.timetuple()[:-4]).timestamp()

                if season != "since_genesis":
                    row.usd_price = Decimal(prices[season][date]['usd'])
                    row.btc_price = Decimal(prices[season][date]['btc'])

                row.update()
                if season != "since_genesis":
                    if row.notary in season_notaries:
                        season_notaries.remove(row.notary)

        # For early season so notaries not mined yet are included.
        if season != "since_genesis":
            for remaining_notary in season_notaries:
                row = daily_mined_count_row()
                row.notary = remaining_notary
                row.blocks_mined = 0
                row.sum_value_mined = 0
                row.mined_date = start
                row.timestamp = now
                row.update()

        start += delta

    logger.info("[process_mined_aggregates] Finished!")
    with open(f"{script_path}/prices_history.json", "w+") as j:
        json.dump(prices, j, indent=4)


#Todo: calc YTD mined btc/usd value
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
    timestamp = int(time.time())
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
