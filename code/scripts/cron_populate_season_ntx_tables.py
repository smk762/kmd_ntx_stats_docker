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

# Get total categorised count for all official chain notarisations
def get_official_ntx(season):
    official_ntx_results = get_official_ntx_results(season)
    official_ntx = {}
    for item in chain_season_ntx_result:
        chain = item[0]
        epoch = item[1]
        notaries = item[2]
        server = item[3]
        count = item[4]
        score_value = item[5]
        official_ntx.update({
            "chain":chain,
            "epoch":epoch,
            "notaries":notary,
            "server":server,
            "count":count,
            "score_value":score_value
        })
    return official_ntx

def get_official_ntx_dict(season):
    official_ntx = get_official_ntx(season)
    official_ntx_dict = {
        "season_ntx_count":0,
        "season_ntx_score":0,
        "servers": {},
        "notaries": {},
        "chains": {}
    }
    for item in official_ntx:
        server = item["server"]
        epoch = item["epoch"]
        chain = item["chain"]
        count = item["count"]
        score_value = item["score_value"]
        notaries = item["notaries"]

        for notary in notaries:

            # Season stats
            official_ntx_dict["season_ntx_count"] += count
            official_ntx_dict["season_ntx_score"] += score_value*count

            # Season chain stats
            if chain not in official_ntx_dict["chains"]:
                official_ntx_dict["chains"].update({
                    chain:{
                        "chain_ntx_count":0,
                        "chain_ntx_score":0
                    }
                })
            official_ntx_dict["chains"][chain]["chain_ntx_count"] += count
            official_ntx_dict["chains"][chain]["chain_ntx_score"] += score_value*count

            # Season notary stats
            if notary not in official_ntx_dict["notaries"]:
                official_ntx_dict["notaries"].update({
                    notary:{
                        "notary_ntx_count":0,
                        "notary_ntx_score":0
                    }
                })
            official_ntx_dict["notaries"][notary]["notary_ntx_count"] += count
            official_ntx_dict["notaries"][notary]["notary_ntx_score"] += score_value*count
            
            # Season server stats
            if server not in official_ntx_dict["servers"]:
                official_ntx_dict["servers"].update({
                    server:{
                        "server_ntx_count":0,
                        "server_ntx_score":0,
                        "epochs":{},
                        "chains":{},
                        "notaries":{}
                    }
                })
            official_ntx_dict["servers"][server]["server_ntx_count"] += count
            official_ntx_dict["servers"][server]["server_ntx_score"] += score_value*count

            # Season server notary stats
            if notary not in official_ntx_dict["servers"][server]["notaries"]:
                official_ntx_dict["servers"][server]["notaries"].update({
                    notary : {
                        "notary_ntx_count":0,
                        "notary_ntx_score":0
                    }
                })
            official_ntx_dict["servers"][server]["notaries"][notary]["notary_ntx_count"] += count
            official_ntx_dict["servers"][server]["notaries"][notary]["notary_ntx_score"] += score_value*count

            # Season server chain stats
            if chain not in official_ntx_dict["servers"][server]["chains"]:
                official_ntx_dict["servers"][server]["chains"].update({
                    chain : {
                        "chain_ntx_count":0,
                        "chain_ntx_score":0
                    }
                })
            official_ntx_dict["servers"][server]["chains"][chain]["chain_ntx_count"] += count
            official_ntx_dict["servers"][server]["chains"][chain]["chain_ntx_score"] += score_value*count
            
            # Season server epoch stats
            if epoch not in official_ntx_dict["servers"][server]["epochs"]:
                official_ntx_dict["servers"][server]["epochs"].update({
                    epoch: {
                        "epoch_ntx_count":0,
                        "epoch_ntx_score":0,
                        "notaries":{},
                        "chains":{}
                    }
                })
            official_ntx_dict["servers"][server]["epochs"][epoch]["epoch_ntx_count"] += count
            official_ntx_dict["servers"][server]["epochs"][epoch]["epoch_ntx_score"] += score_value*count

            # Season server epoch notary stats
            if notary not in official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"]:
                official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"].update({
                    notary: {
                        "notary_ntx_count":0,
                        "notary_ntx_score":0
                    }
                })
            official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["notary_ntx_count"] += count
            official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["notary_ntx_score"] += score_value*count

            # Season server epoch chain stats
            if chain not in official_ntx_dict["servers"][server]["epochs"][epoch]["chains"]:
                official_ntx_dict["servers"][server]["epochs"][epoch]["chains"].update({
                    chain: {
                        "chain_ntx_count":0,
                        "chain_ntx_score":0
                    }
                })
            official_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["chain_ntx_count"] += count
            official_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["chain_ntx_score"] += score_value*count
            
            # Season server epoch chain notary stats
            if notary not in official_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["notaries"]:
                official_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["notaries"].update({
                    notary: {
                        "notary_ntx_count":0,
                        "notary_ntx_score":0
                    }
                })
            official_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["notaries"][notary]["notary_ntx_count"] += count
            official_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["notaries"][notary]["notary_ntx_score"] += score_value*count

            # Season server epoch notary chain stats
            if chain not in official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["chains"]:
                official_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["notaries"].update({
                    chain: {
                        "chain_ntx_count":0,
                        "chain_ntx_score":0
                    }
                })
            official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["chains"][chain]["chain_ntx_count"] += count
            official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["chains"][chain]["chain_ntx_score"] += score_value*count

    return official_ntx_dict

