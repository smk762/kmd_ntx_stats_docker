#!/usr/bin/env python3
import random
from lib_const import *
from decorators import *
from lib_helper import get_season_notaries
from lib_ntx import import_ntx
from lib_query import get_notarised_servers, get_notarised_coins


@print_runtime
def import_notarised():
    for season in SEASONS_INFO:
        if season not in EXCLUDED_SEASONS: 

            season_notaries = get_season_notaries(season)
            servers = get_notarised_servers(season)

            while len(servers) > 0:
                server = random.choice(servers)
                servers.remove(server)
                coins = get_notarised_coins(season, server)

                i = 0
                while len(coins) > 0:
                    i += 1
                    coin = random.choice(coins)
                    coins.remove(coin)
                    logger.info(f">>> Importing {coin} for {season} {server} ({i} processed, {len(coins)} remaining)")
                    import_ntx(season, server, coin)

if __name__ == "__main__":

    import_notarised()
    CURSOR.close()
    CONN.close()


                    
