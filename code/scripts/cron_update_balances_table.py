#!/usr/bin/env python3
from lib_const import *
from lib_wallet import get_balances, delete_stale_balances

'''
This script checks notary balances for all dpow coins via electrum servers
It should be run as a cronjob every hour or so (takes about an 10 min to run).
'''

if __name__ == "__main__":

    delete_stale_balances()
    
    for season in SEASONS_INFO:
        if season in EXCLUDED_SEASONS:
            logger.warning(f"Skipping season: {season}")
        else:
            get_balances(season)

    CURSOR.close()
    CONN.close()
