#!/usr/bin/env python3
from lib_const import *
from lib_helper import has_season_started
from lib_mining import update_mined_table, update_mined_count_daily_table, update_mined_count_season_table
from decorators import print_runtime

''' 
Script for updating mining related databases
Cronjob frequency: 2 min
Tables updated:
    - mined
    - mined_count_daily
    - mined_count_season
'''

@print_runtime
def run_updates():
    for season in SEASONS_INFO:
        if season not in EXCLUDED_SEASONS:
            if season.find("Testnet") == -1:
                if has_season_started(season):
                    if RESCAN_SEASON:
                        update_mined_table(season, "KMD", SEASONS_INFO[season]["start_block"])
                        update_mined_count_daily_table(season, True)
                    else:
                        update_mined_table(season)
                        update_mined_count_daily_table(season)
                    update_mined_count_season_table(season)

if __name__ == "__main__":

    if len(sys.argv) > 1:
        if sys.argv[1] == "rescan":
            RESCAN_SEASON = True

    run_updates()