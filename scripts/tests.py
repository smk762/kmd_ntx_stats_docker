#!/usr/bin/env python3
from notary_lib import *
from rpclib import *
#from unittest import TestCase

rpc = {}
rpc["KMD"] = def_credentials("KMD")

conn = connect_db()
cursor = conn.cursor()

season = get_season(int(time.time()))
assert season == "Season_4"

block_range_tables = ['mined','notarised', 'funding_transactions']
test_data = {}

for tbl in block_range_tables:
#collect test data: 500 blocks (1929000 - 1929099)
    sql = "SELECT * FROM "+tbl+" WHERE block_height >= 1929000 AND block_height < 1929100;"
    cursor.execute(sql)
    test_data.update({tbl: cursor.fetchall()})

try:
    assert len(test_data['mined']) == 100
except Exception as e:
    print("mined len assert failed")
