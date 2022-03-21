#!/usr/bin/env python3
import sys

from decorators import *
from lib_const import *
from lib_wallet import populate_addresses

''' 
You should only need to run this once per season, unless notary pubkeys change
or coins with new params are added.
'''

@print_runtime
def update_adresses():
    # TODO: Populate Addresses for active coins not yet notarised.
    if CLEAN_UP:
        CURSOR.execute(f"DELETE FROM addresses;")
        CONN.commit()

    for season in SEASONS_INFO:
        if season not in EXCLUDED_SEASONS:
            for server in ["Main", "Third_Party"]:
                populate_addresses(season, server)

    CURSOR.close()
    CONN.close()


if __name__ == "__main__":
                
    if len(sys.argv) > 1:
        if sys.argv[1] == "clean":
            CLEAN_UP = True

    update_adresses()
