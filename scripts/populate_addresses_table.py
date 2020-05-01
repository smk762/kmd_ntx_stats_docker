#!/usr/bin/env python3
import logging
import logging.handlers
from notary_info import address_info
from dotenv import load_dotenv
import psycopg2

def add_row_to_addresses_tbl(row_data):
    try:
        sql = "INSERT INTO addresses"
        sql = sql+" (notary_id, notary_name, address, pubkey, season)"
        sql = sql+" VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        logger.debug(e)
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

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

for address in address_info:
    row_data = (address['Notary_id'], address['Notary'], address, address['Pubkey'], address['Season'])
    add_row_to_addresses_tbl(row_data)

cursor.close()

conn.close()