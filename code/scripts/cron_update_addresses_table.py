#!/usr/bin/env python3.12
import sys

from decorators import *
from lib_const import *
from lib_wallet import populate_addresses

'''
You should only need to run this once per season, unless notary pubkeys change
or coins with new params are added.
'''

@print_runtime
def update_adresses(seasons):
    if CLEAN_UP:
        CURSOR.execute(f"DELETE FROM addresses;")
        CONN.commit()

    for season in seasons:
        print(season)
        for server in SEASONS_INFO[season]['servers']:
            populate_addresses(season, server)

    CURSOR.close()
    CONN.close()


if __name__ == "__main__":
    seasons = [CURRENT_SEASON]
    if len(sys.argv) > 1:
        if sys.argv[1] == "clean":
            CLEAN_UP = True
        if sys.argv[1] == "all":
            season = SEASONS_INFO.keys()

    update_adresses(seasons)
