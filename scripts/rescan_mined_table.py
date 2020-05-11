#!/usr/bin/env python3
import time
import logging
import logging.handlers
from address_lib import seasons_info
import psycopg2
from rpclib import def_credentials
import table_lib

'''
This script rescans the database against the blockchain to add newly mined blocks and update records for earlier mined block (in case of orphans).
On completion, it will also populate the aggregate " mined_count_season" and "mined_count_daily" tables.

Note: This script takes a long time to run, so you should use "populate_mined_table.py" unless you suspect orphans.
The "populate_mined_table.py" script will be updated to autmatically scan back the last 20 blocks in next version
'''

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


conn = table_lib.connect_db()
cursor = conn.cursor()

rpc = {}
rpc["KMD"] = def_credentials("KMD")

recorded_txids = []
tip = int(rpc["KMD"].getblockcount())
all_blocks = [*range(0,tip,1)]
all_blocks.reverse()
db_txids = table_lib.select_from_table(cursor, 'mined', 'txid')
for txid in db_txids:
    recorded_txids.append(txid[0])
start = time.time()
i = 1
for block in all_blocks:
    logger.info("scanning block "+str(block)+"...")
    row_data = table_lib.get_miner(block)
    if row_data[5] not in recorded_txids:
        logger.info("UPDATING BLOCK: "+str(block))
        table_lib.update_mined_tbl(conn, cursor, row_data)
    i += 1
    if i%5000 == 0:
        now = time.time()
        pct = round(i/len(all_blocks)*100,3)
        runtime = int(now-start)
        est_end = int(100/pct*runtime)
        logger.info(str(pct)+"% :"+str(i)+"/"+str(len(all_blocks))+" records scanned \
                 ["+str(runtime)+"/"+str(est_end)+" sec]")

logger.info("Finished!")

for season in seasons_info:
    table_lib.get_season_mined_counts(conn, cursor, season)
logging.info("Finished!")


cursor.close()

conn.close()
