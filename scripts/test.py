#!/usr/bin/env python3
import sys
from lib_const import SCORING_EPOCHS, NOTARY_PUBKEYS, CURSOR, CONN, SEASONS_INFO
from lib_table_select import *
from lib_notary import get_dpow_scoring_window
from models import get_chain_epoch_at, get_chain_epoch_score_at

import logging
import logging.handlers

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

all_notarised_seasons = get_notarised_seasons()
all_notarised_servers = get_notarised_servers()
all_notarised_epochs = get_notarised_epochs()
all_notarised_chains = get_notarised_chains()

def get_notarisation_data(min_time, max_time):

    sql = f"SELECT chain, notaries, \
                    season, server, epoch, score_value \
                     FROM notarised"
    where = []
    if min_time:
        where.append(f"block_time >= '{min_time}'")
    if max_time:
        where.append(f"block_time <= '{max_time}'")

    if len(where) > 0:
        sql += " WHERE "
        sql += " AND ".join(where)    
    sql += ";"

    ntx_summary = {}
    chain_totals = {}
    
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

            if chain in ["BTC", "LTC"]:
                server = chain

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

            if "Unofficial" not in [season, server, epoch]:
                for notary in notaries:
                    if notary not in ntx_summary:
                        ntx_summary.update({
                            notary:{
                                "seasons": {
                                    season: {
                                        "servers": {
                                            server: {
                                                "epochs": {
                                                    epoch:{
                                                        "chains": {
                                                            chain:{
                                                                "chain_ntx_count":0,
                                                                "chain_ntx_score_sum":0
                                                            }                                                    
                                                        },
                                                        "score_per_ntx":score_value,
                                                        "epoch_ntx_count":0,
                                                        "epoch_ntx_score_sum":0
                                                    }
                                                },
                                                "server_ntx_count":0,
                                                "server_ntx_score_sum":0
                                            }
                                        },
                                        "season_ntx_count":0,
                                        "season_ntx_score_sum":0
                                    }
                                },
                                "notary_ntx_count":0,
                                "notary_ntx_score_sum":0
                            }
                        })

                    if season not in ntx_summary[notary]["seasons"]:
                        ntx_summary[notary]["seasons"].update({
                            season: {
                                "servers": {
                                    server: {
                                        "epochs": {
                                            epoch:{
                                                "chains": {
                                                    chain:{
                                                        "chain_ntx_count":0,
                                                        "chain_ntx_score_sum":0
                                                    }                                                    
                                                },
                                                "score_per_ntx":score_value,
                                                "epoch_ntx_count":0,
                                                "epoch_ntx_score_sum":0
                                            }
                                        },
                                        "server_ntx_count":0,
                                        "server_ntx_score_sum":0
                                    }
                                },
                                "season_ntx_count":0,
                                "season_ntx_score_sum":0
                            }
                        })

                    if server not in ntx_summary[notary]["seasons"][season]["servers"]:
                        ntx_summary[notary]["seasons"][season]["servers"].update({
                            server: {
                                "epochs": {
                                    epoch:{
                                        "chains": {
                                            chain:{
                                                "chain_ntx_count":0,
                                                "chain_ntx_score_sum":0
                                            }                                                    
                                        },
                                        "epoch_ntx_count":0,
                                        "epoch_ntx_score_sum":0
                                    }
                                },
                                "server_ntx_count":0,
                                "server_ntx_score_sum":0
                            }
                        })

                    if epoch not in ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"]:
                        ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"].update({
                            epoch:{
                                "chains": {
                                    chain:{
                                        "chain_ntx_count":0,
                                        "chain_ntx_score_sum":0
                                    }                                                    
                                },
                                "score_per_ntx":score_value,
                                "epoch_ntx_count":0,
                                "epoch_ntx_score_sum":0
                            }
                        })

                    if chain not in ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"]:
                        ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"].update({
                            chain:{
                                "chain_ntx_count":0,
                                "chain_ntx_score_sum":0
                            }
                        })


                    ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["chain_ntx_count"] += 1
                    ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["chains"][chain]["chain_ntx_score_sum"] += score_value

                    ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["epoch_ntx_count"] += 1
                    ntx_summary[notary]["seasons"][season]["servers"][server]["epochs"][epoch]["epoch_ntx_score_sum"] += score_value

                    ntx_summary[notary]["seasons"][season]["servers"][server]["server_ntx_count"] += 1
                    ntx_summary[notary]["seasons"][season]["servers"][server]["server_ntx_score_sum"] += score_value

                    ntx_summary[notary]["seasons"][season]["season_ntx_count"] += 1
                    ntx_summary[notary]["seasons"][season]["season_ntx_score_sum"] += score_value

                    ntx_summary[notary]["notary_ntx_count"] += 1
                    ntx_summary[notary]["notary_ntx_score_sum"] += score_value

        return ntx_summary, chain_totals
        
    except Exception as e:
        logger.error(f"Error in get_epochs: {e}")
        return ntx_summary, chain_totals

print(get_all_coins())
print(all_notarised_chains)
print(all_notarised_servers)
print(all_notarised_epochs)
print(all_notarised_chains)

sys.exit()
notarisation_data, chain_totals = get_notarisation_data(SEASONS_INFO["Season_4"]["start_time"], SEASONS_INFO["Season_4"]["end_time"])

for notary in notarisation_data:
    if notary == "dragonhound_NA":
        print(f"'{notary}': {notarisation_data[notary]}\n")
        print(f"'{chain_totals}': {chain_totals}\n")

epochs = get_epochs()
print(epochs)

epochs = get_epochs("Season_5_Testnet", "Main")
print(epochs)

season = "Season_5_Testnet"
server = "Main"
chain = "LTC"
block_height = 1616445129

epoch = get_chain_epoch_at(season, server, chain, block_height)
print(epoch)
assert epoch == "Epoch_1"

score  = get_chain_epoch_score_at(season, server, chain, block_height)
print(score)
input()


print(f"SCORING_EPOCHS: {SCORING_EPOCHS}")
print()
print(f"SCORING_EPOCHS seasons: {SCORING_EPOCHS.keys()}")
print()
for season in list(SCORING_EPOCHS.keys()):
    print()
    print(f"SCORING_EPOCHS season {season} servers: {SCORING_EPOCHS[season].keys()}")
    for server in list(SCORING_EPOCHS[season].keys()):
        print(f"SCORING_EPOCHS season {season} servers: {SCORING_EPOCHS[season][server]}")
print()


epochs = get_epochs()
print(f"epochs: {epochs}")

for season in SEASONS_INFO:
    print()
    epochs = get_epochs(season)
    print(f"{season}: {epochs}")
input()

epochs = get_epochs("Season_5_Testnet", "Main")
print(epochs)

print(get_chain_epoch_at("Season_5_Testnet", "Main", "MORTY", 1617319854))

print(get_chain_epoch_score_at("Season_5_Testnet", "Main", "MORTY", 1617319854))
'''
get_tenure_chains("Season_4", "Third_Party")

official_start, official_end, scored_list, unscored_list = get_dpow_scoring_window("Season_4", "GLEEC", "Third_Party")

get_tenure_chains("Season_4", "Main")
official_start, official_end, scored_list, unscored_list = get_dpow_scoring_window("Season_4", "GLEEC", "Main")

get_tenure_chains("Season_4", "Unofficial")
official_start, official_end, scored_list, unscored_list = get_dpow_scoring_window("Season_4", "GLEEC", "Unofficial")
'''