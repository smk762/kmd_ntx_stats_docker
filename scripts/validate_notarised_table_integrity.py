#!/usr/bin/env python3
import sys
import json

from lib_notary import get_server_active_dpow_chains_at_time, get_dpow_score_value, \
get_season_from_addresses, get_notarised_data
from lib_const import *
from lib_table_update import *
from lib_table_select import *
from lib_api import *
from models import *


def rescan_chain(season, chain):
    if chain in ["KMD", "BTC", "LTC"]:
        sql = f"SELECT txid, block_time  \
                FROM notarised \
                WHERE \
                chain = '{chain}' \
                AND block_time >= {SEASONS_INFO[season]['start_time']} \
                AND block_time <= {SEASONS_INFO[season]['end_time']};"
        CURSOR.execute(sql)
        results = CURSOR.fetchall()
        for item in results:

            row = notarised_row()
            row.txid = item[0]
            row.block_time = item[1]
            row.chain = chain
            row.season = season
            if chain in ["LTC", "BTC"]:
                row.score = False
                row.score_value = 0
            else:
                row.score = True
                row.score_value = 0.0325

            row.server = chain
            row.epoch = f"Epoch_{chain}"
            logger.info(f"{row.chain} {row.season} {row.server} {row.epoch} {row.score} {row.score_value}")
            row.update()




def validate_servers(season):
    logger.info(f"Validating servers for {season}...")

    results = {
        "PASS":[],
        "FAIL":[]
    }

    try:
        assert season in list(SEASONS_INFO.keys())
        results["PASS"].append({f"{season} in SEASONS_INFO": "Pass"})

    except:
        results["FAIL"].append({f"{season} in SEASONS_INFO": "Fail"})

    notarised_chains = get_notarised_chains(season)
    tenure_chains = get_tenure_chains(season)
    servers = get_notarised_servers(season)

    try:
        assert notarised_chains == tenure_chains
        results["PASS"].append({f"{season} notarised_chains == tenure_chains": "Pass"})

    except:
        results["FAIL"].append({f"{season} notarised_chains == tenure_chains": "Fail | {notarised_chains} vs {tenure_chains} "})

    for chain in notarised_chains:

        if chain in DPOW_EXCLUDED_CHAINS: 

            if chain in DPOW_EXCLUDED_CHAINS[season]:
                logger.info(f"{chain} excluded from {season}, updating...")
                logger.info(f">>> Updating Server... Unofficial {chain} Unofficial")
                update_unofficial_chain_notarised_tbl(season, chain)

    try:
        assert server not in EXCLUDED_SERVERS
        results["PASS"].append({f"{season} server categories valid": "Pass"})

    except:
        results["FAIL"].append({f"{season} server categories valid": "Fail"})

    return results

def validate_BTC_scores(season):
    logger.info(f"Validating BTC scores for {season}...")
    results = {
        "PASS":[],
        "FAIL":[]
    }

    CURSOR.execute(f"SELECT DISTINCT score_value \
                     FROM notarised \
                     WHERE chain = 'BTC' \
                     AND block_time >= 0 \
                     AND block_time <= 1917364800;")
    btc_scores = CURSOR.fetchall()

    if len(btc_scores) > 0:
        try:
            assert len(btc_scores) == 1 and float(btc_scores[0][0]) == 0
            logger.info(f"BTC scores for {season} OK...")
            results["PASS"].append({f"{season} BTC scores valid": "Pass"})

        except Exception as e:
            bad_scores = []
            for item in btc_scores:
                bad_scores.append(float(item[0]))
            logger.error(f">>> Fixing BTC scores for {season} | Set to 0 not {bad_scores}")
            results["FAIL"].append({f"{season} BTC scores valid":f"Fail (resolved) | Set to 0 not {bad_scores}"})
            if len(btc_scores) > 1:
                update_chain_score_notarised_tbl("BTC", 0, True, 0, 1917364800, season)
    else:
        logger.warning(f"Zero BTC scores for {season} {server} {epoch}!")

    logger.info(f"{season} BTC scores validation complete!\n")
    return results

