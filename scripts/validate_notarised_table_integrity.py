#!/usr/bin/env python3
import sys
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

# recorded_txids = get_existing_notarised_txids()
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
    assert season in list(SEASONS_INFO.keys())
    servers = get_notarised_servers(season)
    logger.info(f"{season} servers: {servers}")
    for server in servers:
        assert server in ["Main", "Third_Party", "Testnet", "Unofficial"]

logger.info(f"Season / Server validation complete!\n")

        
# Validate BTC scores
CURSOR.execute(f"SELECT DISTINCT score_value \
                 FROM notarised \
                 WHERE season = 'Season_4' \
                 AND chain = 'BTC';")
btc_scores = CURSOR.fetchall()
print(f"BTC scores: {btc_scores}")

try:
    assert len(btc_scores) == 1 and float(btc_scores[0][0]) == 0.03250000
    logger.info("BTC scores for Season 4 OK...")
except Exception as e:
    logger.warning("Fixing BTC scores for Season 4")
    if len(btc_scores) > 1:
        update_chain_score_notarised_tbl("BTC", 0.03250000, SEASONS_INFO["Season_4"]["start_time"], SEASONS_INFO["Season_4"]["end_time"])

logger.info(f"Season 4 BTC scores validation complete!\n")

# Validate Other scores
for server in SCORING_EPOCHS["Season_4"]:

    for epoch in SCORING_EPOCHS["Season_4"][server]:

        epoch_start = SCORING_EPOCHS["Season_4"][server][epoch]["start"]
        epoch_end = SCORING_EPOCHS["Season_4"][server][epoch]["end"]
        epoch_midpoint = int((epoch_start + epoch_end)/2)
        active_chains, num_chains = get_server_active_dpow_chains_at_time("Season_4", server, epoch_midpoint)
        logger.info(f"epoch: {epoch}")
        logger.info(f"epoch_start: {epoch_start}")
        logger.info(f"epoch_end: {epoch_end}")
        logger.info(f"{num_chains} active at midpoint of {epoch} in Season_4 {server}")
        logger.info(f"active_chains: {active_chains}")

        for chain in active_chains:

            actual_score = get_dpow_score_value("Season_4", server, chain, epoch_midpoint)
            sql = f"SELECT DISTINCT score_value \
                        FROM notarised \
                        WHERE block_time >= {epoch_start} \
                        AND block_time <= {epoch_end} \
                        AND season = 'Season_4' \
                        AND chain = '{chain}';"

            CURSOR.execute(sql)

            scores = CURSOR.fetchall()

            try:
                assert len(scores) == 1 and float(scores[0][0]) == actual_score
                logger.info(f"{chain} scores for Season 4 {server} {epoch} OK...")
            except Exception as e:
                logger.warning(f"Fixing {chain} scores for Season 4 {server} {epoch}")
                update_chain_score_notarised_tbl(chain, actual_score, epoch_start, epoch_end)

logger.info(f"Season 4 Other scores validation complete!\n")

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


    logger.info(f"Processing {i}/{num_rows} | {chain} | {season} | {server} | {score_value} | {scored}")
    logger.info(f"addresses {address_list}")
    if chain not in ["KMD", "BTC"]:
        ntx_chain = "KMD"
    else:
        ntx_chain = chain

    address_season, address_server = get_season_from_addresses(address_list, block_time, ntx_chain, chain, txid, notaries)

    # Validate Season / Server from addresses
    if len(address_list) == 0:
        if chain == "BTC":
            tx_info = get_btc_tx_info(txid)
            address_list = tx_info['addresses']
            address_season, address_server = get_season_from_addresses(address_list, block_time, ntx_chain, chain, txid, notaries)
        else:
            row_data = get_notarised_data(txid)
            address_list = row_data[6]
            address_season = row_data[11]
            address_server = row_data[12]
        print(f">>> Updating Addresses... {chain} {txid} {address_season} {block_time} {address_season} {notaries} {address_list}")
        update_season_server_addresses_notarised_tbl(txid, address_season, address_server, address_list)


    elif season != address_season:
        print(f">>> Updating Season... {chain} {txid} {address_season} {block_time} {address_season} {notaries} {address_list}")
        update_season_server_addresses_notarised_tbl(txid, address_season, address_server, address_list)

    elif server != address_server:
        print(f">>> Updating Server... {chain} {txid} {address_server} {block_time} {address_server} {notaries} {address_list}")
        update_season_server_addresses_notarised_tbl(txid, address_season, address_server, address_list)



print(deleted)