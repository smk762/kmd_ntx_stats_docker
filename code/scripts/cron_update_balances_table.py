#!/usr/bin/env python3.12
from lib_const import *
from const_seasons import SEASONS_INFO, EXCLUDED_SEASONS
from lib_wallet import get_balances, delete_stale_balances
import lib_helper as helper

'''
This script checks notary balances for all dpow coins via electrum servers
It should be run as a cronjob every hour or so (takes about an 10 min to run).
'''

if __name__ == "__main__":

    delete_stale_balances()
    seasons = helper.get_active_seasons()
    print(f"Active Seasons: {seasons}")
    for season in ['Season_8']: # seasons:
        
        get_balances(season)

    CURSOR.close()
    CONN.close()