def validate_KMD_scores(season):
    logger.info(f"Validating KMD scores for {season}...")
    results = {
        "PASS":[],
        "FAIL":[]
    }

    CURSOR.execute(f"SELECT DISTINCT score_value \
                     FROM notarised \
                     WHERE chain = 'KMD' \
                     AND block_time >= {SEASONS_INFO[season]['start_time']} \
                     AND block_time <= {SEASONS_INFO[season]['end_time']};")
    KMD_scores = CURSOR.fetchall()

    if len(KMD_scores) > 0:
        try:
            assert len(KMD_scores) == 1 and float(KMD_scores[0][0]) == 0.0325
            logger.info(f"KMD scores for {season} OK...")
            results["PASS"].append({f"{season} KMD scores valid": "Pass"})

        except Exception as e:
            bad_scores = []
            for item in KMD_scores:
                bad_scores.append(float(item[0]))
            logger.error(f">>> Fixing KMD scores for {season} | Set to 0.0325 not {bad_scores}")
            results["FAIL"].append({f"{season} KMD scores valid":f"Fail (resolved) | Set to 0.0325 not {bad_scores}"})
            if len(KMD_scores) > 1:
                update_chain_score_notarised_tbl("KMD", 0.03250000, True, SEASONS_INFO[season]["start_time"], SEASONS_INFO[season]["end_time"], season)
    else:
        logger.warning(f"Zero KMD scores for {season} {server} {epoch}!")

    logger.info(f"{season} KMD scores validation complete!\n")
    return results

def validate_LTC_scores(season):
    logger.info(f"Validating LTC scores for {season}...")
    results = {
        "PASS":[],
        "FAIL":[]
    }

    CURSOR.execute(f"SELECT DISTINCT score_value \
                     FROM notarised \
                     WHERE chain = 'LTC' \
                     AND block_time >= 0 \
                     AND block_time <= 1917364800;")
    ltc_scores = CURSOR.fetchall()

    if len(ltc_scores) > 0:
        try:
            assert len(ltc_scores) == 1 and float(ltc_scores[0][0]) == 0
            logger.info(f"LTC scores for {season} OK...")
            results["PASS"].append({f"{season} LTC scores valid": "Pass"})

        except Exception as e:
            bad_scores = []
            for item in ltc_scores:
                bad_scores.append(float(item[0]))
            logger.error(f">>> Fixing LTC scores for {season} | Set to 0 not {bad_scores}")
            results["FAIL"].append({f"{season} LTC scores valid":f"Fail (resolved) | Set to 0 not {bad_scores}"})
            if len(ltc_scores) > 1:
                update_chain_score_notarised_tbl("LTC", 0, False, 0, 1917364800, season)
    else:
        logger.warning(f"Zero LTC scores for {season} {server} {epoch}!")

    logger.info(f"{season} LTC scores validation complete!\n")
    return results

