#!/usr/bin/env python3
import time
import json
from lib_const import *
from decorators import *
from lib_urls import *
from models import addresses_row
from lib_helper import get_pubkeys
from lib_threads import update_notary_balances_thread


@print_runtime
def get_balances(season):
    season_main_coins = requests.get(get_dpow_server_coins_url(season, 'Main')).json()['results']
    season_3p_coins = requests.get(get_dpow_server_coins_url(season, 'Third_Party')).json()['results']

    if len(season_main_coins+season_3p_coins) > 0:
        thread_list = {}

        for pubkey_season in NOTARY_PUBKEYS:

            if pubkey_season.find(season) != -1:
                address_data = requests.get(get_notary_addresses_url(season)).json()

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
                        if coin not in RETIRED_DPOW_CHAINS:
                            address = address_data[season][server][notary]["addresses"][coin]
                            pubkey = address_data[season][server][notary]["pubkey"]
                            thread_list[notary].append(
                                                    update_notary_balances_thread(
                                                        season, server, notary,
                                                        coin, pubkey, address
                                                    )
                                                )

                    for thread in thread_list[notary]:
                        thread.start()
                        time.sleep(0.2)
                    time.sleep(1) # 2 sec sleep = 8 min runtime.


def populate_addresses(season, server):
    url = get_dpow_server_coins_url(season, server)
    logger.info(url)
    coins = requests.get(url).json()['results']

    # TODO: We shouldn't need to add these extras
    coins += ["BTC", "KMD", "LTC"]
    if server == "Third_Party": 
        coins += ["EMC2", "AYA", "CHIPS", "GLEEC-OLD", "MCL", "VRSC", "SFUSD", "MIL"]
        coins = list(set(coins))
    coins.sort()

    if len(coins) > 0:
        i = 0
        pubkeys = get_pubkeys(season, server)

        for notary in pubkeys:
            pubkey = pubkeys[notary]

            for coin in coins:
                row = addresses_row()
                row.season = season
                row.server = server
                row.chain = coin
                row.notary_id = i
                row.notary = notary
                row.pubkey = pubkey
                row.update()

            i += 1

@print_runtime
def delete_stale_balances():
    logger.info(f"Removing stale data...")
    sql = f"DELETE FROM balances WHERE update_time < {int(time.time()-24*60*60)};"
    CURSOR.execute(sql)
    CONN.commit()

