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

def populate_addresses(season):
    season_coins = requests.get(f'{THIS_SERVER}/api/info/dpow_server_coins?season={season}').json()

    if len(season_coins) > 0:
        
        for pubkey_season in NOTARY_PUBKEYS:

            if pubkey_season.find(season) != -1:

                if pubkey_season.find("Third_Party") != -1:
                    coins = season_coins["Third_Party"][:]
                    server = "Third_Party"
                else:
                    coins = season_coins["Main"][:]
                    server = "Main"

                coins += ["BTC", "KMD", "LTC"]
                coins.sort()

                i = 0

                for notary in NOTARY_PUBKEYS[pubkey_season]:
                    pubkey = NOTARY_PUBKEYS[pubkey_season][notary]

                    for coin in coins:
                        row = addresses_row()
                        row.chain = coin
                        row.season = season
                        row.server = server
                        row.notary_id = i
                        row.notary = notary
                        row.pubkey = pubkey
                        if coin == "GLEEC":
                            if server == "Third_Party":
                                coin = "GLEEC_3P"
                            else:
                                coin = "GLEEC_AC"
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
        if season in EXCLUDED_SEASONS:
            logger.warning(f"Skipping season: {season}")
        else:
            populate_addresses(season)