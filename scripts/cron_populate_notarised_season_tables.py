#!/usr/bin/env python3
import os
import sys
import json
import random
import psycopg2
import threading
from decimal import *
from datetime import datetime as dt
import datetime
import dateutil.parser as dp
from lib_electrum import get_ac_block_info
from lib_const import *
from lib_notary import *
from lib_table_update import *
from lib_table_select import *
from lib_api import *
from lib_helper import *
from models import *

def get_season_ntx_dict(season):

    season_ntx_dict = {
        "season_ntx_count":0,
        "season_ntx_score":0,
        "chains":{},
        "servers":{},
        "notaries":{}
    }
    # Get Notary Totals
    notaries = list(NOTARY_PUBKEYS[season].keys())
    notaries.sort()
    for notary in notaries:
        season_ntx_dict["notaries"].update({
            notary: {
                "notary_ntx_count":0,
                "notary_ntx_score":0,
                "notary_ntx_count_pct":0,
                "notary_ntx_score_pct":0,
                "servers":{},
                "chains":{}
            }
        })
    servers = get_notarised_servers(season)
    for server in servers:
        season_ntx_dict["servers"].update({
            server: {
                "server_ntx_count":0,
                "server_ntx_score":0,
                "server_ntx_count_pct":0,
                "server_ntx_score_pct":0
            }
        })
        for notary in notaries:
            season_ntx_dict["notaries"][notary]["servers"].update({
                server: {
                    "notary_server_ntx_count":0,
                    "notary_server_ntx_score":0,
                    "notary_server_ntx_count_pct":0,
                    "notary_server_ntx_score_pct":0,
                    "epochs":{}
                }
            })
        epochs = get_notarised_epochs(season, server)
        for epoch in epochs:
            for notary in notaries:
                season_ntx_dict["notaries"][notary]["servers"][server]["epochs"].update({
                    epoch: {
                        "score_per_ntx":0,
                        "notary_server_epoch_ntx_count":0,
                        "notary_server_epoch_ntx_score":0,
                        "notary_server_epoch_ntx_count_pct":0,
                        "notary_server_epoch_ntx_score_pct":0,
                        "chains":{}
                    }
                })
            chains = get_notarised_chains(season, server, epoch)
            for chain in chains:
                for notary in notaries:
                    season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"].update({
                        chain: {
                            "notary_server_epoch_chain_ntx_count":0,
                            "notary_server_epoch_chain_ntx_score":0,
                            "notary_server_epoch_chain_ntx_count_pct":0,
                            "notary_server_epoch_chain_ntx_score_pct":0
                        }
                    })
                    if chain not in season_ntx_dict["notaries"][notary]["chains"]:
                        season_ntx_dict["notaries"][notary]["chains"].update({
                            chain: {
                                "notary_chain_ntx_count":0,
                                "notary_chain_ntx_score":0,
                                "notary_chain_ntx_count_pct":0,
                                "notary_chain_ntx_score_pct":0
                            }
                        })
                if chain not in season_ntx_dict["chains"]:
                    season_ntx_dict["chains"].update({
                        chain: {
                            "chain_ntx_count":0,
                            "chain_ntx_score":0,
                            "chain_ntx_count_pct":0,
                            "chain_ntx_score_pct":0,
                            "epochs":{}
                        }
                    })
                if epoch not in season_ntx_dict["chains"][chain]["epochs"]:
                    season_ntx_dict["chains"][chain]["epochs"].update({
                        epoch: {
                            "score_per_ntx":0,
                            "chain_epoch_ntx_count":0,
                            "chain_epoch_ntx_score":0,
                            "chain_epoch_ntx_count_pct":0,
                            "chain_epoch_ntx_score_pct":0
                        }

                    })
    i = 0
    for notary in notaries:
        i += 1
        logger.info(f"[season_totals] for {notary} {i}/{len(notaries)}")
        chain_totals = get_official_ntx_results(season, ["server", "epoch", "chain", "score_value"], None, None, None, notary)
        for item in chain_totals:
            server = item[0]
            epoch = item[1]
            chain = item[2]
            score_value = float(item[3])
            server_epoch_chain_count = item[4]
            server_epoch_chain_score = item[5]

            season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_count"] += server_epoch_chain_count
            season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_score"] += server_epoch_chain_score

            season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_count"] += server_epoch_chain_count
            season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_score"] += server_epoch_chain_score
            season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["score_per_ntx"] = score_value
            
            season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_count"] += server_epoch_chain_count
            season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_score"] += server_epoch_chain_score

            season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_count"] += server_epoch_chain_count
            season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_score"] += server_epoch_chain_score

            season_ntx_dict["notaries"][notary]["notary_ntx_count"] += server_epoch_chain_count
            season_ntx_dict["notaries"][notary]["notary_ntx_score"] += server_epoch_chain_score

            season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_count"] += server_epoch_chain_count
            season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_score"] += server_epoch_chain_score
            season_ntx_dict["chains"][chain]["epochs"][epoch]["score_per_ntx"] = score_value

            season_ntx_dict["chains"][chain]["chain_ntx_count"] += server_epoch_chain_count
            season_ntx_dict["chains"][chain]["chain_ntx_score"] += server_epoch_chain_score

            season_ntx_dict["servers"][server]["server_ntx_count"] += server_epoch_chain_count
            season_ntx_dict["servers"][server]["server_ntx_score"] += server_epoch_chain_score

            season_ntx_dict["season_ntx_count"] += server_epoch_chain_count
            season_ntx_dict["season_ntx_score"] += server_epoch_chain_score

    for notary in season_ntx_dict["notaries"]:
        season_ntx_dict["notaries"][notary]["notary_ntx_count_pct"] = round(safe_div(season_ntx_dict["notaries"][notary]["notary_ntx_count"],season_ntx_dict["season_ntx_count"])*100,3)
        season_ntx_dict["notaries"][notary]["notary_ntx_score_pct"] = round(safe_div(season_ntx_dict["notaries"][notary]["notary_ntx_score"],season_ntx_dict["season_ntx_score"])*100,3)
        season_ntx_dict["notaries"][notary]["notary_ntx_score"] = float(season_ntx_dict["notaries"][notary]["notary_ntx_score"])

        for chain in season_ntx_dict["notaries"][notary]["chains"]:
            season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_count_pct"] = round(safe_div(season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_count"],season_ntx_dict["season_ntx_count"])*100,3)
            season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_score_pct"] = round(safe_div(season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_score"],season_ntx_dict["season_ntx_score"])*100,3)
            season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_score"] = float(season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_score"])

        for server in season_ntx_dict["notaries"][notary]["servers"]:
            season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_count_pct"] = round(safe_div(season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_count"],season_ntx_dict["season_ntx_count"])*100,3)
            season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_score_pct"] = round(safe_div(season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_score"],season_ntx_dict["season_ntx_score"])*100,3)
            season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_score"] = float(season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_score"])

            for epoch in season_ntx_dict["notaries"][notary]["servers"][server]["epochs"]:
                season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_count_pct"] = round(safe_div(season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_count"],season_ntx_dict["season_ntx_count"])*100,3)
                season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_score_pct"] = round(safe_div(season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_score"],season_ntx_dict["season_ntx_score"])*100,3)
                season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_score"] = float(season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_score"])

                for chain in season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"]:
                    season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_count_pct"] = round(safe_div(season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_count"],season_ntx_dict["season_ntx_count"])*100,3)
                    season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_score_pct"] = round(safe_div(season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_score"],season_ntx_dict["season_ntx_score"])*100,3)
                    season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_score"] = float(season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_score"])


    for chain in season_ntx_dict["chains"]:
        season_ntx_dict["chains"][chain]["chain_ntx_count_pct"] = round(safe_div(season_ntx_dict["chains"][chain]["chain_ntx_count"],season_ntx_dict["season_ntx_count"])*100,3)
        season_ntx_dict["chains"][chain]["chain_ntx_score_pct"] = round(safe_div(season_ntx_dict["chains"][chain]["chain_ntx_score"],season_ntx_dict["season_ntx_score"])*100,3)
        season_ntx_dict["chains"][chain]["chain_ntx_score"] = float(season_ntx_dict["chains"][chain]["chain_ntx_score"])

        for epoch in season_ntx_dict["chains"][chain]["epochs"]:
            season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_count_pct"] = round(safe_div(season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_count"],season_ntx_dict["season_ntx_count"])*100,3)
            season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_score_pct"] = round(safe_div(season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_score"],season_ntx_dict["season_ntx_score"])*100,3)
            season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_score"] = float(season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_score"])

    for server in season_ntx_dict["servers"]:
        season_ntx_dict["servers"][server]["server_ntx_count_pct"] = round(safe_div(season_ntx_dict["servers"][server]["server_ntx_count"],season_ntx_dict["season_ntx_count"])*100,3)
        season_ntx_dict["servers"][server]["server_ntx_score_pct"] = round(safe_div(season_ntx_dict["servers"][server]["server_ntx_score"],season_ntx_dict["season_ntx_score"])*100,3)
        season_ntx_dict["servers"][server]["server_ntx_count"] = float(season_ntx_dict["servers"][server]["server_ntx_count"])

    season_ntx_dict["season_ntx_score"] = float(season_ntx_dict["season_ntx_score"])


    return season_ntx_dict