def validate_other_scores(season):
    results = {
        "PASS":[],
        "FAIL":[]
    }

    #for server in SCORING_EPOCHS[season]:
    for server in ["Third_Party"]:

        for epoch in SCORING_EPOCHS[season][server]:

            epoch_start = SCORING_EPOCHS[season][server][epoch]["start"]
            epoch_end = SCORING_EPOCHS[season][server][epoch]["end"]
            epoch_midpoint = int((epoch_start + epoch_end)/2)
            epoch_active_chains, num_chains = get_server_active_dpow_chains_at_time(season, server, epoch_midpoint)
            server_tenure_chains = get_tenure_chains(season, server)

            if "BTC" in server_tenure_chains:
                server_tenure_chains.remove("BTC")

            if "KMD" in server_tenure_chains:
                server_tenure_chains.remove("KMD")

            if "LTC" in server_tenure_chains:
                server_tenure_chains.remove("LTC")

            try:
                assert len(set(epoch_active_chains) - set(server_tenure_chains)) == 0
                results["PASS"].append({f"all {season} {server} {epoch} epoch_active_chains in server_tenure_chains": "Pass"})

            except:
                results["FAIL"].append({f"all {season} {server} {epoch} epoch_active_chains in server_tenure_chains": "Fail"})

            logger.info(f"{season} {server} {epoch} server_tenure_chains epoch_match active_chains OK!")

            for chain in epoch_active_chains:

                logger.info(f"Validating {chain} scores for {season} {server} {epoch}...")

                actual_score = get_dpow_score_value(season, server, chain, epoch_midpoint)
                sql = f"SELECT DISTINCT score_value \
                            FROM notarised WHERE \
                            season = '{season}' \
                            AND server = '{server}' \
                            AND epoch = '{epoch}' \
                            AND chain = '{chain}';"

                CURSOR.execute(sql)
                scores = CURSOR.fetchall()
                if len(scores) > 0:
                    try:
                        assert len(scores) == 1 and float(scores[0][0]) == actual_score
                        results["PASS"].append({f"{chain} Scoring correct": "Pass"})
                        logger.info(f"{chain} scores for {season} {server} {epoch} OK...")

                    except Exception as e:
                        bad_scores = []
                        for item in scores:
                            bad_scores.append(float(item[0]))
                        logger.error(f">>> Fixing {chain} scores for {season} {server} {epoch} | Set to {actual_score} not {bad_scores}")
                        update_chain_score_notarised_tbl(chain, actual_score, True, epoch_start, epoch_end, season, server, epoch)
                        results["FAIL"].append({f"{chain} {season} {server} {epoch} scoring incorrect":f"Fail (resolved) Set to {actual_score} not {bad_scores}"})
                else:
                    logger.warning(f"Zero {chain} scores for {season} {server} {epoch}!")


    logger.info(f"{season} Other scores validation complete!\n")
    return results

# TODO: handled in model, but might be good here too...
def validate_epochs(season):

    results = {
        "PASS":[],
        "FAIL":[]
    }

    for server in SCORING_EPOCHS[season]:
        logger.info(f"Validating {season} {server} epochs\n")
        for epoch in SCORING_EPOCHS[season][server]:
            epoch_start = SCORING_EPOCHS[season][server][epoch]["start"]
            epoch_end = SCORING_EPOCHS[season][server][epoch]["end"]
            epoch_midpoint = int((epoch_start + epoch_end)/2)
            epoch_active_chains, num_chains = get_server_active_dpow_chains_at_time(season, server, epoch_midpoint)
            server_tenure_chains = get_tenure_chains(season, server)

            for chain in epoch_active_chains:
                sql = f"SELECT txid  \
                            FROM notarised \
                            WHERE \
                            season = '{season}' \
                            AND epoch = 'Unofficial' \
                            AND chain = '{chain}' \
                            AND block_time >= '{epoch_start}' \
                            AND block_time <= '{epoch_end}' \
                            AND server = '{server}';"
                CURSOR.execute(sql)
                epochs = CURSOR.fetchall()

                if len(epochs) > 0:
                    score = get_dpow_score_value(season, server, chain, epoch_midpoint)
                    logger.warning(f"{len(epochs)} {chain} records with wrong epoch detected in {season} {server}...")
                    logger.error(f">>> Fixing {chain} epoch for {season} {server} | Set to {epoch} not Unofficial")
                    update_chain_notarised_epoch_window(chain, season, server, epoch, epoch_start, epoch_end, score, True)
                    results["FAIL"].append({f"{chain} {season} {server} epoch incorrect":f"Fail (resolved) Set to {epoch} not Unofficial"})
                else:
                    results["PASS"].append({f"{chain} {season} {server} epoch correct": "Pass"})
                    logger.info(f"{chain} {season} {server} {epoch} epoch OK...")

    logger.info(f"{season} Epoch validation complete!\n")
    return results


