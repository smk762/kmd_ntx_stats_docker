#!/usr/bin/env python3
from decorators import *
from lib_const import *
from lib_epochs import *

# TODO: I dont think this will initialise s5 coins until they have recieved a notarisation. 
# Should probably augment with dpow readme parsing.

@print_runtime
def populate_epochs():

    if CLEAN_UP:
        delete_invalid_seasons()
        delete_invalid_servers()

    for season in SEASONS_INFO:
        if season not in EXCLUDED_SEASONS:
            if season not in EXCLUDED_SEASONS:
                if CLEAN_UP:
                    delete_invalid_season_servers(season)
                for server in SCORING_EPOCHS[season]:
                    if CLEAN_UP:
                        delete_invalid_season_server_chains(season, server)
                update_tenure(season)
                update_epochs(season)

    update_notarised_epoch_scoring()

    CURSOR.close()
    CONN.close()


if __name__ == "__main__":

    if len(sys.argv) > 1:
        if sys.argv[1] == "clean":
            CLEAN_UP = True

    populate_epochs()