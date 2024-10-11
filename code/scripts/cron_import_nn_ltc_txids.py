#!/usr/bin/env python3.12
import lib_db
import lib_helper as helper
from lib_ntx import import_nn_txids

if __name__ == "__main__":

    seasons = helper.get_active_seasons()
    for season in seasons:
        import_nn_txids(season, "LTC")
    lib_db.CURSOR.close()
    lib_db.CONN.close()
