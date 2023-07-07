#!/usr/bin/env python3
import random
from lib_const import *
from decorators import *
import lib_helper as helper
import lib_ntx


@print_runtime
def import_notarised():
    for season in ["Season_7"]:
        
            season_notaries = helper.get_season_notaries(season)
            ntx_tbl = lib_ntx.notarised(season)
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

    import_notarised()
    CURSOR.close()
    CONN.close()
