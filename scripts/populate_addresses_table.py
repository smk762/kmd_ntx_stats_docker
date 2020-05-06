#!/usr/bin/env python3
import logging
import logging.handlers
from address_lib import address_info, notary_addresses, notary_pubkeys
import table_lib

# http://kmd.explorer.dexstats.info/insight-api-komodo/addr/RNJmgYaFF5DbnrNUX6pMYz9rcnDKC2tuAc

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

conn = table_lib.connect_db()
cursor = conn.cursor()

for season in notary_addresses:
    for notary in notary_addresses[season]:
        pubkey = notary_pubkeys[season][notary]
        for coin in notary_addresses[season][notary]:
            address = notary_addresses[season][notary][coin]
            kmd_addr = notary_addresses[season][notary]["KMD"]
            notary_id = address_info[season][kmd_addr]['Notary_id']
            row_data = (season, notary, notary_id, coin, pubkey, address)
            result = table_lib.add_row_to_addresses_tbl(conn, cursor, row_data)
            if result == 0:
                result = "[FAILED]"
            else:
                result = "[SUCCESS]"
            print(" | "+result+" | "+pubkey+" | "+address+" | "+season+" | "+notary+" | ")

cursor.close()

conn.close()