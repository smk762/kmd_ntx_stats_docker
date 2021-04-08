#!/usr/bin/env python3
import time
import logging
import logging.handlers
from datetime import datetime as dt
import datetime
from decimal import Decimal

from lib_const import *
from lib_table_select import select_from_table, get_season_mined_counts, get_mined_date_aggregates, get_notarised_seasons
from models import season_mined_count_row, daily_mined_count_row, mined_row, get_season_from_block


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s',
                              datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


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

def update_mined_known_address(address):
    sql = f"SELECT block_height, block_time, block_datetime, value, address, name, txid, season FROM mined WHERE address = '{address}';"
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    for result in results:
        if result[4] in NON_NOTARY_ADDRESSES:
            row = mined_row()
            row.block_height = result[0]
            row.block_time = result[1]
            row.block_datetime = result[2]
            row.value = result[3]
            row.address = result[4]
            row.name = NON_NOTARY_ADDRESSES[row.address]
            row.txid = result[6]
            row.season = get_season_from_block(row.block_height)
            row.update()
            logger.info(f"Updating, address {row.address} as {row.name}")
        else:
            logger.info(f"Not updating, address {row.address} not in NON_NOTARY_ADDRESSES")


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
    logger.info(f"{len(recorded_blocks)} in mined table in db")

    all_blocks = [*range(start_block,tip,1)]    
    unrecorded_blocks = set(all_blocks) - set(recorded_blocks)
    logger.info(f"{len(unrecorded_blocks)} not in mined table in db")

    if not RESCAN_SEASON:
        rescan_blocks = [*range(tip-100,tip,1)]
    else:
        rescan_blocks = [*range(start_block,tip,1)]

    rescan_blocks = list(set(list(unrecorded_blocks) + rescan_blocks))
    logger.info(f"{len(rescan_blocks)} blocks to scan")

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
        start = end - datetime.timedelta(days=7)

    delta = datetime.timedelta(days=1)
    logger.info("Aggregating daily mined counts from "+str(start)+" to "+str(end))
    day = start

    time_stamp = int(time.time())
    while day <= end:
        logger.info(f"Aggregating daily mined counts for {day}")
        results = get_mined_date_aggregates(day)
        logger.info(f"get_mined_date_aggregates results for {day}: {len(results)}")
        for item in results:
            if len(item) > 0:
                row = daily_mined_count_row()
                logger.info(item)
                row.notary = item[0]
                row.blocks_mined = int(item[1])
                row.sum_value_mined = float(item[2])
                row.mined_date = day
                row.time_stamp = time_stamp
                logger.info(f"{day} {row.notary} {row.blocks_mined} {row.sum_value_mined}")
                row.update()
        day += delta
    logger.info("Finished!")


def update_season_mined_counts(season):
    results = get_season_mined_counts(season, POSTSEASON)

    for item in results:
        row = season_mined_count_row()
        row.notary = item[0]
        row.address = item[1]
        row.season = season
        row.blocks_mined = int(item[2])
        row.sum_value_mined = float(item[3])
        row.max_value_mined = float(item[4])
        row.last_mined_blocktime = int(item[5])
        row.last_mined_block = int(item[6])
        row.update()


if __name__ == "__main__":

    RESCAN_SEASON = False
    scan_depth = 100
    seasons = get_notarised_seasons()

    # Uncomment to update addresses in DB after updating NON_NOTARY_ADDRESSES
    # for address in NON_NOTARY_ADDRESSES:
    #   update_mined_known_address(address)

    for season in seasons:

        if season not in EXCLUDED_SEASONS:

            if season.find("Testnet") == -1:

                update_mined_blocks(season)

                update_season_mined_counts(season)

                process_aggregates(season)
