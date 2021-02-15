#!/usr/bin/env python3
import time
import logging
import logging.handlers
from datetime import datetime as dt
import datetime
import requests
import psycopg2
from decimal import *
from psycopg2.extras import execute_values
from lib_notary import *
from lib_rpc import def_credentials

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

try:
    r = requests.get('http://138.201.207.24/funding_tx')
    funding_tx = r.json()
except:
    funding_tx = []

conn = connect_db()
cursor = conn.cursor()

for item in funding_tx:
    row_list = []
    row_list.append(item["chain"])
    row_list.append(item["txid"])
    row_list.append(item["vout"])
    row_list.append(item["amount"])
    row_list.append(item["block_hash"])
    row_list.append(item["block_height"])
    row_list.append(item["block_time"])
    row_list.append(item["category"])
    row_list.append(item["fee"])
    row_list.append(item["address"])
    notary = get_notary_from_address(item["address"])
    row_list.append(notary)
    row_list.append(get_season(int(item["block_time"])))
    row_data = tuple(row_list)

    update_funding_tbl(conn, cursor, row_data)


cursor.close()

conn.close()
