#!/usr/bin/env python3
import os
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

def get_miner(block):
    blockinfo = rpc["KMD"].getblock(str(block), 2)
    blocktime = blockinfo['time']
    for tx in blockinfo['tx']:
        if len(tx['vin']) > 0:
            if 'coinbase' in tx['vin'][0]:
                if 'addresses' in tx['vout'][0]['scriptPubKey']:
                    address = tx['vout'][0]['scriptPubKey']['addresses'][0]
                    if address in address_info:
                        name = address_info[address]['Notary']
                    else:
                        name = address
                else:
                    address = "N/A"
                    name = "non-standard"

                value = tx['vout'][0]['value']
                row_data = (block, blocktime, Decimal(value), address, name, tx['txid'])
                return row_data

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

recorded_blocks = []
cursor.execute("SELECT block from mined;")
existing_blocks = cursor.fetchall()
cursor.execute("SELECT MAX(block) from mined;")
max_block = cursor.fetchone()
tip = int(rpc["KMD"].getblockcount())
all_blocks = [*range(0,tip,1)]
for block in existing_blocks:
    recorded_blocks.append(block[0])
unrecorded_blocks = set(all_blocks) - set(recorded_blocks)
logger.info("Blocks in chain: "+str(len(all_blocks)))
logger.info("Blocks in database: "+str(len(recorded_blocks)))
logger.info("Blocks not in database: "+str(len(unrecorded_blocks)))
logger.info("Max Block in database: "+str(max_block[0]))


records = []

start = time.time()
i = 1
for block in unrecorded_blocks:
    records.append(get_miner(block))
    if len(records) == 10080:
        now = time.time()
        pct = round(len(records)*i/len(unrecorded_blocks)*100,3)
        runtime = int(now-start)
        est_end = int(100/pct*runtime)
        logger.info(str(pct)+"% :"+str(len(records)*i)+"/"+str(len(unrecorded_blocks))+" records added to db ["+str(runtime)+"/"+str(est_end)+" sec]")
        execute_values(cursor, "INSERT INTO mined (block, block_time, value, address, name, txid) VALUES %s", records)
        conn.commit()
        records = []
        i += 1
        if i%5 == 0:
            cursor.execute("SELECT COUNT(*) from mined;")
            block_count = cursor.fetchone()
            logger.info("Blocks in database: "+str(block_count[0])+"/"+str(len(all_blocks)))

execute_values(cursor, "INSERT INTO mined (block, block_time, value, address, name, txid) VALUES %s", records)
conn.commit()
logger.info("Finished!")
logger.info(str(len(unrecorded_blocks))+" mined blocks added to table")
    

cursor.close()

conn.close()