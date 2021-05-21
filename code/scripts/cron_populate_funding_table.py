#!/usr/bin/env python3
import requests
from lib_const import *
from lib_helper import *
from lib_notary import get_notary_from_address, get_season
from models import funding_row

def get_funding_tx():
    try:
        r = requests.get('http://138.201.207.24/funding_tx')
        funding_tx = r.json()
    except:
        funding_tx = []

    for item in funding_tx:
        row = funding_row()
        row.chain = item["chain"]
        row.txid = item["txid"]
        row.vout = item["vout"]
        row.amount = item["amount"]
        row.block_hash = item["block_hash"]
        row.block_height = item["block_height"]
        row.block_time = item["block_time"]
        row.category = item["category"]
        row.fee = item["fee"]
        row.address = item["address"]
        row.notary = get_notary_from_address(item["address"])
        row.season = get_season(int(item["block_time"]))
        row.update()

if __name__ == "__main__":
    
    get_funding_tx()
    CURSOR.close()
    CONN.close()
