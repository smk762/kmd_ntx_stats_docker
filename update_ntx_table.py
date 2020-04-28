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
    last_block = cursor.fetchone()
    logger.info("Last block recorded was "+str(last_block[0]))
    return last_block[0]

def add_row_to_ntx_tbl(row_data):
    try:
        sql = "INSERT INTO notarised"
        sql = sql+" (chain, block_ht, block_hash, notaries, prev_block_hash, prev_block_ht, txid)"
        sql = sql+" VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0


def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def get_ntx_txids(ntx_addr, start, end):
    return rpc["KMD"].getaddresstxids({"addresses": [ntx_addr], "start":start, "end":end})
    
def get_ticker(scriptPubKeyBinary):
    ntx_data = []
    chain = ''
    while len(chain) < 1:
        for i in range(len(scriptPubKeyBinary)):
            if chr(scriptPubKeyBinary[i]).encode() == b'\x00':
                j = i+1
                while j < len(scriptPubKeyBinary)-1:
                    chain += chr(scriptPubKeyBinary[j])
                    j += 1
                    if chr(scriptPubKeyBinary[j]).encode() == b'\x00':
                        break
                break
    if chr(scriptPubKeyBinary[-4])+chr(scriptPubKeyBinary[-3])+chr(scriptPubKeyBinary[-2]) =="KMD":
        chain = "KMD"
    return chain

def get_ntx_data():
    ntx_txids = get_ntx_txids(ntx_addr, startblock, endblock)
    logger.info(str(len(ntx_txids))+" TXIDs to process...")
    i = 0
    for txid in ntx_txids:
        i += 1
        if i%100 == 0 or i == len(ntx_txids): 
            pct = round(i/len(ntx_txids)*100,2)
            logger.info(str(pct)+"% transactions processed...")
        raw_tx = rpc["KMD"].getrawtransaction(txid,1)
        dest_addrs = raw_tx["vout"][0]['scriptPubKey']['addresses']
        if len(dest_addrs) > 0 and ntx_addr in dest_addrs and len(raw_tx['vin']) >= 13:
            scriptPubKey_asm = raw_tx['vout'][1]['scriptPubKey']['asm'].replace("OP_RETURN ","")
            this_block_hash = raw_tx['blockhash']
            this_block_ht = raw_tx['height']
            prev_block_hash = lil_endian(scriptPubKey_asm[:64])
            prev_block_ht = int(lil_endian(scriptPubKey_asm[64:72]),16)
            scriptPubKeyBinary = binascii.unhexlify(scriptPubKey_asm[70:])
            chain = get_ticker(scriptPubKeyBinary)
            if chain.endswith("KMD"):
                chain = "KMD"
            if chain == "KMD":
                btc_txid = lil_endian(scriptPubKey_asm[72:136])
            elif chain not in noMoM:
                # not sure about this bit, need another source to validate the data
                try:
                    start = 72+len(chain)*2+4
                    end = 72+len(chain)*2+4+64
                    MoM_hash = lil_endian(scriptPubKey_asm[start:end])
                    MoM_depth = int(lil_endian(scriptPubKey_asm[end:]),16)
                except:
                    pass
            notary_list = []
            for item in raw_tx['vin']:
                if "address" in item:
                    if item['address'] in known_addresses:
                        notary = known_addresses[item['address']]
                        notary_list.append(notary)
                    else:
                        notary_list.append(item['address'])
            if chain not in ntx_data:
                ntx_data.update({
                        chain:{}
                    })
            notary_list.sort()
            ntx_data[chain].update({
                    this_block_ht:{
                        "block_hash":this_block_hash,
                        "prev_block_hash":prev_block_hash,
                        "prev_block_ht":prev_block_ht,
                        "txid":txid,
                        "notaries": notary_list
                    }
                })
            row_data = (chain, this_block_ht, this_block_hash, notary_list, prev_block_hash, prev_block_ht, txid)
            add_row_to_ntx_tbl(row_data)
    logger.info("Finished... Aggregating results....")
    return ntx_data


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



rpc = {}
rpc["KMD"] = def_credentials("KMD")

ntx_data = {}
ntx_addr = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'
try:
    startblock = get_max_col_val_in_table("block_ht", "notarised")-1
except:
    startblock = 1444000 # season start block
if startblock is None:
    startblock = 1444000
endblock = 7113400 # season end block (or tip if mid season)
tip = int(rpc["KMD"].getblockcount())
logger.info("block at chain tip is "+str(tip))

kmdfilter = 1525032458
acfilter = 1525513998
noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'AYA']

if endblock > tip:
    endblock = tip
while endblock - startblock > 5000:
    logger.info("Processing blocks "+str(startblock)+" to "+str(endblock))
    endblock = startblock + 4000
    ntx_data = get_ntx_data()
    if startblock > tip:
        break
    startblock = endblock
    endblock = startblock + 6000

ntx_data = get_ntx_data()

get_notarised_counts()

cursor.close();

conn.close();