def validate_chains(season):

    results = {
        "PASS":[],
        "FAIL":[]
    }

    for server in SCORING_EPOCHS[season]:
        logger.info(f"Validating {season} {server} chains\n")
        for epoch in SCORING_EPOCHS[season][server]:
            epoch_start = SCORING_EPOCHS[season][server][epoch]["start"]
            epoch_end = SCORING_EPOCHS[season][server][epoch]["end"]
            epoch_midpoint = int((epoch_start + epoch_end)/2)
            epoch_active_chains, num_chains = get_server_active_dpow_chains_at_time(season, server, epoch_midpoint)
            server_tenure_chains = get_tenure_chains(season, server)
            notarised_chains = get_notarised_chains(season, server)

            for chain in notarised_chains:
                if chain not in server_tenure_chains:
                    sql = f"SELECT txid  \
                                FROM notarised \
                                WHERE \
                                season = '{season}' \
                                AND epoch = '{epoch}' \
                                AND chain = '{chain}' \
                                AND block_time >= '{epoch_start}' \
                                AND block_time <= '{epoch_end}' \
                                AND server = '{server}';"
                    CURSOR.execute(sql)
                    epochs = CURSOR.fetchall()

                    if len(epochs) > 0:
                        logger.warning(f"{len(epochs)} {chain} records with wrong epoch detected in {season} {server}...")
                        logger.error(f">>> Fixing {chain} epoch for {season} {server} | Set to {epoch} Unofficial")
                        update_chain_notarised_epoch_window(chain, season, server, epoch, epoch_start, epoch_end, 0, False)
                        results["FAIL"].append({f"{chain} {season} {server} epoch incorrect":f"Fail (resolved) Set to {epoch} Unofficial"})
                    else:
                        results["PASS"].append({f"{chain} {season} {server} epoch correct": "Pass"})
                        logger.info(f"{chain} {season} {server} {epoch} epoch OK...")

    logger.info(f"{season} {server} {epoch} Chain validation complete!\n")
    return results

def zero_unofficial_notarisation_scores():

        sql = f"SELECT score_value, scored  \
                    FROM notarised \
                    WHERE \
                    (season = 'Unofficial' \
                    OR server = 'Unofficial' \
                    OR epoch = 'Unofficial') \
                    AND \
                    (score_value != 0 \
                    OR scored = True );"
        CURSOR.execute(sql)
        scores = CURSOR.fetchall()

        if len(scores) > 0:
            logger.warning(f"{len(scores)} Unofficial scores detected - zeroing them out...")

            sql = f"UPDATE notarised SET scored={False}, score_value=0  \
                        WHERE \
                        (season = 'Unofficial' \
                        OR server = 'Unofficial' \
                        OR epoch = 'Unofficial') \
                        AND \
                        (score_value != 0 \
                        OR scored = True );"
            CURSOR.execute(sql)
            CONN.commit()
        else:
            logger.warning(f"{len(scores)} Unofficial scores detected!")