def update_notarised_chain_season(season):
    logger.info("Getting "+season+" season_notarised_counts")
    ac_block_heights = get_ac_block_info()

    results = get_chain_ntx_season_aggregates(season)

    for item in results:
        chain = item[0]
        block_height = item[1]
        max_time = item[2]
        ntx_count = item[3]
        cols = 'block_hash, txid, block_time, opret, ac_ntx_blockhash, ac_ntx_height'
        conditions = "block_height="+str(block_height)+" AND chain='"+chain+"'"
        try:
            last_ntx_result = select_from_table('notarised', cols, conditions)[0]
            kmd_ntx_blockhash = last_ntx_result[0]
            kmd_ntx_txid = last_ntx_result[1]
            kmd_ntx_blocktime = last_ntx_result[2]
            opret = last_ntx_result[3]
            ac_ntx_blockhash = last_ntx_result[4]
            ac_ntx_height = last_ntx_result[5]

            if chain in ac_block_heights:
                ac_block_height = ac_block_heights[chain]['height']
                ntx_lag = ac_block_height - ac_ntx_height
            else:
                ac_block_height = 0
                ntx_lag = "-"

            if run_updates():
                row = notarised_chain_season_row()
                row.chain = chain
                row.ntx_count = ntx_count
                row.block_height = block_height
                row.kmd_ntx_blockhash = kmd_ntx_blockhash
                row.kmd_ntx_txid = kmd_ntx_txid
                row.kmd_ntx_blocktime = kmd_ntx_blocktime
                row.opret = opret
                row.ac_ntx_blockhash = ac_ntx_blockhash
                row.ac_ntx_height = ac_ntx_height
                row.ac_block_height = ac_block_height
                row.ntx_lag = ntx_lag
                row.season = season
                row.server = server
                row.update()
        except Exception as e:
            logger.error(f"Exception in [update_season_notarised_counts] : {e}")



    logger.info(f"{season} season_notarised_counts complete")


