#!/usr/bin/env python3.12
from decorators import print_runtime
import lib_ntx

'''
Run after season ends to ensure full ntx coverage
and epoch scores alignment. Runtime 4-5hrs.
'''

@print_runtime
def rescan_season(season="Season_8"):
    notarised_table = lib_ntx.Notarised(season, rescan=True)
    # Revalidates existing data, run after epoch changes to correct the scores.
    notarised_table.clean_up()
    # Scan all season blocks for missing txids
    notarised_table.update_table()
    
    ntx_season_tables = lib_ntx.NtxSeasonStats(season)
    # Deletes all season ntx aggregate data for a clean slate
    ntx_season_tables.clean_up()
    # Recalculates season ntx aggregate data
    ntx_season_tables.update_ntx_season_stats_tables()
    
    ntx_daily_tables = lib_ntx.NtxDailyStats(season, rescan=True)
    # Recalculate all daily ntx stats data
    ntx_daily_tables.update_daily_ntx_tables()

if __name__ == "__main__":
    rescan_season()