def validate_addresses(season):
    results = {}

    CURSOR.execute(f"SELECT notarised, season, chain, block_time, notaries, txid, server, scored, score_value, epoch \
                     FROM notarised \
                     WHERE season = '{season}' \
                     ORDER BY server DESC, chain DESC, block_time DESC;")

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
            logger.info(f"Processing {i}/{num_rows} | {chain} | {season} | {server} ")
            
        address_list = item[0]
        season = item[1]
        chain = item[2]
        block_time = item[3]
        notaries = item[4]
        txid = item[5]
        server = item[6]
        scored = item[7]
        score_value = item[8]
        epoch = item[9]

        ntx_chain = chain

        address_season, address_server = get_season_from_addresses(address_list, block_time, ntx_chain, chain, txid, notaries)

        if len(address_list) == 0:
            logger.warning(f">>> Updating missing addresses for {chain}: {txid}")

            if chain == "BTC":
                url = f"{THIS_SERVER}/api/info/nn_btc_txid?txid={txid}"
                local_info = requests.get(url).json()["results"][0]
                notary_addresses = []

                for item in local_info:
                    if item["input_index"] != -1:
                        local_addresses.append(item["address"])

                update_season_server_addresses_notarised_tbl(txid, address_season, address_server, notary_addresses)
                logger.warning(f">>> Updated missing addresses | {chain} {txid} {address_season} {block_time} {address_season} {notaries} {notary_addresses}")

            else:
                row_data = get_notarised_data(txid)

                if row_data is not None:
                    address_list = row_data[6]
                    address_season = row_data[11]
                    address_server = row_data[12]
                    
                    update_season_server_addresses_notarised_tbl(txid, address_season, address_server, address_list)
                    logger.warning(f">>> Updated missing addresses | {chain} {txid} {address_season} {block_time} {address_season} {notaries} {address_list}")


        if season != address_season:
            update_season_server_addresses_notarised_tbl(txid, address_season, address_server, address_list)
            logger.warning(f">>> Updated Season... {chain} {txid} {address_season} {block_time} {address_season} {notaries} {address_list}")

        elif server != address_server:
            update_season_server_addresses_notarised_tbl(txid, address_season, address_server, address_list)
            logger.warning(f">>> Updated Server... {chain} {txid} {address_server} {block_time} {address_server} {notaries} {address_list}")

        actual_epoch = get_chain_epoch_at(address_season, address_server, chain, block_time)

        try:
            assert actual_epoch == epoch and epoch != ''
        except:
            update_notarised_epoch(actual_epoch, None, None, None, txid)
            logger.info(f">>> Updating epoch... {chain} {txid} {address_season} {address_server} {actual_epoch} (not {epoch}) {block_time}")

    return results


if __name__ == "__main__":

    Failed = None

    for chain in ["BTC", "KMD", "LTC"]:
        sql = f"UPDATE notarised SET server='{chain}' \
              WHERE chain='{chain}';"
        try:
            CURSOR.execute(sql)
            CONN.commit()
            print(f"{chain} server updated to {chain}")
        except Exception as e:
            logger.debug(e)
            CONN.rollback()

    for season in get_notarised_seasons():
        if season in DPOW_EXCLUDED_CHAINS:
            for chain in DPOW_EXCLUDED_CHAINS[season]:
                if chain in get_notarised_chains(season):
                    logger.warning(f"Setting {season} {chain} to Unofficial")
                    update_unofficial_chain_notarised_tbl(season, chain)
                    row = ntx_tenure_row()
                    row.delete(season, None, chain)

        zero_unofficial_notarisation_scores()

        assert_results = {}
        notarised_seasons = get_notarised_seasons()

        for season in notarised_seasons:
            if season not in EXCLUDED_SEASONS:
                #for chain in ["KMD", "BTC", "LTC"]:
                #    rescan_chain(season, chain)
                assert_results.update({"validate_servers":validate_servers(season)})
                assert_results.update({"validate_epochs":validate_epochs(season)}) 
                assert_results.update({"validate_chains":validate_chains(season)}) 
                assert_results.update({"validate_BTC_scores":validate_BTC_scores(season)}) 
                assert_results.update({"validate_LTC_scores":validate_LTC_scores(season)}) 
                assert_results.update({"validate_KMD_scores":validate_KMD_scores(season)}) 
                assert_results.update({"validate_other_scores":validate_other_scores(season)}) 


                # this takes a while, run if you have reason or periodically
                # assert_results += validate_addresses(season)

        with open("notarised_table_validation.json", "w") as f:
            json.dump(assert_results, f, indent=4)

        logger.info("Results saved to notarised_table_validation.json")
        for item in assert_results:
            if len(assert_results[item]["FAIL"]) > 0:
                for result in assert_results[item]["FAIL"]:
                    logger.warning(result)
                    Failed = True

        if not Failed:
            logger.info("All tests Passed!")