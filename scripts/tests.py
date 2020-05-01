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
from pgcopy import CopyManager
from decimal import *
from psycopg2.extras import execute_values

# Mined table count should = getblockcount 

def check_mined_table():
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

def check_ntx_table():
	

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

check_mined_table()

cursor.close()

conn.close()