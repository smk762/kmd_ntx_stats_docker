#!/usr/bin/env python3
import requests
from coins_lib import third_party_coins, antara_coins, ex_antara_coins, all_antara_coins, all_coins

ac_block_ht = {}
for chain in antara_coins:
	try:
		url = 'http://'+chain.lower()+'.explorer.dexstats.info/insight-api-komodo/sync'
		r = requests.get(url)
		ac_block_ht.update({chain:r.json()['blockChainHeight']})
	except Exception as e:
		print(chain+" failed")
		print(e)
print(block_heights)
