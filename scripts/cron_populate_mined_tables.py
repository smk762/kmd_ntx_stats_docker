#!/usr/bin/env python3
import time
import logging
import logging.handlers
from datetime import datetime as dt
import datetime

from lib_const import SEASONS_INFO, SKIP_PAST_SEASONS, SKIP_UNTIL_YESTERDAY, RPC
from lib_table_select import select_from_table, get_season_mined_counts
from lib_notary import get_season, update_miner, get_season_notaries, get_daily_mined_counts
from models import season_mined_count_row

logger = logging.getLogger()
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

scan_depth = 100

season = get_season(int(time.time()))


def update_mined_blocks(season):

    # re-check last ten recorded blocks in case of orphans
    tip = int(RPC["KMD"].getblockcount())
    start_block = SEASONS_INFO[season]["start_block"]
    scan_blocks = [*range(tip-100,tip,1)]
    all_blocks = [*range(start_block,tip,1)]

    # adding new blocks...
    start = time.time()
    existing_blocks = select_from_table('mined', 'block_height')

    recorded_blocks = []
    for block in existing_blocks:
        recorded_blocks.append(block[0])

    logger.info(f"{len(existing_blocks)} in mined table in db")
    
    unrecorded_blocks = set(all_blocks) - set(recorded_blocks)
    logger.info(f"{len(unrecorded_blocks)} not in mined table in db")

    scan_blocks = list(set(list(unrecorded_blocks) + scan_blocks))
    logger.info(f"{len(scan_blocks)} blocks to scan")

    time.sleep(4)
    for block in scan_blocks:
        if block >= start_block:
            update_miner(block)


if SKIP_PAST_SEASONS:
    update_mined_blocks(season)

    season_notaries = get_season_notaries(season)
    results = get_season_mined_counts(season, season_notaries)

    for item in results:
        row = season_mined_count_row()
        row.notary = item[0]
        row.season = season
        row.blocks_mined = int(item[1])
        row.sum_value_mined = float(item[2])
        row.max_value_mined = float(item[3])
        row.last_mined_blocktime = int(item[4])
        row.last_mined_block = int(item[5])
        row.update()

else:
    # updating season mined count aggregate table
    for season in SEASONS_INFO:
        update_mined_blocks(season)

        season_notaries = get_season_notaries(season)
        results = get_season_mined_counts(season, season_notaries)

        for item in results:
            row = season_mined_count_row()
            row.notary = item[0]
            row.season = season
            row.blocks_mined = int(item[1])
            row.sum_value_mined = float(item[2])
            row.max_value_mined = float(item[3])
            row.last_mined_blocktime = int(item[4])
            row.last_mined_block = int(item[5])
            row.update()

# updating daily mined count aggregate table

# start on date of most recent season
season_start_time = SEASONS_INFO[season]["start_time"]
season_start_dt = dt.fromtimestamp(season_start_time)
start = season_start_dt.date()
end = datetime.date.today()

if SKIP_UNTIL_YESTERDAY:
    start = end - datetime.timedelta(days=7)

delta = datetime.timedelta(days=1)
logger.info("Aggregating daily mined counts from "+str(start)+" to "+str(end))
day = start

while day <= end:
    
    get_daily_mined_counts(day)
    day += delta
logger.info("Finished!")
