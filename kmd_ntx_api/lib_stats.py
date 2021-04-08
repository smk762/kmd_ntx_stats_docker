#!/usr/bin/env python3

from kmd_ntx_api.lib_info import *

    
def get_region_score_stats(notarisation_scores):
    region_score_stats = {}
    for region in notarisation_scores:
        region_total = 0
        notary_count = 0
        for notary in notarisation_scores[region]:
            notary_count += 1
            region_total += notarisation_scores[region][notary]["score"]
        region_average = region_total/notary_count
        region_score_stats.update({
            region:{
                "notary_count": notary_count,
                "total_score": region_total,
                "average_score": region_average
            }
        })
    return region_score_stats


def get_top_region_notarisers(region_notary_ranks):
    top_region_notarisers = {
        "AR":{
        },
        "EU":{
        },
        "NA":{
        },
        "SH":{
        },
        "DEV":{
        }
    }
    top_ntx_count = {}
    for region in region_notary_ranks:
        if region not in top_ntx_count:
            top_ntx_count.update({region:{}})
        for notary in region_notary_ranks[region]:
            for chain in region_notary_ranks[region][notary]:
                if chain not in top_ntx_count:
                    top_ntx_count[region].update({chain:0})

                if chain not in top_region_notarisers[region]:
                    top_region_notarisers[region].update({chain:{}})

                ntx_count = region_notary_ranks[region][notary][chain]
                if ntx_count > top_ntx_count[region][chain]:
                    top_notary = notary
                    top_ntx_count[region].update({chain:ntx_count})
                    top_region_notarisers[region][chain].update({
                        "top_notary": top_notary,
                        "top_ntx_count": top_ntx_count[region][chain]

                    })
    return top_region_notarisers


def get_top_coin_notarisers(top_region_notarisers, chain):
    top_coin_notarisers = {}
    for region in top_region_notarisers:
        if chain in top_region_notarisers[region]:
            top_coin_notarisers.update({
                region:{
                    "top_notary": top_region_notarisers[region][chain]["top_notary"],
                    "top_ntx_count": top_region_notarisers[region][chain]["top_ntx_count"]
                }
            })
    return top_coin_notarisers


def get_daily_stats_sorted(season=None):
    if not season:
        season = "Season_4"

    notary_list = get_notary_list(season)
    
    mined_last_24hrs = get_mined_data_24hr().values('name').annotate(mined_24hrs=Sum('value'), blocks_24hrs=Count('value'))

    nn_mined_last_24hrs = {}
    for item in mined_last_24hrs:
        nn_mined_last_24hrs.update({item['name']:item['blocks_24hrs']})

    ntx_24hr = get_notarised_data_24hr().values()

    daily_stats = {}
    for notary_name in notary_list:
        region = get_notary_region(notary_name)
        notary_ntx_24hr_summary = get_notary_ntx_24hr_summary(ntx_24hr, notary_name)

        if region not in daily_stats:
            daily_stats.update({region:[]})

        if notary_name not in nn_mined_last_24hrs:
            nn_mined_last_24hrs.update({notary_name:0})

        daily_stats[region].append({
            "notary":notary_name,
            "btc":notary_ntx_24hr_summary["btc_ntx"],
            "main":notary_ntx_24hr_summary["main_ntx"],
            "third_party":notary_ntx_24hr_summary["third_party_ntx"],
            "mining":nn_mined_last_24hrs[notary_name],
            "score":notary_ntx_24hr_summary["score"]
        })

    daily_stats_sorted = {}
    for region in daily_stats:
        daily_stats_sorted.update({region:[]})
        scores_dict = {}
        for item in daily_stats[region]:
            scores_dict.update({item['notary']:item['score']})
        sorted_scores = {k: v for k, v in sorted(scores_dict.items(), key=lambda x: x[1])}
        dec_sorted_scores = dict(reversed(list(sorted_scores.items()))) 
        i = 1
        for notary in dec_sorted_scores:
            for item in daily_stats[region]:
                if notary == item['notary']:
                    new_item = item.copy()
                    new_item.update({"rank":i})
                    daily_stats_sorted[region].append(new_item)
            i += 1
    return daily_stats_sorted


# returns region > notary > chain > season ntx count
def get_coin_notariser_ranks(season):
    # season ntx stats
    ntx_season = get_notarised_count_season_data(season)
    season_chains = get_dpow_coins_list(season)
    ntx_season = ntx_season.values()

    if season == "Season_5_Testnet":
        region_notary_ranks = {
            "TESTNET":{}
        }
        notary_list = get_notary_list(season)
        dpow_coins = ["RICK", "MORTY", "LTC"]

        for notary in notary_list:
            region_notary_ranks["TESTNET"].update({notary:{}})

        for item in ntx_season:
            notary = item['notary']

            if notary in notary_list:
                for coin in item['chain_ntx_counts']:
                    if coin in dpow_coins:
                        region_notary_ranks[region][notary].update({
                            coin:item['chain_ntx_counts'][coin]
                        })
    else:
        region_notary_ranks = {
            "AR":{},
            "EU":{},
            "NA":{},
            "SH":{},
            "DEV":{}
        }
        notary_list = get_notary_list(season)
        dpow_coins = get_dpow_coins_list(season)
        for notary in notary_list:
            region = get_notary_region(notary)
            if region in ["AR","EU","NA","SH", "DEV"]:
                region_notary_ranks[region].update({notary:{}})
        for item in ntx_season:

            notary = item['notary']
            notary = item['notary']
            notary = item['notary']
            notary = item['notary']
            notary = item['notary']
            if notary in notary_list:
                for coin in item['chain_ntx_counts']:
                    if coin in dpow_coins:
                        region = get_notary_region(notary)
                        if region in ["AR","EU","NA","SH", "DEV"]:
                            region_notary_ranks[region][notary].update({
                                coin:item['chain_ntx_counts'][coin]
                            })
    return region_notary_ranks