def update_official_ntx_pct(official_ntx_dict):
    season_ntx_count = official_ntx_dict["season_ntx_count"]
    season_ntx_score = official_ntx_dict["season_ntx_score"]

    # Season chain pct
    for chain in official_ntx_dict["chains"]:
        chain_ntx_count = official_ntx_dict["chains"][chain]["chain_ntx_count"]
        chain_ntx_score = official_ntx_dict["chains"][chain]["chain_ntx_score"]
        official_ntx_dict["chains"][chain].update({
            "season_ntx_count_pct":chain_ntx_count/season_ntx_count,
            "season_ntx_score_pct":chain_ntx_score/season_ntx_score
        })

    # Season notary pct
    for notary in official_ntx_dict["notaries"]:
        notary_ntx_count = official_ntx_dict["notaries"][notary]["notary_ntx_count"]
        notary_ntx_score = official_ntx_dict["notaries"][notary]["notary_ntx_score"]
        official_ntx_dict["notaries"][notary].update({
            "season_ntx_count_pct":notary_ntx_count/season_ntx_count,
            "season_ntx_score_pct":notary_ntx_score/season_ntx_score
        })

    # Season notary pct
    for server in official_ntx_dict["servers"]:
        server_ntx_count = official_ntx_dict["servers"][server]["server_ntx_count"]
        server_ntx_score = official_ntx_dict["servers"][server]["server_ntx_score"]
        official_ntx_dict["servers"][server].update({
            "server_ntx_count_pct":server_ntx_count/season_ntx_count,
            "server_ntx_score_pct":server_ntx_score/season_ntx_score
        })

        # Season server notary stats
        for notary in official_ntx_dict["servers"][server]["notaries"]:
            notary_ntx_count = official_ntx_dict["servers"][server]["notaries"][notary]["notary_ntx_count"]
            notary_ntx_score = official_ntx_dict["servers"][server]["notaries"][notary]["notary_ntx_score"]
            official_ntx_dict["servers"][server]["notaries"][notary].update({
                "season_ntx_count_pct":notary_ntx_count/season_ntx_count,
                "season_ntx_score_pct":notary_ntx_score/season_ntx_score,
                "server_ntx_count_pct":notary_ntx_count/server_ntx_count,
                "server_ntx_score_pct":notary_ntx_score/server_ntx_score
            })

        # Season server chain stats
        for chain in official_ntx_dict["servers"][server]["chains"]:
            chain_ntx_count = official_ntx_dict["servers"][server]["chains"][chain]["chain_ntx_count"]
            chain_ntx_score = official_ntx_dict["servers"][server]["chains"][chain]["chain_ntx_score"]
            official_ntx_dict["servers"][server]["chains"][chain].update({
                "season_ntx_count_pct":chain_ntx_count/season_ntx_count,
                "season_ntx_score_pct":chain_ntx_score/season_ntx_score,
                "server_ntx_count_pct":chain_ntx_count/server_ntx_count,
                "server_ntx_score_pct":chain_ntx_score/server_ntx_score
            })

        # Season server epoch stats
        for epoch in official_ntx_dict["servers"][server]["epochs"]:
            epoch_ntx_count = official_ntx_dict["servers"][server]["epochs"][epoch]["epoch_ntx_count"]
            epoch_ntx_score = official_ntx_dict["servers"][server]["epochs"][epoch]["epoch_ntx_score"]
            official_ntx_dict["servers"][server]["epochs"][epoch].update({
                "season_ntx_count_pct":epoch_ntx_count/season_ntx_count,
                "season_ntx_score_pct":epoch_ntx_score/season_ntx_score,
                "server_ntx_count_pct":epoch_ntx_count/server_ntx_count,
                "server_ntx_score_pct":epoch_ntx_score/server_ntx_score
            })

            # Season server epoch notary stats
            for notary in official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"]:
                official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"].update({
                    notary: {
                        "notary_ntx_count":0,
                        "notary_ntx_score":0
                    }
                })
                notary_ntx_count = official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["notary_ntx_count"]
                notary_ntx_score = official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["notary_ntx_score"]
                official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary].update({
                    "season_ntx_count_pct":notary_ntx_count/season_ntx_count,
                    "season_ntx_score_pct":notary_ntx_score/season_ntx_score,
                    "server_ntx_count_pct":notary_ntx_count/server_ntx_count,
                    "server_ntx_score_pct":notary_ntx_score/server_ntx_score,
                    "epoch_ntx_count_pct":notary_ntx_count/epoch_ntx_count,
                    "epoch_ntx_score_pct":notary_ntx_score/epoch_ntx_score
                })

            # Season server epoch chain stats
            for chain in official_ntx_dict["servers"][server]["epochs"][epoch]["chains"]:
                chain_ntx_count = official_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["chain_ntx_count"]
                chain_ntx_score = official_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["chain_ntx_score"]
                official_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain].update({
                    "season_ntx_count_pct":chain_ntx_count/season_ntx_count,
                    "season_ntx_score_pct":chain_ntx_score/season_ntx_score,
                    "server_ntx_count_pct":chain_ntx_count/server_ntx_count,
                    "server_ntx_score_pct":chain_ntx_score/server_ntx_score,
                    "epoch_ntx_count_pct":chain_ntx_count/epoch_ntx_count,
                    "epoch_ntx_score_pct":chain_ntx_score/epoch_ntx_score
                })
            
            # Season server epoch chain notary stats
            if notary not in official_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["notaries"]:
                notary_ntx_count = official_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["notaries"][notary]["notary_ntx_count"]
                notary_ntx_score = official_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["notaries"][notary]["notary_ntx_score"]
                official_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["notaries"][notary].update({
                    "season_ntx_count_pct":notary_ntx_count/season_ntx_count,
                    "season_ntx_score_pct":notary_ntx_score/season_ntx_score,
                    "server_ntx_count_pct":notary_ntx_count/server_ntx_count,
                    "server_ntx_score_pct":notary_ntx_score/server_ntx_score,
                    "epoch_ntx_count_pct":notary_ntx_count/epoch_ntx_count,
                    "epoch_ntx_score_pct":notary_ntx_score/epoch_ntx_score
                })

            # Season server epoch notary chain stats
            if chain not in official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["chains"]:
                chain_ntx_count = official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["chains"][chain]["chain_ntx_count"]
                chain_ntx_score = official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["chains"][chain]["chain_ntx_score"]
                official_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["chains"][chain].update({
                    "season_ntx_count_pct":chain_ntx_count/season_ntx_count,
                    "season_ntx_score_pct":chain_ntx_score/season_ntx_score,
                    "server_ntx_count_pct":chain_ntx_count/server_ntx_count,
                    "server_ntx_score_pct":chain_ntx_score/server_ntx_score,
                    "epoch_ntx_count_pct":chain_ntx_count/epoch_ntx_count,
                    "epoch_ntx_score_pct":chain_ntx_score/epoch_ntx_score
                })

    return official_ntx_dict


