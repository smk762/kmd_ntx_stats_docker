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


spam_txids = ['1d4d49bdd3d57a40ec19d2b463d10e0b1df499d36ec3871a9f5a8b20036458cb', '2dc3449b5cf366e430e8370e29ef1df8e7129dac216d97c20ec4099a68845f3a', '4aef6b1df8d9386b2a0094412a2498fd20cdbc27e63e662aa55f481f4a2d8a74', '51adca76b7fe5b5f7e4905e2cf3567d3c031ec0808db08045164e4939ef6bc2e', '55c1d916f7957d25c4e15dffa2269cac1211c28ab398d3e9c7334bc206260d16', 'a4d88acab12ab6075c3172b0ce7ac1b13ece688e34822e10933e91cdb09f3cdd', 'b1a22e2d37d378539e6cd60c87fcefa30be77bf792f204daaaf308e4e351b195', 'c4904e601f9ca129c84b19b8d54e95a60673ddc0e788c3a89d79dc4a491224e2', 'cde46b965e4207ef000a9ede85471dd0d82914d24dfc6a503eaf1fab008a616c', 'd3239fcd4ed507b1943ea4fe3cec19fff380d9cfb96d5a3b27bfba549be74a18', 'e5c24dbe206f6a7bd3ad04c90425b28efaf4ff095968c9560caeeadd665b9030']

for txid in spam_txids:  
    sql = "UPDATE nn_btc_tx SET \
          category='SPAM' \
          WHERE txid  = '"+txid+"';"
    try:
        cursor.execute(sql)
        conn.commit()
        logger.info("row updated")
    except Exception as e:
        if str(e).find('duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()

cursor.close()

conn.close()
