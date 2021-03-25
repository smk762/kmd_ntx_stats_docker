#!/usr/bin/env python3
from lib_notary import *
from lib_const import *
from lib_table_update import *
from lib_table_select import *
from lib_api import *


# recorded_txids = get_existing_ntxids()
deleted = []

for item in ["chain", "season", "server", "scored", "btc_validated"]:

            print(f"{item} in DB:")
            CURSOR.execute(f"SELECT DISTINCT {item} FROM notarised;")
            cat_rows = CURSOR.fetchall()
            print(cat_rows)
