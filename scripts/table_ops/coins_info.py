#!/usr/bin/env python3
import os
import sys
import json
import binascii
import time
import logging
import logging.handlers
import psycopg2
import table_lib
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

conn = table_lib.connect_db()
cursor = conn.cursor()

def get_dpow_coins(cursor):
    sql = "SELECT * \
           FROM coins WHERE \
           dpow_active = 1;"
    cursor.execute(sql)
    return cursor.fetchall()

third_party_coins = []
antara_coins = []
dpow_coins = get_dpow_coins(cursor)

for item in dpow_coins:
    if item[6]['server'] == 'dpow-mainnet':
        if item[1] not in ['KMD', 'BTC']:
            antara_coins.append(item[1])
    elif item[6]['server'] == 'dpow-3p':
        third_party_coins.append(item[1])


print(third_party_coins)
print(antara_coins)