def get_notarisation_percentages(official_ntx_counts):
    total_chain_ntx = {
        "total": 0,
        "chains": {}
    }
    total_epoch_ntx = {
        "total": 0,
        "epochs": {}
    }
    total_notary_ntx = {
        "total": 0,
        "notaries": {}
    }
    total_server_ntx = {
        "total": 0,
        "servers": {}
    }
    for item in official_ntx_counts:
        if item['chain'] not in total_chain_ntx["chains"]:
            total_chain_ntx["chains"].update({
                item['chain']:0
            })
        if item['epoch'] not in total_epoch_ntx["epochs"]:
            total_epoch_ntx["epochs"].update({
                item['epoch']:0
            })
        if item['notary'] not in total_notary_ntx["notaries"]:
            total_notary_ntx["notaries"].update({
                item['notary']:0
            })
        if item['server'] not in total_server_ntx["servers"]:
            total_server_ntx["servers"].update({
                item['server']:0
            })
        total_chain_ntx["chains"][item["chain"]] += 1
        total_epoch_ntx["epochs"][item["epoch"]] += 1
        total_notary_ntx["notaries"][item["notary"]] += 1
        total_server_ntx["servers"][item["server"]] += 1

        total_chain_ntx["total"] += 1
        total_epoch_ntx["total"] += 1
        total_notary_ntx["total"] += 1
        total_server_ntx["total"] += 1

    return {
        "total_chain_ntx":total_chain_ntx,
        "total_epoch_ntx":total_epoch_ntx,
        "total_notary_ntx":total_notary_ntx,
        "total_server_ntx":total_server_ntx,
    }


