#!/usr/bin/env python3
import sys
import lib_epochs
from lib_const import *
from decorators import print_runtime

# TODO: I dont think this will initialise s5 coins until they have recieved a notarisation. 
# Should probably augment with dpow readme parsing.

@print_runtime
def populate_epochs():

    if CLEAN_UP:
        lib_epochs.delete_invalid_seasons()
        lib_epochs.delete_invalid_servers()

    for season in SEASONS_INFO:
        if season not in EXCLUDED_SEASONS:
            if CLEAN_UP:
                lib_epochs.delete_invalid_season_servers(season)

                for server in SEASONS_INFO[season]["servers"]:
                    lib_epochs.delete_invalid_season_server_coins(season, server)

            lib_epochs.update_tenure(season)
            lib_epochs.update_epochs(season)

    lib_epochs.update_notarised_epoch_scoring()


    CURSOR.close()
    CONN.close()


if __name__ == "__main__":

    if len(sys.argv) > 1:
        if sys.argv[1] == "clean":
            CLEAN_UP = True

    populate_epochs()