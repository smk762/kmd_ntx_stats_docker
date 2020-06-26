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

# set this to False in .env when originally populating the table, or rescanning
skip_past_seasons = os.getenv("skip_past_seasons")

# set this to True in .env to quickly update tables with most recent data
skip_until_yesterday = os.getenv("skip_until_yesterday")

scan_depth = 100


conn = connect_db()
cursor = conn.cursor()

season = get_season(int(time.time()))


rpc = {}
rpc["KMD"] = def_credentials("KMD")


def bulk_load_mined_clocks(conn, cursor, season):
    # Scanning recently added blocks to recify orphans
    recorded_txids = []
    db_txids =  select_from_table(cursor, 'mined', 'txid')
    for txid in db_txids:
        recorded_txids.append(txid[0])

    # re-check last ten recorded blocks in case of orphans
    tip = int(rpc["KMD"].getblockcount())
    scan_blocks = [*range(tip-10,tip,1)]
    for block in scan_blocks:
        logger.info("scanning block "+str(block)+"...")
        row_data = get_miner(block)
        logger.info("UPDATING BLOCK: "+str(block))
        update_mined_tbl(conn, cursor, row_data)


    # adding new blocks...
    records = []
    start = time.time()
    existing_blocks = select_from_table(cursor, 'mined', 'block_height')
    tip = int(rpc["KMD"].getblockcount())
    all_blocks = [*range(seasons_info[season]["start_block"],tip,1)]
    recorded_blocks = []
    for block in existing_blocks:
        recorded_blocks.append(block[0])
    unrecorded_blocks = set(all_blocks) - set(recorded_blocks)
    logger.info("Blocks in database: "+str(len(recorded_blocks)))
    logger.info(season+" blocks in chain: "+str(len(all_blocks)))
    logger.info(season+" blocks not in database: "+str(len(unrecorded_blocks)))
    i = 1
    start_block = seasons_info[season]["start_block"]
    if skip_until_yesterday:
        start_block = tip-2*24*60
    for block in unrecorded_blocks:
        if block >= start_block:
            row_data = get_miner(block)
            records.append(row_data)
            if len(records) == 1000:
                now = time.time()
                pct = round(len(records)*i/len(unrecorded_blocks)*100,3)
                runtime = int(now-start)
                est_end = int(100/pct*runtime)
                logger.info(str(pct)+"% :"+str(len(records)*i)+"/"+str(len(unrecorded_blocks))+" records added to db \
                         ["+str(runtime)+"/"+str(est_end)+" sec]")
                execute_values(cursor, "INSERT INTO mined (block_height, block_time, block_datetime, value, address, name, txid, season) VALUES %s", records)
                conn.commit()
                records = []
                logger.info("10080 Blocks added to db")

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
    bulk_load_mined_clocks(conn, cursor, season)
    get_season_mined_counts(conn, cursor, season)
else:
    # updating season mined count aggregate table
    for season in seasons_info:
        bulk_load_mined_clocks(conn, cursor, season)
        get_season_mined_counts(conn, cursor, season)

# updating daily mined count aggregate table

# start on date of most recent season
season_start_time = seasons_info[season]["start_time"]
season_start_dt = dt.fromtimestamp(season_start_time)
start = season_start_dt.date()
end = datetime.date.today()
if skip_until_yesterday:
    start = end - datetime.timedelta(days=7)
delta = datetime.timedelta(days=1)
logger.info("Aggregating daily notary notarisations from "+str(start)+" to "+str(end))
day = start

while day <= end:
    get_daily_mined_counts(conn, cursor, day)
    day += delta
logger.info("Finished!")


cursor.close()

conn.close()
