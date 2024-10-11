#!/usr/bin/env python3.12
import time
import random

import lib_db
import lib_ntx
import lib_helper as helper
from decorators import print_runtime
from const_seasons import get_season_from_ts
from logger import logger


@print_runtime
def import_notarised(season):
    ntx_tbl = lib_ntx.Notarised(season)
    servers = helper.get_season_servers(season)
    while len(servers) > 0:
        server = random.choice(servers)
        servers.remove(server)
        coins = helper.get_season_coins(season, server)

        i = 0
        while len(coins) > 0:
            i += 1
            coin = random.choice(coins)
            coins.remove(coin)
            logger.info(f">>> Importing {coin} for {season} {server} ({i} processed, {len(coins)} remaining)")
            ntx_tbl.import_ntx(server, coin)


if __name__ == "__main__":
    seasons = helper.get_active_seasons()
    for season in seasons:
        import_notarised(season)
    lib_db.CURSOR.close()
    lib_db.CONN.close()
