#!/usr/bin/env python3
import sys
import logging
import logging.handlers

from lib_notary import get_server_active_dpow_chains_at_time, get_dpow_score_value, \
get_season_from_addresses, get_notarised_data
from lib_const import *
from lib_table_update import *
from lib_table_select import *
from lib_api import *
from models import get_chain_epoch_at


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# recorded_txids = get_existing_notarised_txids()

deleted = {}

assert_results = []
'''
for item in ["chain", "season", "server", "scored", "btc_validated"]:

            print(f"{item} in DB:")
            CURSOR.execute(f"SELECT DISTINCT {item} FROM notarised;")
            cat_rows = CURSOR.fetchall()
            print(cat_rows)
'''
    

# Validate correct servers

notarised_seasons = get_notarised_seasons()

for season in notarised_seasons:
    
    try:
        assert season in list(SEASONS_INFO.keys()) or season == "Unofficial"
        assert_results.append({f"{season} in SEASONS_INFO: Pass"})
    except:
        assert_results.append({f"{season} in SEASONS_INFO: Fail"})

    if season != "Unofficial":
        notarised_chains = get_notarised_chains(season)
        tenure_chains = get_tenure_chains(season)
        if season not in ["Season_1", "Season_2", "Season_3", "Unofficial"]:
            try:
                assert notarised_chains == tenure_chains
                assert_results.append({f"{season} notarised_chains == tenure_chains: Pass"})
            except:
                assert_results.append({f"{season} notarised_chains == tenure_chains: Fail"})

            

        for chain in notarised_chains:
            if season in DPOW_EXCLUDED_CHAINS: 
                if chain in DPOW_EXCLUDED_CHAINS[season]:
                    print(f"{chain} excluded from {season}, updating...")
                    print(f">>> Updating Server... Unofficial {chain} Unofficial")
                    update_unofficial_chain_notarised_tbl(season, chain)


    
    servers = get_notarised_servers(season)
    try:
        assert server in ["Main", "Third_Party", "Testnet", "Unofficial"]
        assert_results.append({f"{season} server catgories valid: Pass"})
    except:
        assert_results.append({f"{season} server catgories valid: Fail"})
        
# Validate BTC scores
CURSOR.execute(f"SELECT DISTINCT score_value \
                 FROM notarised \
                 WHERE season = 'Season_4' \
                 AND chain = 'BTC';")
btc_scores = CURSOR.fetchall()

try:
    assert len(btc_scores) == 1 and float(btc_scores[0][0]) == 0.03250000
    logger.info("BTC scores for Season 4 OK...")
    assert_results.append({"BTC scores valid: Pass"})
except Exception as e:
    logger.warning(">>> Fixing BTC scores for Season 4")
    assert_results.append({"BTC scores valid":"Fail (resolved)"})
    if len(btc_scores) > 1:
        update_chain_score_notarised_tbl("BTC", 0.03250000, SEASONS_INFO["Season_4"]["start_time"], SEASONS_INFO["Season_4"]["end_time"])

logger.info(f"Season 4 BTC scores validation complete!\n")
        
# Validate LTC scores
CURSOR.execute(f"SELECT DISTINCT score_value \
                 FROM notarised \
                 WHERE season = 'Season_5_Testnet' \
                 AND chain = 'LTC';")
ltc_scores = CURSOR.fetchall()

try:
    assert len(btc_scores) == 1 and float(btc_scores[0][0]) == 0.03250000
    logger.info("LTC scores for Season_5_Testnet OK...")
    assert_results.append({"LTC scores valid: Pass"})
except Exception as e:
    logger.warning(">>> Fixing LTC scores for Season_5_Testnet")
    assert_results.append({"LTC scores valid":"Fail (resolved)"})
    if len(ltc_scores) > 1:
        update_chain_score_notarised_tbl("LTC", 0.03250000, SEASONS_INFO["Season_5_Testnet"]["start_time"], SEASONS_INFO["Season_5_Testnet"]["end_time"])

logger.info(f"Season_5_Testnet LTC scores validation complete!\n")

