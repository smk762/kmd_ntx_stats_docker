#!/usr/bin/env python3.12
import sys
from lib_dpow_const import RESCAN_SEASON
from const_seasons import SEASONS
from lib_helper import get_active_seasons
from lib_mining import update_mined_table, update_mined_count_daily_table, update_mined_count_season_table
from decorators import print_runtime
from logger import logger

''' 
Script for updating mining related databases
Cronjob frequency: 2 min
Tables updated:
    - mined
    - mined_count_daily
    - mined_count_season
'''


@print_runtime
def run_updates(seasons):
    if seasons == "since_genesis":
        update_mined_table("since_genesis", "KMD", 1)
        update_mined_count_daily_table("since_genesis", True, True)
    else:
        for season in seasons:
            logger.info(f"Getting mined blocks for {season}")
            if RESCAN_SEASON:
                update_mined_table(season, "KMD", SEASONS.INFO[season]["start_block"])
                update_mined_count_daily_table(season, True)
            else:
                update_mined_table(season)
                update_mined_count_daily_table(season)
            update_mined_count_season_table(season)

if __name__ == "__main__":
    seasons = get_active_seasons()
    if len(sys.argv) > 1:
        if sys.argv[1] == "rescan":
            RESCAN_SEASON = True

        if sys.argv[1] == "all":
            seasons = SEASONS.INFO.keys()

        if sys.argv[1] == "since_genesis":
            seasons = "since_genesis"

    run_updates(seasons)
