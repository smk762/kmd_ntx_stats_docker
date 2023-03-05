#!/usr/bin/env python3
import sys
import lib_epochs
import lib_helper as helper
from lib_const import *
from decorators import print_runtime

# TODO: I dont think this will initialise s5 coins until they have recieved a notarisation. 
# Should probably augment with dpow readme parsing.

@print_runtime
def populate_epochs(season):

    if CLEAN_UP:
        lib_epochs.delete_invalid_seasons()
        lib_epochs.delete_invalid_servers()
        lib_epochs.delete_invalid_season_servers(season)

        for server in SEASONS_INFO[season]["servers"]:
            lib_epochs.delete_invalid_season_server_coins(season, server)

    lib_epochs.update_tenure(season)
    lib_epochs.update_epochs(season)

    lib_epochs.update_notarised_epoch_scoring(season)


    CURSOR.close()
    CONN.close()


if __name__ == "__main__":

    seasons = helper.get_active_seasons()
    if len(sys.argv) > 1:
        if sys.argv[1] == "clean":
            CLEAN_UP = True
        if sys.argv[1] == "rescan":
            seasons = SEASONS_INFO.keys()

    for season in seasons:
        if season not in EXCLUDED_SEASONS:
            populate_epochs(season)