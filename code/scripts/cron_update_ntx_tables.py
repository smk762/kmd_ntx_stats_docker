#!/usr/bin/env python3
import sys
from lib_const import *
from lib_helper import is_postseason
from decorators import print_runtime
import lib_ntx

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
        if season not in EXCLUDED_SEASONS or SCAN_ALL:
            logger.info(f"Updating notarisations for {season}")

            notarised_table = lib_ntx.notarised(season, rescan)
            if CLEAN_UP:                            
                notarised_table.clean_up(season)
                rescan = True
            notarised_table.update_table()

            ntx_daily_tables = lib_ntx.ntx_daily_stats(season, rescan)
            ntx_daily_tables.update_daily_ntx_tables()

            ntx_season_tables = lib_ntx.ntx_season_stats(season)
            if CLEAN_UP:                            
                ntx_season_tables.clean_up(season)
            ntx_season_tables.update_ntx_season_stats_tables()

            last_ntx_tables = lib_ntx.last_notarisations(season)
            last_ntx_tables.update_coin_table()
            last_ntx_tables.update_notary_table()

if __name__ == "__main__":

    # Rescan will check chain for data since season start
    # Clean will recalculate data existing in table
    SCAN_ALL = False
    CLEAN_UP = False
    RESCAN_SEASON = False
    if len(sys.argv) > 1:
        if "rescan" in sys.argv:
            RESCAN_SEASON = True
        elif "clean" in sys.argv:
            CLEAN_UP = True
        elif "all" in sys.argv:
            SCAN_ALL = True

    update_ntx_tables(RESCAN_SEASON)
