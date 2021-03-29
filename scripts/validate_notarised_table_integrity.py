#!/usr/bin/env python3
import logging
import logging.handlers

from lib_notary import *
from lib_const import *
from lib_table_update import *
from lib_table_select import *
from lib_api import *


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# recorded_txids = get_existing_ntxids()
deleted = {}
'''
for item in ["chain", "season", "server", "scored", "btc_validated"]:

            print(f"{item} in DB:")
            CURSOR.execute(f"SELECT DISTINCT {item} FROM notarised;")
            cat_rows = CURSOR.fetchall()
            print(cat_rows)
'''
# Validate notry addresses match season


CURSOR.execute(f"SELECT notary_addresses, season, chain, block_time, notaries, txid, server, scored, score_value \
				 FROM notarised \
				 WHERE season = 'Season_4' \
				 ORDER BY block_time DESC;")

address_season_rows = CURSOR.fetchall()

for item in address_season_rows:
	
	address_list = item[0]
	season = item[1]
	chain = item[2]
	block_time = item[3]
	notaries = item[4]
	txid = item[5]
	server = item[6]
	scored = item[7]
	score_value = item[8]

	if chain not in ["KMD", "BTC"]:
		ntx_chain = "KMD"

	else:
		ntx_chain = chain

	address_season, address_server = get_season_from_addresses(address_list, block_time, ntx_chain, chain, txid, notaries)

	if address_season == "Season_4":
		if len(address_list) == 0:
			delete_txid_from_notarised_tbl(txid)
			print(f">>> DELETING {chain} {txid} {season} {block_time} {address_season} {notaries} {address_list}")
			if chain not in deleted:
				deleted.update({chain:[]})
			deleted[chain].append(txid)

		elif season != address_season:
			print(f">>> Updating... {chain} {txid} {address_season} {block_time} {address_season} {notaries} {address_list}")
			update_season_notarised_tbl(txid, address_season, address_server)

		elif server != address_server:
			print(f">>> Updating Server... {chain} {txid} {address_server} {block_time} {address_server} {notaries} {address_list}")
			update_season_notarised_tbl(txid, address_season, address_server)

		# Check server ok at blocktime
		validate_score_value = get_dpow_score_value(address_season, address_server, chain, block_time)

		if validate_score_value > 0:
			validate_scored = True
		else:
			validate_scored = False

			print(f">>> Updating Score Value... {chain} {txid} {address_season} {address_server} {block_time} {validate_scored} {validate_score_value}")
		if validate_scored != scored:
			print(f">>> Updating Score... {chain} {txid} {address_season} {address_server} {block_time} {validate_scored} {validate_score_value}")
			update_score_notarised_tbl(txid, validate_scored, validate_score_value)
			
		elif validate_score_value != score_value:
			print(f">>> Updating Score Value... {chain} {txid} {address_season} {address_server} {block_time} {validate_scored} {validate_score_value}")
			update_score_notarised_tbl(txid, validate_scored, validate_score_value)

		print("\n")

print(deleted)