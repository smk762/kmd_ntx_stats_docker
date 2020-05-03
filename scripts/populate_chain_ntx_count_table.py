#!/usr/bin/env python3
import os
import json
import binascii
import time
import logging
import requests
import logging.handlers
from notary_info import season_addresses, seasons_info
from rpclib import def_credentials
from os.path import expanduser
from dotenv import load_dotenv
import psycopg2

startblock = 1444000

def get_ac_block_heights():
    print("Getting AC block heights from electrum")
    ac_block_ht = {}
    for chain in antara_coins:
      try:
        url = 'http://'+chain.lower()+'.explorer.dexstats.info/insight-api-komodo/sync'
        r = requests.get(url)
        ac_block_ht.update({chain:r.json()['blockChainHeight']})
      except Exception as e:
        print(chain+" failed")
        print(e)
    return ac_block_ht

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

def get_chain_notarised_counts():
        print("Getting chain data from db")
        sql = "SELECT chain, MAX(block_ht), MAX(block_time), COUNT(*) FROM notarised WHERE block_time >= "+str(seasons_info["Season_3"]["start_time"])+" GROUP BY chain;"
        cursor.execute(sql)
        chains_aggr_resp = cursor.fetchall()

        print(chains_aggr_resp)

        ac_block_heights = get_ac_block_heights()
        print(ac_block_heights)

        chain_json = {}
        for item in chains_aggr_resp:
            print(item)
            chain = item[0]
            kmd_ntx_height = item[1]
            kmd_ntx_time = item[2]
            ntx_count = item[3]
            print("Getting "+chain+" data from db")
            try:
                sql = "SELECT prev_block_hash, prev_block_ht, opret, block_hash, txid FROM notarised WHERE chain = '"+chain+"' AND block_ht = "+str(kmd_ntx_height)+";"
                cursor.execute(sql)
                chains_resp = cursor.fetchone()
                print(chains_resp)
            except Exception as e:
                logger.debug(e)
                conn.rollback()


            chain_json.update({
                chain:{
                    "ntx_count": ntx_count,
                    "kmd_ntx_height": kmd_ntx_height,
                    "lastnotarization": kmd_ntx_time,
                    "kmd_ntx_blockhash": chains_resp[3],
                    "kmd_ntx_txid": chains_resp[4],
                    "opret": chains_resp[2],
                    "ac_ntx_block_hash": chains_resp[0],
                    "ac_ntx_height": chains_resp[1]
                }
            })
            if chain in ac_block_heights:
                chain_json[chain].update({
                    "ac_block_height": ac_block_heights[chain],
                    "ntx_lag": ac_block_heights[chain] - chains_resp[1]
                })
            else:
                chain_json[chain].update({
                    "ac_block_height": "no data",
                    "ntx_lag": "no data"
                })
            print(chain_json)
            row_data = ( chain, ntx_count, kmd_ntx_height, chain_json[chain]['kmd_ntx_blockhash'], chain_json[chain]['kmd_ntx_txid'],
                         chain_json[chain]['lastnotarization'], chain_json[chain]['opret'], chain_json[chain]['ac_ntx_block_hash'],
                         chain_json[chain]['ac_ntx_height'], chain_json[chain]['ac_block_height'],
                         chain_json[chain]['ntx_lag'])
            print("Adding counts for "+chain+" to notarised_chain table")
            add_row_to_notarised_chain_tbl(row_data)

def add_row_to_notarised_chain_tbl(row_data):
        sql = "INSERT INTO notarised_chain"
        sql = sql+" (chain, ntx_count, kmd_ntx_height, kmd_ntx_blockhash, kmd_ntx_txid, lastnotarization, opret, ac_ntx_block_hash, ac_ntx_height, ac_block_height, ntx_lag)"
        sql = sql+" VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        cursor.execute(sql, row_data)
        conn.commit()

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

table = 'notarised_chain'

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

cursor.execute("TRUNCATE "+table+";")
conn.commit()

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

results_list = get_chain_notarised_counts()
#update_table(results_list)

sql = "SELECT * FROM notarised_chain"
cursor.execute(sql)
print(cursor.fetchall())

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

cursor.close();

conn.close();