def update_notarised_count_season(season):

    season_ntx_dict = get_season_ntx_dict(season)

    for notary in NOTARY_PUBKEYS[season]:

        season_ntx_count_row = notarised_count_season_row()
        season_ntx_count_row.time_stamp = time.time()
        season_ntx_count_row.notary = notary
        season_ntx_count_row.season = season

        if notary in season_ntx_dict["notaries"]:
            season_score = season_ntx_dict["notaries"][notary]["notary_ntx_score"]
            chain_ntx_counts = season_ntx_dict["notaries"][notary]
        else:
            season_score = 0
            chain_ntx_counts = {}

        chain_ntx_pct_dict = {}
        for chain in season_ntx_dict["chains"]:
            chain_ntx_pct_dict.update({
                chain: season_ntx_dict["chains"][chain]["chain_ntx_count_pct"]
            })

        btc_count = 0
        if "KMD" in season_ntx_dict["chains"]:
            btc_count = season_ntx_dict["notaries"][notary]["servers"]["KMD"]["epochs"]["KMD"]["notary_server_epoch_ntx_count"]

        antara_count = 0
        if "Main" in season_ntx_dict["servers"]:
            for epoch in season_ntx_dict["notaries"][notary]["servers"]["Main"]["epochs"]:
                if epoch != "Unofficial":
                    antara_count += season_ntx_dict["notaries"][notary]["servers"]["Main"]["epochs"][epoch]["notary_server_epoch_ntx_count"]

        third_party_count = 0
        if "Third_Party" in season_ntx_dict["servers"]:
            for epoch in season_ntx_dict["notaries"][notary]["servers"]["Third_Party"]["epochs"]:
                if epoch != "Unofficial":
                    third_party_count += season_ntx_dict["notaries"][notary]["servers"]["Third_Party"]["epochs"][epoch]["notary_server_epoch_ntx_count"]

        other_count = 0
        for server in season_ntx_dict["notaries"][notary]["servers"]:
            for epoch in ["Unofficial","BTC","LTC"]:
                if epoch in season_ntx_dict["notaries"][notary]["servers"][server]["epochs"]:
                    other_count += season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_count"]
                else:
                    logger.info(f'{notary} {server} not in season_ntx_dict["notaries"][notary]["servers"]')

        season_ntx_count_row.season_score = season_score
        season_ntx_count_row.btc_count = btc_count
        season_ntx_count_row.antara_count = antara_count
        season_ntx_count_row.third_party_count = third_party_count
        season_ntx_count_row.other_count = other_count
        season_ntx_count_row.total_ntx_count = btc_count+antara_count+third_party_count

        season_ntx_count_row.chain_ntx_counts = json.dumps(chain_ntx_counts)
        season_ntx_count_row.chain_ntx_pct = json.dumps(chain_ntx_pct_dict)
        season_ntx_count_row.update()


