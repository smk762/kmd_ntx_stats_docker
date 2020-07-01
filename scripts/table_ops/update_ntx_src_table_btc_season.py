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
from table_lib import *

load_dotenv()

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

conn = connect_db()
cursor = conn.cursor()

sql = "UPDATE notarised SET \
    season='Season_3' WHERE season = 'Season_4' \
    AND chain = 'BTC' and ac_ntx_height < 1922000;"
cursor.execute(sql)
conn.commit()

cursor.close()

conn.close()
