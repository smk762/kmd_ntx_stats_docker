#!/usr/bin/env python3
import sys
from lib_const import SEASONS_INFO, EXCLUDED_SEASONS
from lib_helper import is_postseason
from decorators import print_runtime
from lib_ntx import *

'''
This script scans the blockchain for notarisation txids that are not already recorded in the database.
After updaing the "notarised" table, aggregations are performed to get counts for notaries and coins within each season.
It is intended to be run as a cronjob every 15-30 min
Script runtime is around 5-10 mins, except for initial population which is up to 1 day per season
'''

@print_runtime
def update_ntx_tables(rescan=False):
    # Uncomment if record contains address rather than notary in [notaries] list (e.g. saved before pubkeys updated)
    for season in SEASONS_INFO:
        if season not in EXCLUDED_SEASONS:
            logger.info(f"Updating notarisations for {season}")

            update_notarised_table(season, rescan)                      # 35 sec runtime

            if CLEAN_UP:                            
                clean_up_notarised_table(season)                        # approx. 2 min per day
                update_notarised_count_daily_table(season, CLEAN_UP)    # 20 sec
                update_notarised_coin_daily_table(season, CLEAN_UP)    # 20 sec
            else:
                update_notarised_count_daily_table(season, rescan)      # 20 sec
                update_notarised_coin_daily_table(season, rescan)      # 20 sec

            update_notarised_count_season_table(season)                 # 60 sec runtime
            update_notarised_coin_season_table(season)                 # 5 sec
            update_last_notarised_table(season)

if __name__ == "__main__":

    # Rescan will check chain for data since season start
    # Clean will recalculate data existing in table
    if len(sys.argv) > 1:
        if sys.argv[1] == "rescan":
            RESCAN_SEASON = True
        elif sys.argv[1] == "clean":
            CLEAN_UP = True

    update_ntx_tables(RESCAN_SEASON)

