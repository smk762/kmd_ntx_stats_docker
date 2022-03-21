#!/usr/bin/env python3
import time
from decimal import *
from datetime import datetime as dt
import datetime
from lib_rpc import *
from lib_const import *
from lib_helper import *
from decorators import *
from models import mined_row, daily_mined_count_row, season_mined_count_row
from lib_table_select import select_from_table, get_mined_date_aggregates, get_max_value_mined_txid


def get_mined_row(block_height, chain="KMD"):
    row = mined_row()
    blockinfo = RPC[chain].getblock(str(block_height), 2)

    for tx in blockinfo['tx']:
        if len(tx['vin']) > 0:
            if 'coinbase' in tx['vin'][0]:
                if 'addresses' in tx['vout'][0]['scriptPubKey']:
                    address = tx['vout'][0]['scriptPubKey']['addresses'][0]
                    name = get_name_from_address(address)
                else:
                    address = "N/A"
                    name = "non-standard"

                row.block_height = block_height
                row.block_time = blockinfo['time']
                row.block_datetime = dt.utcfromtimestamp(blockinfo['time'])
                row.address = address
                row.name = name
                row.txid = tx['txid']
                row.diff = blockinfo['difficulty']
                row.season = get_season_from_block(block_height)
                row.value = Decimal(tx['vout'][0]['value'])
                break
    return row


def update_mined_row(block_height, chain="KMD"):
    row = get_mined_row(block_height, chain)
    if row.address not in ['', 'N/A']:
        row.update()


@print_runtime
def update_mined_table(season, chain="KMD"):

    tip = int(RPC[chain].getblockcount())
    start_block = tip-10   

    all_blocks = [*range(start_block,tip,1)] 
    recorded_blocks = [block[0] for block in select_from_table('mined', 'block_height')]
    unrecorded_blocks = set(all_blocks) - set(recorded_blocks)
    
    if RESCAN_SEASON:
        start_block = SEASONS_INFO[season]["start_block"]
    rescan_blocks = list(set(list(unrecorded_blocks) + [*range(start_block,tip,1)]))

    logger.info(f"[update_mined_table] {len(recorded_blocks)} in mined table in db")
    logger.info(f"[update_mined_table] {len(unrecorded_blocks)} not in mined table in db")
    logger.info(f"[update_mined_table] {len(rescan_blocks)} blocks to scan")

    for block in rescan_blocks:
        update_mined_row(block)


@print_runtime
def update_mined_count_daily_table(season):

    season_notaries = get_season_notaries(season)
    season_start_dt = dt.fromtimestamp(SEASONS_INFO[season]["start_time"])
    start = season_start_dt.date()
    end = datetime.date.today()
    delta = datetime.timedelta(days=1)
    now = int(time.time())

    if not RESCAN_SEASON:
        start = end - datetime.timedelta(days=5)

    logger.info(f"[process_mined_aggregates] Aggregating daily mined counts from {start} to {end}")

    while start <= end:
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


@print_runtime
def update_mined_count_season_table(season):
    season_notaries = get_season_notaries(season)

    for item in get_season_mined_counts(season):

        if item[1] in KNOWN_ADDRESSES or row.blocks_mined > 25:
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
        row = daily_mined_count_row()
        row.address = get_address_from_notary(season, remaining_notary, "KMD")
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