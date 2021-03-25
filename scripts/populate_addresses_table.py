#!/usr/bin/env python3
import logging
import logging.handlers
from lib_notary import *
from lib_const import *
from lib_table_update import update_addresses_tbl

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

for season in NOTARY_ADDRESSES_DICT:
    if season.lower().find("third") != -1:
        node = 'third party'
    else:
        node = 'main'

    for notary in NOTARY_ADDRESSES_DICT[season]:
        pubkey = NOTARY_PUBKEYS[season][notary]

        for chain in NOTARY_ADDRESSES_DICT[season][notary]:
            is_main_server = (node == 'main' and chain in ANTARA_COINS or chain == 'BTC')
            is_3p_server = (node == 'third party' and chain in THIRD_PARTY_COINS)
            # ignore non notarising addresses
            if chain in ['KMD', 'LTC', 'BTC'] or is_main_server or is_3p_server:
                address = NOTARY_ADDRESSES_DICT[season][notary][chain]
                kmd_addr = NOTARY_ADDRESSES_DICT[season][notary]["KMD"]
                notary_id = ADDRESS_INFO[season][kmd_addr]['Notary_id']
                row_data = (season, node, notary, notary_id, chain, pubkey, address)
                result = update_addresses_tbl(row_data)
                if result == 0:
                    result = "[FAILED]"
                else:
                    result = "[SUCCESS]"
                if chain == 'GleecBTC':
                    print(" | "+result+" | "+pubkey+" | "+address+" | "+season+" | "+node+" | "+notary+" | "+chain+" | ")

CURSOR.close()

CONN.close()