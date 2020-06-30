#!/usr/bin/env python3
import logging
import logging.handlers
from notary_lib import *

''' You should only need to run this once per season, unless notary pubkeys change. 
Dont forget to update the pubkeys in py
TODO: auto grab from repo?
'''

# http://kmd.explorer.dexstats.info/insight-api-komodo/addr/RNJmgYaFF5DbnrNUX6pMYz9rcnDKC2tuAc

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

conn = connect_db()
cursor = conn.cursor()
for season in notary_addresses:
    if season.lower().find("third") != -1:
        node = 'third party'
    else:
        node = 'main'

    for notary in notary_addresses[season]:
        pubkey = notary_pubkeys[season][notary]

        for chain in notary_addresses[season][notary]:
            is_main_server = (node == 'main' and chain in antara_coins or chain == 'BTC')
            is_3p_server = (node == 'third party' and chain in third_party_coins)
            # ignore non notarising addresses
            if chain in ['KMD'] or is_main_server or is_3p_server:
                address = notary_addresses[season][notary][chain]
                kmd_addr = notary_addresses[season][notary]["KMD"]
                notary_id = address_info[season][kmd_addr]['Notary_id']
                row_data = (season, node, notary, notary_id, chain, pubkey, address)
                result = update_addresses_tbl(conn, cursor, row_data)
                if result == 0:
                    result = "[FAILED]"
                else:
                    result = "[SUCCESS]"
                print(" | "+result+" | "+pubkey+" | "+address+" | "+season+" | "+node+" | "+notary+" | "+chain+" | ")

cursor.close()

conn.close()