def get_notary_season_count_pct(season):
    season_chains = get_notarised_chains(season)
    season_notaries = NOTARY_PUBKEYS[season]
    
    season_main_coins = requests.get(f'{THIS_SERVER}/api/info/dpow_server_coins/?season={SEASON}&server=Main').json()["results"]
    season_3P_coins = requests.get(f'{THIS_SERVER}/api/info/dpow_server_coins/?season={SEASON}&server=Third_Party').json()["results"]

    total_chain_season_ntx = get_official_chain_ntx_totals(season)
    total_notary_chain_season_ntx = get_official_notary_chain_ntx_totals(season)

    notary_season_counts = {}
    results = get_ntx_for_season(season)

    for item in results:
        chain = item[0]
        notaries = item[1]

        for notary in notaries:
            if notary not in notary_season_counts:
                notary_season_counts.update({notary:{}})

            if chain not in notary_season_counts[notary]:
                notary_season_counts[notary].update({chain:1})
            else:
                notary_season_counts[notary][chain] += 1

    notary_season_count_notaries = list(notary_season_counts.keys())
    for notary in season_notaries:
        if notary not in notary_season_count_notaries:
            notary_season_counts.update({notary:{}})

        notary_season_count_notary_chains = list(notary_season_counts[notary].keys())
        for chain in season_chains:
            if chain not in notary_season_count_notary_chains:
                notary_season_counts[notary].update({chain:0})

        
    notary_season_pct = {}
    for notary in notary_season_counts:

        chain_ntx_counts = notary_season_counts[notary]
        btc_count = 0
        antara_count = 0
        third_party_count = 0
        other_count = 0
        total_ntx_count = 0

        if notary not in notary_season_pct:
            notary_season_pct.update({notary:{}})
        for chain in chain_ntx_counts:
            if chain == "KMD":
                btc_count += chain_ntx_counts[chain]
                total_ntx_count += chain_ntx_counts[chain]
            elif chain in season_3P_coins:
                third_party_count += chain_ntx_counts[chain]
                total_ntx_count += chain_ntx_counts[chain]
            elif chain in season_main_coins:
                antara_count += chain_ntx_counts[chain]
                total_ntx_count += chain_ntx_counts[chain]
            else:
                other_count += chain_ntx_counts[chain]

            pct = round(chain_ntx_counts[chain]/total_chain_season_ntx[chain]*100,3)
            notary_season_pct[notary].update({chain:pct})
 
    return chain_ntx_counts, notary_season_pct


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


def get_chain_ntx_pct_dict(official_ntx_dict):
    chain_ntx_pct_dict = {}
    for chain in official_ntx_dict["chains"]:
        pct = official_ntx_dict["chains"][chain]["season_ntx_count_pct"]
        chain_ntx_pct_dict.update({
            chain:pct
        })
    return chain_ntx_pct_dict

