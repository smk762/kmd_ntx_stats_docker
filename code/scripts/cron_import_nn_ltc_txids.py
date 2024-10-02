#!/usr/bin/env python3.12
from lib_const import *
from lib_ntx import import_nn_ltc_txids

if __name__ == "__main__":

    for season in ["Season_8"]:
        
            import_nn_ltc_txids(season)
