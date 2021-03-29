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

# Validate correct servers
notarised_seasons = get_notarised_seasons()
logger.info(f"notarised_seasons: {notarised_seasons}")
for season in notarised_seasons:
	servers = get_notarised_servers(season)
	logger.info(f"{season} servers: {servers}")
	for server in servers:
		assert server in ["Main", "Third_Party", "Testnet", "Unofficial"]
			

CURSOR.execute(f"SELECT DISTINCT score_value \
				 FROM notarised \
				 WHERE season = 'Season_4' and chain = 'BTC';")
btc_scores = CURSOR.fetchone()
print(f"BTC scores: {btc_scores}")
try:
	assert len(btc_scores) == 1 and btc_scores == 0.03250000
except:
	if len(btc_scores) > 1:
		update_chain_score_notarised_tbl("BTC", 0.03250000, SEASONS_INFO["Season_4"]["start_time"], SEASONS_INFO["Season_4"]["end_time"])


CURSOR.execute(f"SELECT notary_addresses, season, chain, block_time, notaries, txid, server, scored, score_value \
				 FROM notarised \
				 WHERE season = 'Season_4' \
				 ORDER BY server DESC, chain ASC, block_time DESC;")

notarised_rows = CURSOR.fetchall()


i = 0
start = int(time.time())
num_rows = len(notarised_rows)

for item in notarised_rows:
	i += 1
	logger.info(f"Processing {i}/{num_rows}")
	if i%100 == 0:
		now = int(time.time())
		duration = now - start
		pct_done = i/num_rows*100
		eta = duration*100/pct_done
		logger.info(f"{pct_done}% done. ETA {duration}/{eta} sec")
	address_list = item[0]
	season = item[1]
	chain = item[2]
	block_time = item[3]
	notaries = item[4]
	txid = item[5]
	server = item[6]
	scored = item[7]
	score_value = item[8]

	if server != "Unofficial":
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



			if chain != "BTC":
				validate_score_value = get_dpow_score_value(address_season, address_server, chain, block_time)

				if validate_score_value > 0:
					validate_scored = True
				else:
					validate_scored = False

					print(f">>> Updating Score Value... {chain} {txid} {address_season} {address_server} {block_time} {validate_scored} {validate_score_value}")
				if validate_scored != scored:
					print(f">>> Updating Score... {chain} {txid} {address_season} {address_server} {block_time} {validate_scored} {validate_score_value}")
					update_txid_score_notarised_tbl(txid, validate_scored, validate_score_value)
					
				elif validate_score_value != score_value:
					print(f">>> Updating Score Value... {chain} {txid} {address_season} {address_server} {block_time} {validate_scored} {validate_score_value}")
					update_txid_score_notarised_tbl(txid, validate_scored, validate_score_value)

				print("\n")

print(deleted)