#!/usr/bin/env python3

import json
import requests
import logging
import logging.handlers
from lib_const import *
from models import coins_row
from lib_table_select import get_existing_notarised_txids, get_notarisations
from lib_table_update import update_score_notarised_tbl

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

coins_info = requests.get(f"{THIS_SERVER}/api/info/coins/").json()["results"][0]
txids = get_notarisations("Season_4")

for txid in txids:
	coin = txid["chain"]
	if coin in DPOW_EXCLUDED_CHAINS["Season_4"]:
		print("not Scored, excluded")
	else:
		try:
			ntx_block_time = txid["block_time"]
			try:
				dpow_tenure = coins_info[coin]["dpow_tenure"]["Season_4"]
			except:
				dpow_tenure = coins_info[TRANSLATE_COINS[coin]]["dpow_tenure"]["Season_4"]
			tenure_start_time = dpow_tenure["first_ntx_block_time"]
			tenure_end_time = dpow_tenure["last_ntx_block_time"]
			if ntx_block_time >= tenure_start_time and ntx_block_time <= tenure_end_time:
				update_score_notarised_tbl(txid["txid"], True)
			else:
				update_score_notarised_tbl(txid["txid"], False)

		except Exception as e:
			print(e)
			input()