def get_notarisation_scores(season):
    notarisation_scores = {}
    # set coins lists
    if not season:
        season = "Season_4"
    coin_notariser_ranks = get_coin_notariser_ranks(season)
    coins_dict = get_dpow_server_coins_dict(season)
    server_chains = get_server_chains(season)
    main_chains = get_mainnet_chains(coins_dict)
    third_chains = get_third_party_chains(coins_dict)

    # init scores dict
    for region in coin_notariser_ranks:
        notarisation_scores.update({region:{}})
        for notary in coin_notariser_ranks[region]:
            notarisation_scores[region].update({
                notary:{
                    "btc":0,
                    "main":0,
                    "third_party":0,
                    "mining":0
                }
            })
    # populate mining data
    mined_season = get_mined_season(season)

    for item in mined_season:
        notary = item["name"]
        region = get_notary_region(notary)
        if region in ["AR","EU","NA","SH", "DEV"]:
            blocks_mined = item["season_blocks_mined"]
            if notary in notarisation_scores[region]:
                notarisation_scores[region][notary].update({
                    "mining": blocks_mined
                })

    scores = get_notarised_count_season_data(season).values()

    # update chain / server counts
    for item in scores:
        notary = item['notary']
        try:
            region = get_notary_region(notary)
            notarisation_scores[region][notary].update({
                "btc":item["btc_count"]
            })
            notarisation_scores[region][notary].update({
                "main":item["antara_count"]
            })
            notarisation_scores[region][notary].update({
                "third_party":item["third_party_count"]
            })
            notarisation_scores[region][notary].update({
                "score":item["season_score"]
            })
            notarisation_scores[region][notary].update({
                "chain_counts":item["chain_ntx_counts"]
            })
        except Exception as e:
            logger.error(f"[get_notarisation_scores] Exception: {e}")
            pass


    # calc scores
    for region in notarisation_scores:
        for notary in notarisation_scores[region]:
            rank = 1
            for other_notary in notarisation_scores[region]:
                other_score = notarisation_scores[region][other_notary]["score"]
                score = notarisation_scores[region][notary]["score"]
                if other_score > score:
                    rank += 1
            notarisation_scores[region][notary].update({
                "rank": rank
            })


    return notarisation_scores


def get_notarised_season_score(season=None, chain=None):
    if not season:
        season = get_season()
    if not chain:
        chain = "KMD"

    notarised_data = get_notarised_data(season, chain).values()
 
    resp = {}
    for item in notarised_data:

        txid = item['txid']
        chain = item['chain']
        block_hash = item['block_hash']
        block_time = item['block_time']
        block_datetime = item['block_datetime']
        block_height = item['block_height']
        notaries = item['notaries']
        notary_addresses = item['notary_addresses']
        ac_ntx_blockhash = item['ac_ntx_blockhash']
        ac_ntx_height = item['ac_ntx_height']
        opret = item['opret']
        season = item['season']
        server = item['server']
        scored = item['scored']
        score_value = item['score_value']
        btc_validated = item['btc_validated']

        if chain == "BTC":
            server = "BTC"
            epoch_id = "epoch_BTC"
        if chain == "KMD":
            server = "KMD"
            epoch_id = "epoch_KMD"

        else:
            epoch_id = get_epoch_id(season, server, block_time)

        if not epoch_id:
            logger.warning(f"[get_notarised_season_score] no epoch for txid {txid}")

        else:
            for notary in notaries:
                if notary not in resp:
                    resp.update({
                        notary:{
                            "servers": {
                                server:{
                                    "epochs":{
                                        epoch_id:{
                                            "chains": {
                                                chain:{
                                                    "chain_ntx":0,
                                                    "chain_score":0
                                                },
                                            },
                                            "epoch_ntx":0,
                                            "epoch_score":0
                                        }
                                    },
                                    "server_ntx":0,
                                    "server_score":0
                                }
                            },
                            "season_score":0
                        }
                    })

                if server not in resp[notary]["servers"]:
                    resp[notary]["servers"].update({
                        server:{
                            "epochs":{
                                epoch_id:{
                                    "chains": {
                                        chain:{
                                            "chain_ntx":0,
                                            "chain_score":0
                                        },
                                    },
                                    "epoch_ntx":0,
                                    "epoch_score":0
                                }
                            },
                            "server_ntx":0,
                            "server_score":0
                        }
                    })

                if epoch_id not in resp[notary]["servers"][server]["epochs"]:
                    resp[notary]["servers"][server]["epochs"].update({
                        epoch_id:{
                            "chains": {
                                chain:{
                                    "chain_ntx":0,
                                    "chain_score":0
                                },
                            },
                            "epoch_ntx":0,
                            "epoch_score":0
                        }
                    })

                if chain not in resp[notary]["servers"][server]["epochs"][epoch_id]["chains"]:
                    resp[notary]["servers"][server]["epochs"][epoch_id]["chains"].update({
                        chain:{
                            "chain_ntx":0,
                            "chain_score":0
                        },
                    })

                resp[notary]["season_score"] += score_value

                resp[notary]["servers"][server]["server_ntx"] += 1
                resp[notary]["servers"][server]["server_score"] += score_value

                resp[notary]["servers"][server]["epochs"][epoch_id]["epoch_ntx"] += 1
                resp[notary]["servers"][server]["epochs"][epoch_id]["epoch_score"] += score_value

                resp[notary]["servers"][server]["epochs"][epoch_id]["chains"][chain]["chain_ntx"] += 1
                resp[notary]["servers"][server]["epochs"][epoch_id]["chains"][chain]["chain_score"] += score_value
           
    return resp

