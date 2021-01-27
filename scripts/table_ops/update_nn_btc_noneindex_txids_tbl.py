#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
import logging
import logging.handlers
import psycopg2
import threading
from decimal import *
from datetime import datetime as dt
import datetime
from dotenv import load_dotenv
import table_lib


load_dotenv()

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

conn = table_lib.connect_db()
cursor = conn.cursor()

sql = "DELETE FROM nn_btc_tx a \
      USING ( \
      SELECT MIN(ctid) as ctid, txid \
        FROM nn_btc_tx \
        GROUP BY txid HAVING COUNT(*) > 1 \
      ) b \
      WHERE a.txid = b.txid \
      AND a.category = 'Split or Consolidate';"


#sql = "UPDATE nn_btc_tx SET \
#      input_index = 1000 \
#      WHERE txid  = '829564c9268f426363bd4dddc982a326f9544e958b2f290e53f7aab5fa47c933';"
try:
    logger.info(sql)
    cursor.execute(sql)
    conn.commit()
    logger.info("row updated")
except Exception as e:
    logger.debug(e)
    if str(e).find('duplicate') == -1:
        logger.debug(e)
    conn.rollback()


cursor.close()

conn.close()
