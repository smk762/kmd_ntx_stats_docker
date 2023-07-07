#!/usr/bin/env python3
from lib_const import *
from lib_ntx import import_nn_ltc_txids

if __name__ == "__main__":

    for season in ["Season_7"]:
        
            import_nn_ltc_txids(season)
