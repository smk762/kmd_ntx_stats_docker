#!/usr/bin/env python3.12

import sys
import json
import requests
from logger import logger

coin = input("Coin: ")
season = input("Season: ")
server = input("Server: ")
amount = input("amount: ")

r = requests.get(f"http://116.203.120.91:8762/api/table/addresses/?season={season}&server={server}&coin={coin}")
resp = r.json()["results"]

addresses = []

for item in resp:
    if item['notary'] not in ['alrighttt_DEV', 'majora31_SH']:
        addresses.append(item["address"])

sendmany = {}
for address in addresses:
    sendmany.update({address:amount})

logger.info(coin+' sendmany "" "'+json.dumps(sendmany).replace('"', '\\"')+'"')
logger.info(f"Sendmany generated for {len(resp)} {season} {server} addresses to send {amount}")
