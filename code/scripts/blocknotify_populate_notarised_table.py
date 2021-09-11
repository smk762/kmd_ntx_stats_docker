#!/usr/bin/env python
from cron_populate_notarised_table import *

TIP = int(RPC["KMD"].getblockcount())

for season in SEASONS_INFO:
    if season not in EXCLUDED_SEASONS:
        if 'post_season_end_time' in SEASONS_INFO[season]:
            sql = f"UPDATE notarised SET epoch = 'Unofficial' WHERE season = '{season}' \
                    AND block_time >= {SEASONS_INFO[season]['end_time']} \
                    AND block_time <= {SEASONS_INFO[season]['post_season_end_time']};"
            print(sql)
            CURSOR.execute(sql)
            CONN.commit()

        start = time.time()
        scan_rpc_for_ntx(season, TIP, True)
        end = time.time()
        logger.info(f">>> {end-start} sec to complete [scan_rpc_for_ntx({season})]")

CURSOR.close()
CONN.close()