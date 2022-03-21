#!/usr/bin/env python3
import random
from lib_const import *
from decorators import *
from lib_helper import get_season_notaries
from lib_notarisation import import_ntx
from lib_table_select import get_notarised_servers, get_notarised_chains


@print_runtime
def import_notarised():
    for season in SEASONS_INFO:
        if season not in EXCLUDED_SEASONS: 

            season_notaries = get_season_notaries(season)
            servers = get_notarised_servers(season)

            while len(servers) > 0:
                server = random.choice(servers)
                servers.remove(server)
                chains = get_notarised_chains(season, server)

                i = 0
                while len(chains) > 0:
                    i += 1
                    chain = random.choice(chains)
                    chains.remove(chain)
                    logger.info(f">>> Importing {chain} for {season} {server} ({i} processed, {len(chains)} remaining)")
                    import_ntx(season, server, chain)

if __name__ == "__main__":

    import_notarised()
    CURSOR.close()
    CONN.close()


                    