def update_notarised_count_season(season):

    official_ntx_dict = get_official_ntx_dict(season)
    official_ntx_dict = update_official_ntx_pct(official_ntx_dict)
    chain_ntx_pct_dict = get_chain_ntx_pct_dict(official_ntx_dict)

    for notary in NOTARY_PUBKEYS[season]:

        season_ntx_count_row = notarised_count_season_row()
        season_ntx_count_row.time_stamp = time.time()
        season_ntx_count_row.notary = notary
        season_ntx_count_row.season = season
        season_ntx_count_row.other_count = 0

        if notary in official_ntx_dict["notaries"]:
            season_score = official_ntx_dict["notaries"][notary]["notary_ntx_score"]
            chain_ntx_counts = official_ntx_dict["notaries"][notary]
        else:
            season_score = 0
            chain_ntx_counts = {}

        if "KMD" in official_ntx_dict["chains"]:
            btc_count = official_ntx_dict["chains"]["KMD"]["chain_ntx_count"]
        else:
            btc_count = 0

        if "Main" in official_ntx_dict["servers"]:
            antara_count = official_ntx_dict["servers"]["Main"]["server_ntx_count"]
        else:
            antara_count = 0

        if "Third_Party" in official_ntx_dict["servers"]:
            third_party_count = official_ntx_dict["servers"]["Third_Party"]["server_ntx_count"]
        else:
            third_party_count = 0

        season_ntx_count_row.season_score = season_score
        season_ntx_count_row.btc_count = btc_count
        season_ntx_count_row.antara_count = antara_count
        season_ntx_count_row.third_party_count = third_party_count
        season_ntx_count_row.total_ntx_count = btc_count+antara_count+third_party_count

        season_ntx_count_row.chain_ntx_counts = chain_ntx_counts
        season_ntx_count_row.chain_ntx_pct = chain_ntx_pct_dict
        season_ntx_count_row.update()



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


def make_ntx_summary_dict(season):
    ntx_summary = {}
    for notary in NOTARY_PUBKEYS[season]:
        if notary not in ntx_summary:
            ntx_summary.update({
                notary:{
                    "seasons": {
                        season: {
                            "servers": {},
                            "season_ntx_count":0,
                            "season_score":0,
                            "season_ntx_count_pct":0,
                            "season_score_pct":0,
                            "global_season_ntx_official_count":0,
                            "global_season_score":0
                        }
                    }
                }
            })

    notarised_servers = get_notarised_servers(season)
    for server in notarised_servers:
        if "Unofficial" not in [season, server]:
            logger.info(f"Adding notarised server {server}")
            for notary in NOTARY_PUBKEYS[season]:
                    if server not in ntx_summary[notary]["seasons"][season]["servers"]:
                        ntx_summary[notary]["seasons"][season]["servers"].update({
                            server: {
                                "epochs": {},
                                "chains": {},
                                "server_ntx_count":0,
                                "server_score":0,
                                "server_ntx_count_pct":0,
                                "server_score_pct":0,
                                "global_server_ntx_count":0,
                                "global_server_score":0
                            }
                        })

            epochs = get_notarised_epochs(season, server)
            for epoch in epochs:
                logger.info(f"Adding notarised server {server} epoch {epoch}")
                for notary in NOTARY_PUBKEYS[season]:
                    if epoch not in ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"]:
                        ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"].update({
                            epoch:{
                                "chains": {},
                                "score_per_ntx":0,
                                "epoch_ntx_count":0,
                                "epoch_score":0,
                                "epoch_ntx_count_pct":0,
                                "epoch_score_pct":0,
                                "global_server_epoch_ntx_count":0,
                                "global_server_epoch_score":0
                            }
                        })
                chains = get_notarised_chains(season, server, epoch)
                for chain in chains:
                    logger.info(f"Adding notarised server {server} epoch {epoch} chain {chain}")
                    for notary in NOTARY_PUBKEYS[season]:
                        if chain not in ntx_summary[notary]["seasons"][season]["servers"][server]["chains"]:
                            ntx_summary[notary]["seasons"][season]["servers"][server]["chains"].update({
                                chain:{
                                    "chain_ntx_count":0,
                                    "chain_score":0,
                                    "chain_ntx_count_pct":0,
                                    "chain_score_pct":0,
                                    "global_server_chain_ntx_count":0,
                                    "global_server_chain_score":0
                                }
                            })

                        if chain not in ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"]:
                            ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"].update({
                                chain:{
                                    "epoch_chain_ntx_count":0,
                                    "epoch_chain_score":0,
                                    "epoch_chain_ntx_count_pct":0,
                                    "epoch_chain_score_pct":0,
                                    "global_server_epoch_chain_ntx_count":0,
                                    "global_server_epoch_chain_score":0
                                }
                            })
    return ntx_summary


