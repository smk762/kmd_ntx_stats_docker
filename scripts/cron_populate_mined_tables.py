#!/usr/bin/env python3
import time
from datetime import datetime as dt
import datetime
from decimal import Decimal

from lib_const import *
from lib_table_select import select_from_table, get_season_mined_counts, get_mined_date_aggregates, get_notarised_seasons, get_max_value_mined_txid
from models import season_mined_count_row, daily_mined_count_row, mined_row, get_season_from_block
from lib_helper import has_season_started

''' 
This script is intended to run as a cronjob every 5-15 minutes.
It rescans the last 100 blocks in the database
(configurable with "scan_depth" variable) to realign potential
orphaned blocks in the database.
Next, it retrieves info from the block chain for blocks not yet
in the database and updates the mined table.
Lastly, it updates the mined_count_season and mined_count_daily
tables with aggregated stats for each notary season.
'''

def clear_known_address(address):

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

def update_miner(block):
    blockinfo = RPC["KMD"].getblock(str(block), 2)
    for tx in blockinfo['tx']:
        if len(tx['vin']) > 0:
            if 'coinbase' in tx['vin'][0]:
                if 'addresses' in tx['vout'][0]['scriptPubKey']:
                    address = tx['vout'][0]['scriptPubKey']['addresses'][0]
                    if address in KNOWN_ADDRESSES:
                        name = KNOWN_ADDRESSES[address]
                    else:
                        name = address
                else:
                    address = "N/A"
                    name = "non-standard"

                row = mined_row()
                row.block_height = block
                row.block_time = blockinfo['time']
                row.block_datetime = dt.utcfromtimestamp(blockinfo['time'])
                row.address = address
                row.name = name
                row.txid = tx['txid']
                row.season = get_season_from_block(block)
                row.value = Decimal(tx['vout'][0]['value'])
                row.update()


def update_mined_blocks(season):

    # re-check last ten recorded blocks in case of orphans
    tip = int(RPC["KMD"].getblockcount())
    start_block = SEASONS_INFO[season]["start_block"]
    existing_blocks = select_from_table('mined', 'block_height')

    recorded_blocks = []
    for block in existing_blocks:
        recorded_blocks.append(block[0])
    logger.info(f"[update_mined_blocks] {len(recorded_blocks)} in mined table in db")

    all_blocks = [*range(start_block,tip,1)]    
    unrecorded_blocks = set(all_blocks) - set(recorded_blocks)
    logger.info(f"[update_mined_blocks] {len(unrecorded_blocks)} not in mined table in db")

    if not RESCAN_SEASON:
        rescan_blocks = [*range(tip-100,tip,1)]
    else:
        rescan_blocks = [*range(start_block,tip,1)]

    rescan_blocks = list(set(list(unrecorded_blocks) + rescan_blocks))
    logger.info(f"[update_mined_blocks] {len(rescan_blocks)} blocks to scan")

    time.sleep(4)
    for block in rescan_blocks:
        if block >= start_block:
            update_miner(block)


# updating daily mined count aggregate table
def process_aggregates(season):

    season_start_time = SEASONS_INFO[season]["start_time"]
    season_start_dt = dt.fromtimestamp(season_start_time)
    start = season_start_dt.date()
    end = datetime.date.today()

    if SKIP_UNTIL_YESTERDAY and not RESCAN_SEASON:
        start = end - datetime.timedelta(days=20)

    delta = datetime.timedelta(days=1)
    logger.info(f"[process_aggregates] Aggregating daily mined counts from {start} to {end}")
    day = start

    season_notaries = list(NOTARY_PUBKEYS[season].keys())
    time_stamp = int(time.time())
    while day <= end:
        logger.info(f"[process_aggregates] Aggregating daily mined counts for {day}")
        results = get_mined_date_aggregates(day)


        for item in results:
            if len(item) > 0:
                row = daily_mined_count_row()
                row.notary = item[0]
                row.blocks_mined = int(item[1])
                row.sum_value_mined = float(item[2])
                row.mined_date = day
                row.time_stamp = time_stamp
                row.update()
                if row.notary in season_notaries:
                    season_notaries.remove(row.notary)

        # Handle where notary has not mined on this day
        for remaining_notary in season_notaries:
            row = daily_mined_count_row()
            row.notary = remaining_notary
            row.blocks_mined = 0
            row.sum_value_mined = 0
            row.mined_date = day
            row.time_stamp = time_stamp
            row.update()

        day += delta
    logger.info("[process_aggregates] Finished!")


def update_season_mined_counts(season):

    results = get_season_mined_counts(season)

    for item in results:
        row = season_mined_count_row()
        row.name = item[0]
        row.address = item[1]
        row.season = season
        row.blocks_mined = int(item[2])
        if row.address in KNOWN_ADDRESSES or row.blocks_mined > 25:
            max_value_txid = get_max_value_mined_txid(item[4])
            row.sum_value_mined = float(item[3])
            row.max_value_mined = float(item[4])
            row.max_value_txid = max_value_txid
            row.last_mined_blocktime = int(item[5])
            row.last_mined_block = int(item[6])
            row.update()


if __name__ == "__main__":

    RESCAN_SEASON = False
    scan_depth = 100
    start = time.time()
    seasons = get_notarised_seasons()
    end = time.time()
    logger.info(f">>> {end-start} sec to complete [get_notarised_seasons()]")

    # Uncomment to update addresses in DB after updating NON_NOTARY_ADDRESSES
    '''
    for address in NON_NOTARY_ADDRESSES:
        logger.info(f"updating {address}")
        clear_known_address(address)
    '''

    for season in seasons:

        if season not in EXCLUDED_SEASONS:

            if season.find("Testnet") == -1:
                if has_season_started(season):
                    start = end
                    update_mined_blocks(season)
                    end = time.time()
                    logger.info(f">>> {end-start} sec to complete [update_mined_blocks({season})]")

                    start = end
                    update_season_mined_counts(season)
                    end = time.time()
                    logger.info(f">>> {end-start} sec to complete [update_season_mined_counts({season})]")

                    start = end
                    process_aggregates(season)
                    end = time.time()
                    logger.info(f">>> {end-start} sec to complete [process_aggregates({season})]")

