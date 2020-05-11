#!/usr/bin/env python3
import time
from coins_lib import antara_coins
import table_lib
import electrum_lib
import logging
import logging.handlers
from address_lib import notary_addresses
import threading

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

'''
This script checks notary balance via electrum servers. 
It should be run as a cronjob every 6 hours or so (takes about an hour to run).
'''

class electrum_thread(threading.Thread):
    def __init__(self, conn, cursor, notary, chain, addr, season):
        threading.Thread.__init__(self)
        self.conn = conn
        self.cursor = cursor
        self.notary = notary
        self.chain = chain
        self.addr = addr
        self.season = season
    def run(self):
        thread_electrum(self.conn, self.cursor, self.notary,
                        self.chain, self.addr, self.season)

def thread_electrum(conn, cursor, notary, chain, addr, season):
    if season.find("Season_3") != -1:
        season = "Season_3"
    balance = electrum_lib.get_electrum_balance(chain, addr)
    row_data = (notary, chain, balance, addr, season, int(time.time()))        
    table_lib.update_balances_tbl(conn, cursor, row_data)
    logger.info("Got "+chain+" "+season+" balances for "+notary+" ["+addr+"]")

conn = table_lib.connect_db()
cursor = conn.cursor()
thread_list = {}
for season in notary_addresses:
    for notary in notary_addresses[season]:
        thread_list.update({notary:[]})
        for chain in notary_addresses[season][notary]:
            addr = notary_addresses[season][notary][chain]
            thread_list[notary].append(electrum_thread(conn, cursor, notary, chain, addr, season))
        for thread in thread_list[notary]:
            thread.start()
        time.sleep(1)

cursor.close()

conn.close()