def get_notarisation_data(season, min_time=None, max_time=None, notary_name=None, chain_name=None, server_name=None, epoch_name=None):


    logger.info(f"Getting ntx data for {season}")

    sql = f"SELECT chain, notaries, \
                    season, server, epoch, score_value \
                     FROM notarised"
    where = []
    if season:
        where.append(f"season = '{season}'")
    if min_time:
        where.append(f"block_time >= {min_time}")
    if max_time:
        where.append(f"block_time <= {max_time}")
    if chain_name:
        where.append(f"chain = '{chain_name}'")
    if server_name:
        where.append(f"server = '{server_name}'")
    if epoch_name:
        where.append(f"epoch = '{epoch_name}'")

    if len(where) > 0:
        sql += " WHERE "
        sql += " AND ".join(where)
    sql += ";"

    logger.info(f"[get_notarisation_data] {where}")
    ntx_summary = make_ntx_summary_dict(season)
    chain_totals = {}
    global_totals = {}
    
    try:
        CURSOR.execute(sql)
        results = CURSOR.fetchall()

        for item in results:
            chain = item[0]
            notaries = item[1]
            season = item[2]
            server = item[3]
            epoch = item[4]
            score_value = round(float(item[5]), 8)

            if chain in ["BTC", "LTC", "KMD"]:
                server = chain
                epoch = chain
            if "Unofficial" not in [season, server]:

                if server not in chain_totals:
                    chain_totals.update({
                        server: {
                            chain: {
                                "count":0,
                                "total_score":0                        
                            }
                        }
                    })

                if chain not in chain_totals[server]:
                    chain_totals[server].update({
                        chain: {
                            "count":0,
                            "total_score":0
                        }
                    })

                chain_totals[server][chain]["count"] += 1
                chain_totals[server][chain]["total_score"] += score_value

                for notary in notaries:
                    if (notary_name is None or notary_name == notary) and (chain_name is None or chain_name == chain):

                        ntx_summary[notary]["seasons"][season]["season_ntx_count"] += 1
                        ntx_summary[notary]["seasons"][season]["season_score"] += score_value

                        ntx_summary[notary]["seasons"][season]["servers"][server]["server_ntx_count"] += 1
                        ntx_summary[notary]["seasons"][season]["servers"][server]["server_score"] += score_value

                        ntx_summary[notary]["seasons"][season]["servers"][server]["chains"][chain]["chain_ntx_count"] += 1
                        ntx_summary[notary]["seasons"][season]["servers"][server]["chains"][chain]["chain_score"] += score_value

                        ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["epoch_ntx_count"] += 1
                        ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["epoch_score"] += score_value

                        ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["epoch_chain_ntx_count"] += 1
                        ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["epoch_chain_score"] += score_value


        try:
            # Use one notary to calculate global totals
            global_notaries = list(NOTARY_PUBKEYS[season].keys())[0]
            logger.info(f"Getting notarisation data globals for {notary}")
            for season in ntx_summary[notary]["seasons"]:

                for notary_name in ntx_summary:
                    count = ntx_summary[notary_name]["seasons"][season]["season_ntx_count"]
                    score = ntx_summary[notary_name]["seasons"][season]["season_score"]
                    ntx_summary[global_notaries]["seasons"][season]["global_season_ntx_official_count"] += count
                    ntx_summary[global_notaries]["seasons"][season]["global_season_score"] += score
                    logger.info(f"{count}: count")
                    logger.info(f"{score}: score")
                    logger.info(f'{ntx_summary[global_notaries]["seasons"][season]["global_season_score"]}: ntx_summary[global_notaries]["seasons"][season]["global_season_score"]')
                    logger.info(f'{ntx_summary[global_notaries]["seasons"][season]["global_season_score"]}: ntx_summary[global_notaries]["seasons"][season]["global_season_score"]')

                logger.info(f"for server in {season}")
                for server in ntx_summary[notary]["seasons"][season]["servers"]:
                    for notary_name in ntx_summary:
                        count = ntx_summary[notary_name]["seasons"][season]["servers"][server]["server_ntx_count"]
                        score = ntx_summary[notary_name]["seasons"][season]["servers"][server]["server_score"]
                        ntx_summary[global_notaries]["seasons"][season]["servers"][server]["global_server_ntx_count"] += count
                        ntx_summary[global_notaries]["seasons"][season]["servers"][server]["global_server_score"] += score

                    logger.info(f"for chain in {season} {server}")
                    for chain in ntx_summary[notary]["seasons"][season]["servers"][server]["chains"]:
                        for notary_name in ntx_summary:

                            count = ntx_summary[notary_name]["seasons"][season]["servers"][server]["chains"][chain]["chain_ntx_count"]
                            score = ntx_summary[notary_name]["seasons"][season]["servers"][server]["chains"][chain]["chain_score"]
                            ntx_summary[global_notaries]["seasons"][season]["servers"][server]["chains"][chain]["global_server_chain_ntx_count"] += count
                            ntx_summary[global_notaries]["seasons"][season]["servers"][server]["chains"][chain]["global_server_chain_score"] += score

                    logger.info(f"for epoch in {season} {server}")
                    for epoch in ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"]:
                        if epoch != "Unofficial":
                            for notary_name in ntx_summary:

                                count = ntx_summary[notary_name]["seasons"][season]["servers"][server]["epochs"][epoch]["epoch_ntx_count"]
                                score = ntx_summary[notary_name]["seasons"][season]["servers"][server]["epochs"][epoch]["epoch_score"]
                                ntx_summary[global_notaries]["seasons"][season]["servers"][server]["epochs"][epoch]["global_server_epoch_ntx_count"] += count
                                ntx_summary[global_notaries]["seasons"][season]["servers"][server]["epochs"][epoch]["global_server_epoch_score"] += score

                            logger.info(f"for epoch chain in  {season} {server} {epoch}")
                            for chain in ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"]:
                                for notary_name in ntx_summary:

                                    count = ntx_summary[notary_name]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["epoch_chain_ntx_count"]
                                    score = ntx_summary[notary_name]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["epoch_chain_score"]
                                    ntx_summary[global_notaries]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["global_server_epoch_chain_ntx_count"] += count
                                    ntx_summary[global_notaries]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["global_server_epoch_chain_score"] += score

            # Apply global totals to all notaries
            for notary in ntx_summary:
                for season in ntx_summary[global_notaries]["seasons"]:
                    global_count = ntx_summary[global_notaries]["seasons"][season]["global_season_ntx_official_count"]
                    global_score = ntx_summary[global_notaries]["seasons"][season]["global_season_score"]
                    notary_count = ntx_summary[notary]["seasons"][season]["season_ntx_count"]
                    notary_score = ntx_summary[notary]["seasons"][season]["season_score"]
                    ntx_summary[notary]["seasons"][season]["season_ntx_count_pct"] = safe_div(notary_count,global_count)
                    ntx_summary[notary]["seasons"][season]["season_score_pct"] = safe_div(notary_score,global_score)
                    ntx_summary[notary]["seasons"][season]["global_season_ntx_official_count"] = global_count
                    ntx_summary[notary]["seasons"][season]["global_season_score"] = global_score

                    for server in ntx_summary[global_notaries]["seasons"][season]["servers"]:
                        global_count = ntx_summary[global_notaries]["seasons"][season]["servers"][server]["global_server_ntx_count"]
                        global_score = ntx_summary[global_notaries]["seasons"][season]["servers"][server]["global_server_score"]
                        notary_count = ntx_summary[notary]["seasons"][season]["servers"][server]["server_ntx_count"]
                        notary_score = ntx_summary[notary]["seasons"][season]["servers"][server]["server_score"]
                        ntx_summary[notary]["seasons"][season]["servers"][server]["server_ntx_count_pct"] = safe_div(notary_count,global_count)
                        ntx_summary[notary]["seasons"][season]["servers"][server]["server_score_pct"] = safe_div(notary_score,global_score)
                        ntx_summary[notary]["seasons"][season]["servers"][server]["global_server_ntx_count"] = global_count
                        ntx_summary[notary]["seasons"][season]["servers"][server]["global_server_score"] = global_score

                        for chain in ntx_summary[global_notaries]["seasons"][season]["servers"][server]["chains"]:
                            global_count = ntx_summary[global_notaries]["seasons"][season]["servers"][server]["chains"][chain]["global_server_chain_ntx_count"]
                            global_score = ntx_summary[global_notaries]["seasons"][season]["servers"][server]["chains"][chain]["global_server_chain_score"]
                            notary_count = ntx_summary[notary]["seasons"][season]["servers"][server]["chains"][chain]["chain_ntx_count"]
                            notary_score = ntx_summary[notary]["seasons"][season]["servers"][server]["chains"][chain]["chain_score"]
                            ntx_summary[notary]["seasons"][season]["servers"][server]["chains"][chain]["chain_ntx_count_pct"] = safe_div(notary_count,global_count)
                            ntx_summary[notary]["seasons"][season]["servers"][server]["chains"][chain]["chain_score_pct"] = safe_div(notary_score,global_score)
                            ntx_summary[notary]["seasons"][season]["servers"][server]["chains"][chain]["global_server_chain_ntx_count"] = global_count
                            ntx_summary[notary]["seasons"][season]["servers"][server]["chains"][chain]["global_server_chain_score"] = global_score

                        for epoch in ntx_summary[global_notaries]["seasons"][season]["servers"][server]["epochs"]:
                            global_count = ntx_summary[global_notaries]["seasons"][season]["servers"][server]["epochs"][epoch]["global_server_epoch_ntx_count"]
                            global_score = ntx_summary[global_notaries]["seasons"][season]["servers"][server]["epochs"][epoch]["global_server_epoch_score"]
                            notary_count = ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["epoch_ntx_count"]
                            notary_score = ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["epoch_score"]
                            ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["epoch_ntx_count_pct"] = safe_div(notary_count,global_count)
                            ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["epoch_score_pct"] = safe_div(notary_score,global_score)
                            ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["global_server_epoch_ntx_count"] = global_count
                            ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["global_server_epoch_score"] = global_score

                            for chain in ntx_summary[global_notaries]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"]:
                                global_count = ntx_summary[global_notaries]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["global_server_epoch_chain_ntx_count"]
                                global_score = ntx_summary[global_notaries]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["global_server_epoch_chain_score"]
                                notary_count = ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["epoch_chain_ntx_count"]
                                notary_score = ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["epoch_chain_score"]
                                ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["epoch_chain_ntx_count_pct"] = safe_div(notary_count,global_count)
                                ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["epoch_chain_score_pct"] = safe_div(notary_score,global_score)
                                ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["global_server_epoch_chain_ntx_count"] = global_count
                                ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["global_server_epoch_chain_score"] = global_score



        except Exception as e:
            logger.error(f"Error in [get_notarisation_data]: {e}")
            logger.error(f"Error in [get_notarisation_data]: {sql}")
            return ntx_summary, chain_totals

        return ntx_summary, chain_totals
        
    except Exception as e:
        logger.error(f"Error in [get_notarisation_data]: {e}")
        logger.error(f"Error in [get_notarisation_data]: {sql}")
        return ntx_summary, chain_totals


