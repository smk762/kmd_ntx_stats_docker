#!/usr/bin/env python3
import time
import logging
import logging.handlers
from address_lib import notary_info, known_addresses, seasons_info
import psycopg2
from rpclib import def_credentials
from decimal import *
from psycopg2.extras import execute_values
import table_lib

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

''' 
This script is intended to run as a cronjob every 5-15 minutes.
It rescans the last 100 blocks in the database (configurable with "scan_depth" variable) to realign potential orphaned blocks in the database
Next, it retrieves info from the block chain for blocks not yet in the database and updates the mined table.
Lastly, it updates the mined_counts table with aggregated stats for each notar season.

'''
scan_depth = 100

conn = table_lib.connect_db()
cursor = conn.cursor()

rpc = {}
rpc["KMD"] = def_credentials("KMD")

# Scanning recently added blocks to recify orphans
recorded_txids = []
db_txids =  table_lib.select_from_table(cursor, 'mined', 'txid')
for txid in db_txids:
    recorded_txids.append(txid[0])
    
tip = int(rpc["KMD"].getblockcount())
max_block_in_db = table_lib.get_max_col_val_in_table(cursor, 'block_height', 'mined')
scan_blocks = [*range(max_block_in_db-scan_depth,max_block_in_db,1)]
for block in scan_blocks:
    logger.info("scanning block "+str(block)+"...")
    row_data = table_lib.get_miner(block)
    if row_data[5] not in recorded_txids:
        logger.info("UPDATING BLOCK: "+str(block))
        table_lib.update_mined_tbl(conn, cursor, row_data)

# adding new blocks...
existing_blocks = table_lib.select_from_table(cursor, 'mined', 'block_height')
max_block =  table_lib.get_max_col_val_in_table(cursor, 'block_height', 'mined')
tip = int(rpc["KMD"].getblockcount())
all_blocks = [*range(0,tip,1)]
recorded_blocks = []
for block in existing_blocks:
    recorded_blocks.append(block[0])
unrecorded_blocks = set(all_blocks) - set(recorded_blocks)
logger.info("Blocks in chain: "+str(len(all_blocks)))
logger.info("Blocks in database: "+str(len(recorded_blocks)))
logger.info("Blocks not in database: "+str(len(unrecorded_blocks)))
logger.info("Max Block in database: "+str(max_block))


records = []

start = time.time()
i = 1
for block in unrecorded_blocks:
    records.append(table_lib.get_miner(block))
    if len(records) == 10080:
        now = time.time()
        pct = round(len(records)*i/len(unrecorded_blocks)*100,3)
        runtime = int(now-start)
        est_end = int(100/pct*runtime)
        logger.info(str(pct)+"% :"+str(len(records)*i)+"/"+str(len(unrecorded_blocks))+" records added to db \
                 ["+str(runtime)+"/"+str(est_end)+" sec]")
        execute_values(cursor, "INSERT INTO mined (block_height, block_time, block_datetime, value, address, name, txid, season) VALUES %s", records)
        conn.commit()
        records = []
        i += 1
        if i%5 == 0:
            cursor.execute("SELECT COUNT(*) from mined;")
            block_count = cursor.fetchone()
            logger.info("Blocks in database: "+str(block_count[0])+"/"+str(len(all_blocks)))

execute_values(cursor, "INSERT INTO mined (block_height, block_time, block_datetime, value, address, name, txid, season) VALUES %s", records)
conn.commit()
logger.info("Finished!")
logger.info(str(len(unrecorded_blocks))+" mined blocks added to table")

# updating mined count aggregate table
for season in seasons_info:
    table_lib.get_mined_counts(conn, cursor, season)
logging.info("Finished!")


cursor.close()

conn.close()
