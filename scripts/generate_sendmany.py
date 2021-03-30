#!/usr/bin/env python3

import sys
import json
import requests

try:
    chain = sys.argv[1]
    season = sys.argv[2]
    amount = float(sys.argv[3])
except:
    print("Needs season and chain params like 'generate_sendmany.py CHAIN Season_4 0.777")
    sys.exit()

r = requests.get(f"http://116.203.120.91:8762/api/info/addresses/?season={season}&chain={chain}")
resp = r.json()["results"][0]

addresses = []

for notary in resp:
    addresses.append(resp[notary][season]["addresses"][chain])

sendmany = {}
for address in addresses:
    sendmany.update({address:amount})

print(chain+' sendmany "" "'+json.dumps(sendmany).replace('"', '\\"')+'"')

