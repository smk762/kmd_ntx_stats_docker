#!/usr/bin/env python3
from lib_const import CURSOR
from models import mined_row

import logging
import logging.handlers

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

sql = "SELECT DISTINCT season \
       FROM mined;"
CURSOR.execute(sql)
results = CURSOR.fetchall()
logger.info(f"{len(results)} seasons in mined table: {results}")

sql = "SELECT block_height, block_time, block_datetime, \
              value, address, name, txid, season \
       FROM mined WHERE \
       season = 'Season_5_Testnet';"
CURSOR.execute(sql)
results = CURSOR.fetchall()
logger.info(f"{len(results)} records to rescan...")

i = 0
for item in results:
    i += 1
    logger.info(f"Processing {i}/{len(results)}")
    row = mined_row()
    row.block_height = item["block_height"]
    row.block_time = item["block_time"]
    row.block_datetime = item["block_datetime"]
    row.value = item["value"]
    row.address = item["address"]
    row.name = item["name"]
    row.txid = item["txid"]
    row.season = item["season"]
    row.update()