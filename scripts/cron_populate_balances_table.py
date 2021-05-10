#!/usr/bin/env python3
import time
import math
import lib_electrum
from lib_notary import get_season
import threading
from lib_const import *
from lib_table_select import get_notarised_seasons, get_notarised_servers, get_notarised_chains
from models import balance_row
from lib_electrum import get_balance
from base_58 import get_addr_from_pubkey

'''
This script checks notary balances for all dpow coins via electrum servers,
and any pending KMD rewards then stores data in db
It should be run as a cronjob every hour or so (takes about an 10 min to run).
'''

class electrum_thread(threading.Thread):
    def __init__(self, season, server, notary, coin, pubkey, address):
        threading.Thread.__init__(self)
        self.season = season
        self.server = server
        self.notary = notary
        self.chain = coin
        self.pubkey = pubkey
        self.address = address
    def run(self):
        thread_electrum(self.season, self.server, self.notary, self.chain, self.pubkey, self.address)

def thread_electrum(season, server, notary, coin, pubkey, address):
    balance = balance_row()
    balance.season = season
    balance.server = server
    balance.notary = notary
    balance.chain = coin
    balance.pubkey = pubkey
    balance.address = address

    balance.balance = get_balance(balance.chain, balance.pubkey, balance.address, balance.server)

    if balance.balance != -1:
        balance.update()

def get_balances(season):

    logger.warning(f"Processing season: {season}")
    season_main_coins = requests.get(f'{THIS_SERVER}/api/info/dpow_server_coins/?season={season}&server=Main').json()['results']
    season_3p_coins = requests.get(f'{THIS_SERVER}/api/info/dpow_server_coins/?season={season}&server=Third_Party').json()['results']
    logger.warning(f"season_main_coins: {season_main_coins}")
    logger.warning(f"season_3p_coins: {season_3p_coins}")

    if len(season_main_coins+season_3p_coins) > 0:
        thread_list = {}

        for pubkey_season in NOTARY_PUBKEYS:

            if pubkey_season.find(season) != -1:
                address_data = requests.get(f'{THIS_SERVER}/api/wallet/notary_addresses/?season={season}').json()

                if pubkey_season.find("Third_Party") != -1:
                    coins = season_3p_coins
                    server = "Third_Party"

                else:
                    coins = season_main_coins
                    server = "Main"

                coins += ["BTC", "KMD", "LTC"]
                coins.sort()
                
                for notary in NOTARY_PUBKEYS[pubkey_season]:
                    thread_list.update({notary:[]})

                    for coin in coins:
                        address = address_data[season][server][notary]["addresses"][coin]
                        pubkey = address_data[season][server][notary]["pubkey"]
                        thread_list[notary].append(electrum_thread(season, server, notary, coin, pubkey, address))

                    for thread in thread_list[notary]:
                        thread.start()
                        time.sleep(0.1) # 2 sec sleep = 8 min runtime.
                    time.sleep(2) # 2 sec sleep = 8 min runtime.


if __name__ == "__main__":

    logger.info(f"Preparing to populate [balances] table...")


    logger.info(f"Removing stale data...")
    logger.info(time.time())
    logger.info(time.time()-24*60*60)
    sql = f"DELETE FROM balances WHERE update_time < {time.time()-24*60*60};"
    logger.info(sql)
    CURSOR.execute(sql)
    CONN.commit()

    for season in SEASONS_INFO:
        if season in EXCLUDED_SEASONS:
            logger.warning(f"Skipping season: {season}")
        else:
            get_balances(season)
    CURSOR.close()
    CONN.close()
