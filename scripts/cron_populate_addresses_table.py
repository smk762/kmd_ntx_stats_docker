#!/usr/bin/env python3
import requests
from lib_const import *
from models import addresses_row
from base_58 import get_addr_from_pubkey

''' 
You should only need to run this once per season, unless notary pubkeys change
or coins with new parmas are added.
TODO: auto grab from repo?
'''

def populate_addresses(season, server):
    url = f'{THIS_SERVER}/api/info/dpow_server_coins/?season={season}&server={server}'
    logger.info(url)
    coins = requests.get(url).json()['results']
    coins += ["BTC", "KMD", "LTC"]
    coins.sort()

    if len(coins) > 0:
        if server == 'Main':
            pubkeys = NOTARY_PUBKEYS[season]
        elif server == 'Third_Party':
            if f"{season}_Third_Party" in NOTARY_PUBKEYS:
                pubkeys = NOTARY_PUBKEYS[f"{season}_Third_Party"]
            else:
                pubkeys = []


        i = 0

        for notary in pubkeys:
            pubkey = pubkeys[notary]

            for coin in coins:
                row = addresses_row()
                row.chain = coin
                row.season = season
                row.server = server
                row.notary_id = i
                row.notary = notary
                row.pubkey = pubkey
                if coin == "GLEEC":
                    if row.server == "Third_Party":
                        coin = "GLEEC-OLD"
                    else:
                        coin = "GLEEC"
                row.address = get_addr_from_pubkey(coin, pubkey)
                row.update()

            i += 1

if __name__ == "__main__":

    logger.info(f"Preparing to populate [addresses] table...")

    # uncomment to clear table
    '''
    CURSOR.execute(f"DELETE FROM addresses;")
    CONN.commit()
    '''

    for season in SEASONS_INFO:
        #if season in EXCLUDED_SEASONS:
        #    logger.warning(f"Skipping season: {season}")
        #else:
        for server in ["Main", "Third_Party"]:
            populate_addresses(season, server)
    CURSOR.close()
    CONN.close()
