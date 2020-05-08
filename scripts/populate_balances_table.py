#!/usr/bin/env python3
import time
from coins_lib import antara_coins
import table_lib
import electrum_lib
import logging
import logging.handlers
from address_lib import notary_addresses

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

conn = table_lib.connect_db()
cursor = conn.cursor()
update_time = int(time.time())
for season in notary_addresses:
    for notary in notary_addresses[season]:
        for chain in notary_addresses[season][notary]:
            addr = notary_addresses[season][notary][chain]
            logger.info("Getting "+chain+" "+season+" balances for "+notary+" ["+addr+"]")
            balance = electrum_lib.get_electrum_balance(chain, addr)
            row_data = (notary, chain, balance, addr, update_time)        
            table_lib.update_balances_tbl(conn, cursor, row_data)

cursor.close()

conn.close()