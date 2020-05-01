#!/usr/bin/env python3
import os
import json
import binascii
import time
import logging
import logging.handlers
from notary_pubkeys import known_addresses
from rpclib import def_credentials
from os.path import expanduser
from dotenv import load_dotenv
import psycopg2

startblock = 1444000

third_party_coins = ["AYA", "CHIPS", "EMC2", "GAME", "GIN", 'HUSH3']
antara_coins = ["AXO", "BET", "BOTS", "BTCH", "CCL", "COQUICASH", "CRYPTO", "DEX", "ETOMIC", "HODL", "ILN", "JUMBLR",
                "K64", "KOIN", "KSB", "KV", "MESH", "MGW", "MORTY", "MSHARK", "NINJA", "OOT", "OUR", "PANGEA", "PGT",
                "PIRATE", "REVS", "RFOX", "RICK", "SEC", "SUPERNET", "THC", "VOTE2020", "VRSC", "WLC", "WLC21", "ZEXO",
                "ZILLA", "STBL"]
ex_antara_coins = ['CHAIN', 'GLXT', 'MCL', 'PRLPAY', 'COMMOD', 'DION',
                   'EQL', 'CEAL', 'BNTN', 'KMDICE', 'DSEC']
all_antara_coins = antara_coins + ex_antara_coins

def get_max_col_val_in_table(col, table):
    sql = "SELECT MAX("+col+") FROM "+table+";"
    cursor.execute(sql)
    max_val = cursor.fetchone()
    logger.info("Max "+col+" value is "+str(max_val))
    return max_val

def get_notarised_counts():
    sql = "SELECT chain, notaries FROM notarised WHERE block_ht >= "+str(startblock)+";"
    cursor.execute(sql)
    results = cursor.fetchall()
    results_list = []
    timestamp = int(time.time())
    for item in results:
        results_list.append({
                "chain":item[0],
                "notaries":item[1]
            })
    json_count = {}
    print("Aggregating "+str(len(results_list))+" rows from notarised table")
    for item in results_list:
        notaries = item['notaries']
        chain = item['chain']
        for notary in notaries:
            if notary not in json_count:
                json_count.update({notary:{}})
            if chain not in json_count[notary]:
                json_count[notary].update({chain:1})
            else:
                count = json_count[notary][chain]+1
                json_count[notary].update({chain:count})
    print(json_count)
    node_counts = {}
    other_coins = []
    for notary in json_count:
        node_counts.update({notary:{
                "btc_count":0,
                "antara_count":0,
                "third_party_count":0,
                "other_count":0,
                "total_ntx_count":0
            }})
        for chain in json_count[notary]:
            if chain == "KMD":
                count = node_counts[notary]["btc_count"]+json_count[notary][chain]
                node_counts[notary].update({"btc_count":count})
            elif chain in all_antara_coins:
                count = node_counts[notary]["antara_count"]+json_count[notary][chain]
                node_counts[notary].update({"antara_count":count})
            elif chain in third_party_coins:
                count = node_counts[notary]["third_party_count"]+json_count[notary][chain]
                node_counts[notary].update({"third_party_count":count})
            else:
                count = node_counts[notary]["other_count"]+json_count[notary][chain]
                node_counts[notary].update({"other_count":count})
                other_coins.append(chain)

            count = node_counts[notary]["total_ntx_count"]+json_count[notary][chain]
            node_counts[notary].update({"total_ntx_count":count})

        row_data = (notary, node_counts[notary]['btc_count'], node_counts[notary]['antara_count'], 
                    node_counts[notary]['third_party_count'], node_counts[notary]['other_count'], 
                    node_counts[notary]['total_ntx_count'], json.dumps(json_count[notary]), timestamp)
        print("Adding counts for "+notary+" to notarised_count table")
        add_row_to_notarised_count_tbl(row_data)


def add_row_to_notarised_count_tbl(row_data):
    print("inserting")
    try:
        sql = "INSERT INTO notarised_count"
        sql = sql+" (notary, btc_count, antara_count, third_party_count, other_count, total_ntx_count, json_count, timestamp)"
        sql = sql+" VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

home = expanduser("~")

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


results_list = get_notarised_counts()
#update_table(results_list)

sql = "SELECT * FROM notarised_count"
x = cursor.execute(sql)
print(x.fetchall())

cursor.close();

conn.close();