def update_notarised_count_season_OLD(season):

    ntx_summary, chain_totals = get_notarisation_data(season)
    chain_ntx_counts, notary_season_pct = get_notary_season_count_pct(season)
    for notary in ntx_summary:

        for summary_season in ntx_summary[notary]["seasons"]:
            logger.info(f"Getting season summary for {notary} {summary_season}")


            if notary in KNOWN_NOTARIES:

                season_ntx_count_row = notarised_count_season_row()
                season_ntx_count_row.notary = notary
                season_ntx_count_row.season = summary_season
                servers = ntx_summary[notary]["seasons"][summary_season]['servers']

                if "KMD" in servers:
                    season_ntx_count_row.btc_count = servers['KMD']['server_ntx_count']

                elif "LTC" in servers:
                    season_ntx_count_row.btc_count = servers['LTC']['server_ntx_count']

                else: 
                    season_ntx_count_row.btc_count = 0

                if 'Main' in servers:
                    season_ntx_count_row.antara_count = servers['Main']['server_ntx_count']

                else:
                    season_ntx_count_row.antara_count = 0

                if 'Third_Party' in servers:
                    season_ntx_count_row.third_party_count = servers['Third_Party']['server_ntx_count']

                else:
                    season_ntx_count_row.third_party_count = 0

                season_ntx_count_row.other_count = 0
                season_ntx_count_row.total_ntx_count = ntx_summary[notary]["seasons"][summary_season]['season_ntx_count']

                season_ntx_count_row.season_score = ntx_summary[notary]["seasons"][summary_season]["season_score"]
                season_ntx_count_row.chain_ntx_counts = json.dumps(ntx_summary[notary])
                season_ntx_count_row.chain_ntx_pct = json.dumps(notary_season_pct[notary])
                season_ntx_count_row.time_stamp = time.time()
                season_ntx_count_row.update()




def run_updates():
    return __name__ == "__main__"

if __name__ == "__main__":

    # Uncomment if record contains address rather than notary in [notaries] list (e.g. saved before pubkeys updated)
    # rescan_notaries(SEASON)

    start = time.time()
    seasons = get_notarised_seasons()
    end = time.time()
    logger.info(f">>> {end-start} sec to complete [get_notarised_seasons]")

    logger.info(f"Preparing to populate NTX tables...")

    for season in seasons:
        if season in ["Season_1", "Season_2", "Season_3", "Unofficial", "Season_5_Testnet"]:
            logger.warning(f"Skipping season: {season}")
        else:

            update_notarised_count_season(season)
            end = time.time()
            logger.info(f">>> {end-start} sec to complete [get_totals({season})]")

            start = end
            update_notarised_chain_season(season)
            end = time.time()
            logger.info(f">>> {end-start} sec to complete [update_notarised_chain_season({season})]")
            