#!/usr/bin/env python3
import logging
import logging.handlers
from notary_info import address_info
from dotenv import load_dotenv
import psycopg2
import bitcoin
from bitcoin.core import x
from bitcoin.core import CoreMainParams
from bitcoin.wallet import P2PKHBitcoinAddress
from notary_info import notary_pubkeys

class KMD_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 60,
                       'SCRIPT_ADDR': 85,
                       'SECRET_KEY': 188}

class BTC_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 0,
                       'SCRIPT_ADDR': 5,
                       'SECRET_KEY': 128}

class AYA_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 23,
                       'SCRIPT_ADDR': 5,
                       'SECRET_KEY': 176}

class EMC2_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 33,
                       'SCRIPT_ADDR': 5,
                       'SECRET_KEY': 176}

class GAME_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 38,
                       'SCRIPT_ADDR': 5,
                       'SECRET_KEY': 166}

class GIN_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 38,
                       'SCRIPT_ADDR': 10,
                       'SECRET_KEY': 198}

coin_params = {
    "KMD": KMD_CoinParams,
    "BTC": BTC_CoinParams,
    "AYA": AYA_CoinParams,
    "EMC2": EMC2_CoinParams,
    "GAME": GAME_CoinParams,
    "GIN": GIN_CoinParams,
}
third_party = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'AYA', 'KMD']


# http://kmd.explorer.dexstats.info/insight-api-komodo/addr/RNJmgYaFF5DbnrNUX6pMYz9rcnDKC2tuAc

def add_row_to_addresses_tbl(row_data):
    try:
        sql = "INSERT INTO addresses"
        sql = sql+" (season, notary_name, notary_id, coin, pubkey, address)"
        sql = sql+" VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        logger.debug(e)
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
load_dotenv()

conn = psycopg2.connect(
  host='localhost',
  user='postgres',
  password='postgres',
  port = "7654",
  database='postgres'
)
cursor = conn.cursor()

table = 'addresses'

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

cursor.execute("TRUNCATE "+table+";")
conn.commit()

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

addresses = {}

for season in notary_pubkeys:
    addresses.update({season:{}})
    notary_id = 0
    for notary in notary_pubkeys[season]:
        if notary not in addresses:
            addresses[season].update({notary:{}})
        for coin in coin_params:
            bitcoin.params = coin_params[coin]
            pubkey = notary_pubkeys[season][notary]
            address = str(P2PKHBitcoinAddress.from_pubkey(x(pubkey)))
            addresses[season][notary].update({coin:address})
for season in addresses:
    for notary in addresses[season]:
        for coin in addresses[season][notary]:
            address = addresses[season][notary][coin]
            kmd_addr = addresses[season][notary]["KMD"]
            notary_id = address_info[season][kmd_addr]['Notary_id']
            row_data = (season, notary, notary_id, coin, pubkey, address)
            add_row_to_addresses_tbl(row_data)

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

cursor.close()

conn.close()