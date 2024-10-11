#!/usr/bin/env python3.12
import os
import sys
import json
import time
import random
from typing import List, Dict, Optional
from decimal import *
from datetime import datetime as dt
import datetime
from const_seasons import SEASONS_INFO, get_season_from_ts
from lib_const import *
from decorators import *
from models import mined_row, daily_mined_count_row, season_mined_count_row
from lib_query import *
import lib_api as api
import lib_validate
import lib_helper
from logger import logger

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


def update_mined_rows(rescan_blocks: List[int], coin: str = "KMD", prices: Optional[Dict] = None):
    if prices is None:
        prices = {}
    
    def format_date(timestamp: int) -> str:
        """Helper function to format the date."""
        return dt.utcfromtimestamp(timestamp).strftime('%d-%m-%Y')

    def fetch_block_info(block: int, coin: str) -> dict:
        """Fetch block info from the RPC."""
        try:
            return RPC[coin].getblock(str(block), 2)
        except Exception as e:
            logger.error(f"Error fetching block info for block {block}: {e}")
            return {}

    def fetch_and_update_prices(season: str, date: str) -> None:
        """Fetch prices from the API and update the prices dictionary."""
        if season not in prices:
            prices[season] = {}

        if date not in prices[season]:
            api_prices = api.get_kmd_price(date)
            if api_prices:
                logger.info(f"Fetched prices for {date}: {api_prices}")
                prices[season][date] = api_prices
            else:
                logger.warning(f"No prices available for {date}, setting default values.")
                prices[season][date] = {"btc": 0, "usd": 0}

            time.sleep(1)  # Adjust this based on the API rate limits

    def process_block(block: int) -> None:
        """Process individual block."""
        row = mined_row()
        blockinfo = fetch_block_info(block, coin)
        if not blockinfo:
            return
        
        row.block_time = blockinfo['time']
        row.diff = blockinfo['difficulty']
        row.block_height = block
        
        season = get_season_from_ts(row.block_time)['season']
        date = format_date(row.block_time)

        logger.info(f"Processing block {block} from {season} on {date}")

        fetch_and_update_prices(season, date)

        # Set price in row
        row.usd_price = Decimal(prices[season][date].get('usd', 0))
        row.btc_price = Decimal(prices[season][date].get('btc', 0))

        row = get_mined_row(row, blockinfo['tx'], coin, prices)
        if row.address not in ['', 'N/A']:
            row.update()

    # Main loop through blocks
    for block in rescan_blocks:
        process_block(block)

    # Save updated prices history
    with open(f"{script_path}/prices_history.json", "w+") as j:
        json.dump(prices, j, indent=4)



@print_runtime
def update_mined_table(season, coin="KMD", start_block=None):

    tip = int(RPC[coin].getblockcount())
    if not start_block:
        start_block = tip - 15000

    logger.info(f"Checking mined blocks {start_block} - {tip}")
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
        logger.info(e)
        prices = {}
    update_mined_rows(rescan_blocks, "KMD", prices)


@print_runtime
def update_mined_count_daily_table(season, rescan=None, since_genesis=False):

    try:
        with open(f"{script_path}/prices_history.json", "r") as j:
            prices = json.load(j)
    except Exception as e:
        logger.info(e)
        prices = {}

    if season != "since_genesis":
        season_notaries = SEASONS_INFO[season]["notaries"]
        season_start_dt = dt.fromtimestamp(SEASONS_INFO[season]["start_time"], datetime.UTC)
        start = season_start_dt.date()
    else:
        start = datetime.date(2016, 9, 13)

    end = datetime.date.today()
    delta = datetime.timedelta(days=1)
    now = int(time.time())

    if not rescan:
        start = end - datetime.timedelta(days=3)

    logger.info(f"[process_mined_aggregates] Aggregating daily mined counts from {start} to {end}")
    logger.info(f"[process_mined_aggregates] Aggregating daily mined counts from {start} to {end}")

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
