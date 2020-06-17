#!/usr/bin/env python3
import time
import logging
import logging.handlers
from datetime import datetime as dt
import datetime
from notary_lib import *
import psycopg2
from rpclib import def_credentials
from decimal import *
from psycopg2.extras import execute_values

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
Lastly, it updates the mined_count_season and mined_count_daily tables with aggregated stats for each notar season.
'''

# set this to false when originally populating the table, or rescanning
skip_past_seasons = True
# set this to false when originally populating the daily tables table, or rescanning
start_daily_2days_ago = True

scan_depth = 100


conn = connect_db()
cursor = conn.cursor()

season = get_season(int(time.time()))


rpc = {}
rpc["KMD"] = def_credentials("KMD")

# Scanning recently added blocks to recify orphans
recorded_txids = []
db_txids =  select_from_table(cursor, 'mined', 'txid')
for txid in db_txids:
    recorded_txids.append(txid[0])
    
tip = int(rpc["KMD"].getblockcount())
max_block_in_db = get_max_from_table(cursor, 'mined', 'block_height')
if max_block_in_db is None:
    max_block_in_db = scan_depth
if start_daily_2days_ago:
    max_block_in_db = 24*60*14
scan_blocks = [*range(max_block_in_db-scan_depth,max_block_in_db,1)]

known_addresses = get_known_addr("KMD", "Season_4")

for block in scan_blocks:
    logger.info("scanning block "+str(block)+"...")
    row_data = get_miner(block, known_addresses)
    if row_data[5] not in recorded_txids:
        logger.info("UPDATING BLOCK: "+str(block))
        update_mined_tbl(conn, cursor, row_data)

# adding new blocks...
existing_blocks = select_from_table(cursor, 'mined', 'block_height')
max_block =  get_max_from_table(cursor, 'mined', 'block_height')
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
    records.append(get_miner(block, known_addresses))
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

if skip_past_seasons:
    get_season_mined_counts(conn, cursor, season)
else:
    # updating season mined count aggregate table
    for season in seasons_info:
        get_season_mined_counts(conn, cursor, season)

# updating daily mined count aggregate table

# start on date of most recent season
season_start_time = seasons_info[season]["start_time"]
season_start_dt = dt.fromtimestamp(season_start_time)
start = season_start_dt.date()
end = datetime.date.today()
if start_daily_2days_ago:
    start = end - datetime.timedelta(days=7)
delta = datetime.timedelta(days=1)
logger.info("Aggregating daily notary notarisations from "+str(start)+" to "+str(end))
day = start

while day <= end:
    get_daily_mined_counts(conn, cursor, day)
    day += delta
logging.info("Finished!")


cursor.close()

conn.close()
