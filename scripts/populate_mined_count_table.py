#!/usr/bin/env python3
import logging
import logging.handlers
from address_lib import seasons_info
import table_lib

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

conn = table_lib.connect_db()
cursor = conn.cursor()

for season in seasons_info:
    table_lib.get_mined_counts(conn, cursor, season)
logging.info("Finished!")

cursor.close()

conn.close()