# Validate Other scores
for season in SCORING_EPOCHS:
    if season not in ["Season_1", "Season_2", "Season_3", "Unofficial"]:
        for server in SCORING_EPOCHS[season]:

            for epoch in SCORING_EPOCHS[season][server]:

                epoch_start = SCORING_EPOCHS[season][server][epoch]["start"]
                epoch_end = SCORING_EPOCHS[season][server][epoch]["end"]
                epoch_midpoint = int((epoch_start + epoch_end)/2)
                epoch_active_chains, num_chains = get_server_active_dpow_chains_at_time(season, server, epoch_midpoint)
                server_tenure_chains = get_tenure_chains(season, server)
                if "BTC" in server_tenure_chains:
                    server_tenure_chains.remove("BTC")
                if "LTC" in server_tenure_chains:
                    server_tenure_chains.remove("LTC")
                try:
                    assert len(set(epoch_active_chains) - set(server_tenure_chains)) == 0
                    assert_results.append({"all epoch_active_chains in server_tenure_chains: Pass"})
                except:
                    assert_results.append({"all epoch_active_chains in server_tenure_chains: Fail"})

                logger.info(f"{season} {server} {epoch} server_tenure_chains epoch_match active_chains OK!")

                for chain in epoch_active_chains:

                    actual_score = get_dpow_score_value(season, server, chain, epoch_midpoint)
                    sql = f"SELECT DISTINCT score_value \
                                FROM notarised \
                                WHERE block_time >= {epoch_start} \
                                AND block_time <= {epoch_end} \
                                AND season = '{season}' \
                                AND chain = '{chain}';"

                    CURSOR.execute(sql)

                    scores = CURSOR.fetchall()

                    try:
                        assert len(scores) == 1 and float(scores[0][0]) == actual_score
                        assert_results.append({f"{chain} Scoring correct: Pass"})
                        logger.info(f"{chain} scores for {season} {server} {epoch} OK...")
                    except Exception as e:
                        logger.warning(f">>> Fixing {chain} scores for {season} {server} {epoch}")
                        update_chain_score_notarised_tbl(chain, actual_score, epoch_start, epoch_end)
                        assert_results.append({f"{chain} scoring incorrect":"Fail (resolved)"})

        logger.info(f"{season} Other scores validation complete!\n")

        CURSOR.execute(f"SELECT notary_addresses, season, chain, block_time, notaries, txid, server, scored, score_value, epoch \
                         FROM notarised \
                         WHERE season = '{season}' \
                         ORDER BY server DESC, chain DESC, block_time DESC;")
                        # ORDER BY server DESC, chain ASC, block_time DESC;")

        notarised_rows = CURSOR.fetchall()

        i = 0
        start = int(time.time())
        num_rows = len(notarised_rows)
        long_chain_names = []

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
            if len(chain) > 10:
                logger.warning(f"chain = {chain} for {txid}")
                long_chain_names.append(chain)

            block_time = item[3]
            notaries = item[4]
            txid = item[5]
            server = item[6]
            scored = item[7]
            score_value = item[8]
            epoch = item[9]

            logger.info(f"Processing {i}/{num_rows} | {chain} | {season} | {server} | {score_value} | {scored}")
            if chain not in ["KMD", "BTC"]:
                ntx_chain = "KMD"
            else:
                ntx_chain = chain

            address_season, address_server = get_season_from_addresses(address_list, block_time, ntx_chain, chain, txid, notaries)

            # Validate Season / Server from addresses
            if len(address_list) == 0:
                if chain == "BTC":
                    url = f"{THIS_SERVER}/api/info/nn_btc_txid?txid={txid}"
                    local_info = requests.get(url).json()["results"][0]
                    local_addresses = []
                    for item in local_info:
                        if item["input_index"] != -1:
                            local_addresses.append(item["address"])
                    notary_addresses = local_addresses
                    season, server = get_season_from_addresses(local_addresses, block_time, "BTC", "BTC", txid, notaries)
                    #tx_info = get_btc_tx_info(txid)
                    #address_list = tx_info['addresses']
                    #address_season, address_server = get_season_from_addresses(address_list, block_time, ntx_chain, chain, txid, notaries)
                    print(f">>> Updating Addresses... {chain} {txid} {address_season} {block_time} {address_season} {notaries} {local_addresses}")
                    update_season_server_addresses_notarised_tbl(txid, address_season, address_server, local_addresses)
                else:
                    row_data = get_notarised_data(txid)
                    if row_data is not None:
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

            actual_epoch = get_chain_epoch_at(address_season, address_server, chain, block_time)
            try:
                assert actual_epoch == epoch and epoch != ''
            except:
                print(f">>> Updating epoch... {chain} {txid} {address_season} {address_server} {actual_epoch} (not {epoch}) {block_time}")

                update_notarised_epoch(actual_epoch, None, None, None, txid)
                



print(get_notarised_chains())
print(deleted)
print(long_chain_names)
for result in assert_results:
    print(result)
print("Now run to resolve where repaired: ./cron_populate_epochs.py")
