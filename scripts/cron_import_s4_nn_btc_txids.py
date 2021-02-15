#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
import logging.handlers
import psycopg2
import requests
import threading
from decimal import *
from datetime import datetime as dt
import datetime
import dateutil.parser as dp
from dotenv import load_dotenv
from lib_rpc import def_credentials
from lib_electrum import get_ac_block_info
from lib_const import BTC_NTX_ADDR
from lib_notary import *
from lib_table_update import *
from lib_table_select import *
from lib_api import *

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# 14nE2emgyoUYCgYi759iubnqFtVV47eGDt, 18J5n4pQ25yjSkxtVhvMVmmrCuCKkyTyJZ, 1GMumuJSv8qZJ6XYBuuqLLiPkgmb8hSGCn initial funding source addrs

load_dotenv()

# set this to False in .env when originally populating the table, or rescanning
skip_past_seasons = (os.getenv("skip_past_seasons") == 'True')

# set this to True in .env to quickly update tables with most recent data
skip_until_yesterday = (os.getenv("skip_until_yesterday") == 'True')


def update_replenish_addresses():
    x = 0
    replenish_addresses = get_replenish_addresses(cursor)
    new_ra = []
    while True:
        updated = False
        logger.info(f"Replenish loop count {x}")
        logger.info(f"Replenish addr count {len(replenish_addresses)}")
        for addr in replenish_addresses:
            logger.info(f"getting txids for replenish address {addr}")
            time.sleep(0.1)
            ra_txids = get_existing_nn_btc_txids(cursor, addr, "Other")
            for txid in ra_txids:
                replenish_vin = False
                replenish_vout = False
                tx_vins, tx_vouts = get_nn_btc_tx_parts_local(txid)

                for vin in tx_vins:
                    if vin['address'] == addr and vin['notary'] != "SPAM" and vin['address'] not in [BTC_NTX_ADDR, "SPAM"]:
                        replenish_vin = True

                for vout in tx_vouts:
                    if vout['address'] in ALL_SEASON_NOTARY_BTC_ADDRESSES and vout['address'] not in [BTC_NTX_ADDR, "SPAM"] and vout['notary'] != "SPAM":
                        replenish_vout = True

                if replenish_vin or replenish_vout:
                    update_nn_btc_tx_category_from_txid(conn, cursor, "Top Up", txid)

                    for vin in tx_vins:
                        if vin['address'] not in ALL_SEASON_NOTARY_BTC_ADDRESSES and vin['notary'] not in ["Replenish_Address", "SPAM"] and vin['address'] not in [BTC_NTX_ADDR, "SPAM"]:
                            updated = True
                            new_ra.append(vin['address'])
                            update_nn_btc_tx_notary_from_addr(conn, cursor, "Replenish_Address", vin['address'])

                    for vout in tx_vouts:
                        if vout['address'] not in ALL_SEASON_NOTARY_BTC_ADDRESSES and vout['notary'] not in ["Replenish_Address", "SPAM"] and vout['address'] not in [BTC_NTX_ADDR, "SPAM"]:
                            updated = True
                            new_ra.append(vout['address'])
                            update_nn_btc_tx_notary_from_addr(conn, cursor, "Replenish_Address", vout['address'])

        if len(new_ra) == 0 or x > 12:
            logger.info(f"Replenish loop exit")
            break
        else:
            replenish_addresses = new_ra[:]
            new_ra = []
            x += 1

    # detect dragonhound_NA linked replenish addresses
    dh_txids = get_existing_nn_btc_txids(cursor, "1LtvR7B1zmvqKUeJkuaWYzSK2on8dS4u1h")
    for txid in dh_txids:
        replenish_vin = False
        replenish_vout = False
        tx_vins, tx_vouts = get_nn_btc_tx_parts_local(txid)

        for vin in tx_vins:
            if vin['address'] == "1LtvR7B1zmvqKUeJkuaWYzSK2on8dS4u1h":
                replenish_vin = True

        for vout in tx_vouts:
            if vout['address'] in ALL_SEASON_NOTARY_BTC_ADDRESSES and vout['address'] not in [BTC_NTX_ADDR, "1LtvR7B1zmvqKUeJkuaWYzSK2on8dS4u1h"] and vout['notary'] != "SPAM":
                replenish_vout = True

        if replenish_vin and replenish_vout:
            update_nn_btc_tx_category_from_txid(conn, cursor, "Replenished", txid)
            for vin in tx_vins:
                if vin['address'] not in ALL_SEASON_NOTARY_BTC_ADDRESSES and vin['notary'] not in ["Replenish_Address", "SPAM"]:
                    update_nn_btc_tx_notary_from_addr(conn, cursor, "Replenish_Address", vin['address'])
            for vout in tx_vouts:
                if vout['address'] not in ALL_SEASON_NOTARY_BTC_ADDRESSES and vout['notary'] not in ["Replenish_Address", "SPAM"] and vout['address'] not in [BTC_NTX_ADDR, "SPAM"]:
                    if vout['address'] not in ALL_SEASON_NOTARY_BTC_ADDRESSES and vout['address'] != BTC_NTX_ADDR:
                        update_nn_btc_tx_notary_from_addr(conn, cursor, "Replenish_Address", vout['address'])

conn = connect_db()
cursor = conn.cursor()

other_server = os.getenv("other_server")

'''
for season in NN_BTC_ADDRESSES_DICT:
    for addr in NN_BTC_ADDRESSES_DICT[season]:
        update_nn_btc_tx_notary_from_addr(conn, cursor, NN_BTC_ADDRESSES_DICT[season][addr], addr)
'''

# detect Replenish_Address linked replenish addresses
update_replenish_addresses()
categorize_import_transactions("1LtvR7B1zmvqKUeJkuaWYzSK2on8dS4u1h", "Season_4")

for season in NN_BTC_ADDRESSES_DICT:
    for notary_address in NOTARY_BTC_ADDRESSES[season]:
        if notary_address != "1LtvR7B1zmvqKUeJkuaWYzSK2on8dS4u1h":
            categorize_import_transactions(notary_address, season)

cursor.close()
conn.close()