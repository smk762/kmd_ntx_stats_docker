#!/usr/bin/env python3
from lib_const import *
from lib_notarisation import import_nn_ltc_txids

if __name__ == "__main__":

    for season in SEASONS_INFO:
        if season not in EXCLUDED_SEASONS: 
            import_nn_ltc_txids(season)
