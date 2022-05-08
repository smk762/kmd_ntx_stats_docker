#!/usr/bin/env python3

import sys
import json
import requests

coin = inut("Coin: ")
season = inut("Season: ")
server = inut("Server: ")
amount = inut("amount: ")

r = requests.get(f"http://116.203.120.91:8762/api/table/addresses/?season={season}&server={server}&coin={coin}")
resp = r.json()["results"]

addresses = []

for item in resp:
    if item['notary'] not in ['alrighttt_DEV', 'majora31_SH']:
        addresses.append(item["address"])

sendmany = {}
for address in addresses:
    sendmany.update({address:amount})

print(coin+' sendmany "" "'+json.dumps(sendmany).replace('"', '\\"')+'"')
print(f"Sendmany generated for {len(resp)} {season} {server} addresses to send {amount}")
