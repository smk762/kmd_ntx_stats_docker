#!/usr/bin/env python3
import os
import sys
import json
import binascii
import time
import logging
import logging.handlers
from notary_pubkeys import known_addresses
from notary_info import notary_info, address_info, seasons_info
from rpclib import def_credentials
from os.path import expanduser
from dotenv import load_dotenv
import psycopg2
from decimal import *
from psycopg2.extras import execute_values


third_party_coins = ["AYA", "CHIPS", "EMC2", "GAME", "GIN", 'HUSH3']
antara_coins = ["AXO", "BET", "BOTS", "BTCH", "CCL", "COQUICASH", "CRYPTO", "DEX", "ETOMIC", "HODL", "ILN", "JUMBLR",
                "K64", "KOIN", "KSB", "KV", "MESH", "MGW", "MORTY", "MSHARK", "NINJA", "OOT", "OUR", "PANGEA", "PGT",
                "PIRATE", "REVS", "RFOX", "RICK", "SEC", "SUPERNET", "THC", "VOTE2020", "VRSC", "WLC", "WLC21", "ZEXO",
                "ZILLA", "STBL"]
ex_antara_coins = ['CHAIN', 'GLXT', 'MCL', 'PRLPAY', 'COMMOD', 'DION',
                   'EQL', 'CEAL', 'BNTN', 'KMDICE', 'DSEC']
all_antara_coins = antara_coins + ex_antara_coins

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def get_ntx_txids(ntx_addr, start, end):
    return rpc["KMD"].getaddresstxids({"addresses": [ntx_addr], "start":start, "end":end})
    
def get_ticker(scriptPubKeyBinary):
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

def get_ntx_data(txid):
    raw_tx = rpc["KMD"].getrawtransaction(txid,1)
    this_block_hash = raw_tx['blockhash']
    dest_addrs = raw_tx["vout"][0]['scriptPubKey']['addresses']
    this_block_time = raw_tx['blocktime']
    this_block_ht = raw_tx['height']
    if len(dest_addrs) > 0:
        if ntx_addr in dest_addrs:
            if len(raw_tx['vin']) >= 13:
                notary_list = []
                for item in raw_tx['vin']:
                    if "address" in item:
                        if item['address'] in known_addresses:
                            notary = known_addresses[item['address']]
                            notary_list.append(notary)
                        else:
                            notary_list.append(item['address'])
                notary_list.sort()
                opret = raw_tx['vout'][1]['scriptPubKey']['asm']
                if opret.find("OP_RETURN") != -1:
                    scriptPubKey_asm = opret.replace("OP_RETURN ","")
                    prev_block_hash = lil_endian(scriptPubKey_asm[:64])
                    try:
                        prev_block_ht = int(lil_endian(scriptPubKey_asm[64:72]),16) 
                    except:
                        print(scriptPubKey_asm)
                        sys.exit()
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
                        except Exception as e:
                            logger.debug(e)
                    row_data = (chain, this_block_ht, this_block_time, this_block_hash, notary_list, prev_block_hash, prev_block_ht, txid, opret)
                else:
                    row_data = ("not_opret", this_block_ht, this_block_time, this_block_hash, notary_list, "unknown", 0, txid, "unknown")
                
            else:
                # logger.info("["+txid+"] only has "+str(len(raw_tx['vin']))+" vins!")
                row_data = ("low_vin", this_block_ht, this_block_time, this_block_hash, [], "unknown", 0, txid, "unknown")
        else:
            # logger.info("["+txid+"] ntx_address not in destination addresses!")
            row_data = ("not_dest", this_block_ht, this_block_time, this_block_hash, [], "unknown", 0, txid, "unknown")
    else:
        # logger.info("["+txid+"] has no destination addresses!")
        row_data = ("no_dest", this_block_ht, this_block_time, this_block_hash, [], "unknown", 0, txid, "unknown") 
    return row_data

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

ntx_addr = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'

recorded_txids = []

logger.info("Getting existing TXIDs from database...")
cursor.execute("SELECT txid from notarised;")
existing_txids = cursor.fetchall()
tip = int(rpc["KMD"].getblockcount())
start_block = 0
all_txids = []
chunk_size = 100000
while tip - start_block > chunk_size:
    logger.info("Getting notarization TXIDs from block chain data for blocks "+str(start_block+1)+" to "+str(start_block+chunk_size)+"...")
    all_txids += get_ntx_txids(ntx_addr, start_block+1, start_block+chunk_size)
    start_block += chunk_size
all_txids += get_ntx_txids(ntx_addr, start_block+1, tip)
for txid in existing_txids:
    recorded_txids.append(txid[0])
unrecorded_txids = set(all_txids) - set(recorded_txids)
logger.info("TXIDs in chain: "+str(len(all_txids)))
logger.info("TXIDs in chain (set): "+str(len(set(all_txids))))
logger.info("TXIDs in database: "+str(len(recorded_txids)))
logger.info("TXIDs in database (set): "+str(len(set(recorded_txids))))
logger.info("TXIDs not in database: "+str(len(unrecorded_txids)))

noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'AYA']

records = []
start = time.time()
i = 1
for txid in unrecorded_txids:
    row_data = get_ntx_data(txid)
    records.append(row_data)

    if len(records) == 10080:
        now = time.time()
        pct = str(round(len(records)*i/len(unrecorded_txids)*100,3))+"%"
        logger.info(pct+" :"+str(len(records)*i)+"/"+str(len(unrecorded_txids))+" records added to db ["+str(int(now-start))+" sec]")
        execute_values(cursor, "INSERT INTO notarised (chain, block_ht, block_time, block_hash, notaries, prev_block_hash, prev_block_ht, txid, opret) VALUES %s", records)
        conn.commit()
        records = []
        i += 1
        if i%5 == 0:
            cursor.execute("SELECT COUNT(*) from notarised;")
            block_count = cursor.fetchone()
            logger.info("notarisations in database: "+str(block_count[0]))

execute_values(cursor, "INSERT INTO notarised (chain, block_ht, block_time, block_hash, notaries, prev_block_hash, prev_block_ht, txid, opret) VALUES %s", records)

conn.commit()
logger.info("Finished!")
logger.info("NTX Address transactions processed: "+str(len(unrecorded_txids)))
logger.info("Finished!")
logger.info("Finished!")
logger.info(str(len(unrecorded_txids))+" notarised TXIDs added to table")

cursor.close()

conn.close()