def run_updates():
    return __name__ == "__main__"

if __name__ == "__main__":

    # Uncomment if record contains address rather than notary in [notaries] list (e.g. saved before pubkeys updated)
    # rescan_notaries(SEASON)

    for chain in ["LTC","BTC","KMD"]:
        sql = f"UPDATE notarised SET epoch = '{chain}', server = '{chain}' WHERE chain = '{chain}';"
        print(sql)
        CURSOR.execute(sql)
        CONN.commit()


    seasons = get_notarised_seasons()
    logger.info(f"Preparing to populate NTX tables...")

    for season in seasons:
        if season in ["Season_1", "Season_2", "Season_3", "Unofficial", "Season_5_Testnet"]:
            logger.warning(f"Skipping season: {season}")
        else:
            if 'post_season_end_time' in SEASONS_INFO[season]:
                sql = f"UPDATE notarised SET epoch = 'Unofficial' WHERE season = '{season}' \
                        AND block_time >= {SEASONS_INFO[season]['end_time']} \
                        AND block_time <= {SEASONS_INFO[season]['post_season_end_time']};"
                print(sql)
                CURSOR.execute(sql)
                CONN.commit()

            start = time.time()
            update_notarised_count_season(season)
            end = time.time()
            logger.info(f">>> {end-start} sec to complete [update_notarised_count_season({season})]")

            start = end
            update_notarised_chain_season(season)
            end = time.time()
            logger.info(f">>> {end-start} sec to complete [update_notarised_chain_season({season})]")
    
    CURSOR.close()
    CONN.close()
