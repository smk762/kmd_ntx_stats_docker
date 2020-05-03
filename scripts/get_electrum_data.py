#!/usr/bin/env python3
import requests

third_party_coins = ["AYA", "CHIPS", "EMC2", "GAME", "GIN", 'HUSH3']
antara_coins = ["AXO", "BET", "BOTS", "BTCH", "CCL", "COQUICASH", "CRYPTO", "DEX", "ETOMIC", "HODL", "ILN", "JUMBLR",
                "K64", "KOIN", "KSB", "KV", "MESH", "MGW", "MORTY", "MSHARK", "NINJA", "OOT", "OUR", "PANGEA", "PGT",
                "PIRATE", "REVS", "RFOX", "RICK", "SEC", "SUPERNET", "THC", "VOTE2020", "VRSC", "WLC21", "ZEXO",
                "ZILLA", "STBL"]
ex_antara_coins = ['CHAIN', 'GLXT', 'MCL', 'PRLPAY', 'COMMOD', 'DION',
                   'EQL', 'CEAL', 'BNTN', 'KMDICE', 'DSEC', "WLC"]
all_antara_coins = antara_coins + ex_antara_coins

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
