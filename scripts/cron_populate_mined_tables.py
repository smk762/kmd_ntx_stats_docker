#!/usr/bin/env python3
import time
import logging
import logging.handlers
from datetime import datetime as dt
import datetime

from lib_const import SEASONS_INFO, SKIP_PAST_SEASONS, SKIP_UNTIL_YESTERDAY, RPC, POSTSEASON
from lib_table_select import select_from_table, get_season_mined_counts, get_mined_date_aggregates, get_notarised_seasons
from lib_notary import get_season, update_miner, get_season_notaries, get_daily_mined_counts
from models import season_mined_count_row, daily_mined_count_row


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

    if not rescan_season:
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

    if SKIP_UNTIL_YESTERDAY and not rescan_season:
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


if __name__ == "__main__":

    rescan_season = False
    scan_depth = 100
    seasons = get_notarised_seasons()

    for season in seasons:
        if season not in ["Season_1", "Season_2", "Season_3", "Unofficial"]: 

            update_mined_blocks(season)

            season_notaries = get_season_notaries(season)

            results = get_season_mined_counts(season, season_notaries, POSTSEASON)

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

            process_aggregates(season)