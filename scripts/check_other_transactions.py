#!/usr/bin/env python3
from lib_const import *
import requests
import json

r = requests.get(f"{THIS_SERVER}/api/info/notary_nodes/")
notaries = r.json()["results"][0]

notaries_with_others = {}
for notary in notaries:
    r = requests.get(f"{THIS_SERVER}/api/info/notary_btc_txids?notary={notary}")
    results = r.json()["results"]["Season_4"]
    print(f"Checking {notary}")
    if "Other" in results:
        txids = results["Other"]["txids"].keys()
        notaries_with_others.update({
            notary: {
                "count":len(txids),
                "txids":[]
                }
            })
        print(f"{notary} has {len(txids)} unrecognised transactions")
        for txid in txids:
            notaries_with_others[notary]['txids'].append(f"https://www.blockchain.com/btc/tx/{txid}")

print("\n Uncategorised Transactions")
for notary in notaries_with_others:
    print(f"{notary}")
    for txid in notaries_with_others[notary]['txids']:
        print(txid)

'''
for txid in [
    "37a3dea365c395ce77d196221d1fe6e02e909ae9fe2e93e2550bb221ebb5972f",
    "7eb2125b338b7d5a548253eedfccf4a665dd78e63490b78b7db3ec90288bc069",
    "2fd3e99bd7b19c1fbbcc5cc15f703c2c729ae2dd8bc924e3fec81e452f810e15",
    "3ef3e2e0e82f5a710538d32ce081fdd140a0679bcc36a32add49f65dee0430b2",
    "6f80a01c348b19255e5a1f2403aca5034d167d7daba7563fc30b7941465d3ea9",
    "37a3dea365c395ce77d196221d1fe6e02e909ae9fe2e93e2550bb221ebb5972f",
    "37a3dea365c395ce77d196221d1fe6e02e909ae9fe2e93e2550bb221ebb5972f",
    "37a3dea365c395ce77d196221d1fe6e02e909ae9fe2e93e2550bb221ebb5972f",
    "37a3dea365c395ce77d196221d1fe6e02e909ae9fe2e93e2550bb221ebb5972f",
    "37a3dea365c395ce77d196221d1fe6e02e909ae9fe2e93e2550bb221ebb5972f",
    "37a3dea365c395ce77d196221d1fe6e02e909ae9fe2e93e2550bb221ebb5972f",
    "37a3dea365c395ce77d196221d1fe6e02e909ae9fe2e93e2550bb221ebb5972f",
    "37a3dea365c395ce77d196221d1fe6e02e909ae9fe2e93e2550bb221ebb5972f",

]'''