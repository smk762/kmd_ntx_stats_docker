#!/usr/bin/env python3

from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_struct as struct
import kmd_ntx_api.lib_mining as mining
import kmd_ntx_api.lib_ntx as ntx
from django.db.models import Count, Min, Max, Sum

    
def get_region_score_stats(notarisation_scores):
    region_score_stats = {}
    for region in notarisation_scores:
        region_total = 0
        notary_count = 0
        for item in notarisation_scores[region]:
            notary_count += 1
            region_total += item["score"]
        region_average = helper.safe_div(region_total,notary_count)
        region_score_stats.update({
            region:{
                "notary_count": notary_count,
                "total_score": region_total,
                "average_score": region_average
            }
        })
    return region_score_stats


def get_top_region_notarisers(region_notary_ranks):
    top_region_notarisers = struct.default_top_region_notarisers()
    top_ntx_count = {}
    for region in region_notary_ranks:
        if region not in top_ntx_count:
            top_ntx_count.update({region:{}})
        for notary in region_notary_ranks[region]:

            for coin in region_notary_ranks[region][notary]:
                if coin not in top_ntx_count[region]:
                    top_ntx_count[region].update({coin:0})

                if coin not in top_region_notarisers[region]:
                    top_region_notarisers[region].update({coin:{}})
                ntx_count = region_notary_ranks[region][notary][coin]
                if ntx_count > top_ntx_count[region][coin]:
                    top_notary = notary
                    top_ntx_count[region].update({coin:ntx_count})
                    top_region_notarisers[region][coin].update({
                        "top_notary": top_notary,
                        "top_ntx_count": top_ntx_count[region][coin]

                    })
    return top_region_notarisers


def get_top_coin_notarisers(top_region_notarisers, coin, notary_icons):
    top_coin_notarisers = {}
    for region in top_region_notarisers:
        if coin in top_region_notarisers[region]:
            if coin == "LTC":
                coin = "KMD"
            if "top_notary" in top_region_notarisers[region][coin]:
                notary = top_region_notarisers[region][coin]["top_notary"]
                top_coin_notarisers.update({
                    region:{
                        "top_notary": notary,
                        "top_notary_icon": notary_icons[notary],
                        "top_ntx_count": top_region_notarisers[region][coin]["top_ntx_count"]
                    }
                })
    return top_coin_notarisers


def get_daily_stats_sorted(season=None, coins_dict=None):
    if not season:
        season = SEASON
    if not coins_dict:
        coins_dict = helper.get_dpow_server_coins_dict(season)
    notary_list = helper.get_notary_list(season)

    day_ago = int(time.time()) - SINCE_INTERVALS['day']
    data = query.get_mined_data().filter(block_time__gt=str(day_ago))
    mined_last_24hrs = mining.get_mined_data_24hr().values('name').annotate(mined_24hrs=Sum('value'), blocks_24hrs=Count('value'))
    nn_mined_last_24hrs = {}
    for item in mined_last_24hrs:
        nn_mined_last_24hrs.update({item['name']:item['blocks_24hrs']})

    daily_stats = {}
    for notary in notary_list:
        
        region = helper.get_notary_region(notary)
        if region not in daily_stats:
            daily_stats.update({region:[]})

        if notary not in nn_mined_last_24hrs:
            nn_mined_last_24hrs.update({notary:0})

    ntx_24hr = ntx.get_notarised_date().values()
    for notary_name in notary_list:
        notary_ntx_24hr_summary = info.get_notary_ntx_24hr_summary(ntx_24hr, notary_name, season, coins_dict)
        region = helper.get_notary_region(notary_name)

        daily_stats[region].append({
            "notary": notary_name,
            "btc": notary_ntx_24hr_summary["btc_ntx"],
            "main": notary_ntx_24hr_summary["main_ntx"],
            "third_party": notary_ntx_24hr_summary["third_party_ntx"],
            "seed": notary_ntx_24hr_summary["seed_node_status"],
            "mining": nn_mined_last_24hrs[notary_name],
            "score": notary_ntx_24hr_summary["score"]
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
                    new_item.update({"rank": i})
                    daily_stats_sorted[region].append(new_item)
            i += 1
    return daily_stats_sorted


# returns region > notary > coin > season ntx count
def get_coin_notariser_ranks(season, coins_list=None):
    # season ntx stats
    if not coins_list:
        coins_list = info.get_dpow_coins_list(season)

    ntx_season = query.get_notary_ntx_season_data(season)
    notary_list = helper.get_notary_list(season)
    ntx_season = ntx_season.values()

    if season == "Season_5_Testnet": 
        region_notary_ranks = {
            "TESTNET": {}
        }
        coins_list = ["RICK", "MORTY", "LTC"]

        for notary in notary_list:
            region_notary_ranks["TESTNET"].update({notary:{}})

        for item in ntx_season:
            notary = item['notary']
            if notary in notary_list:
                for coin in item['coin_ntx_counts']:
                    if coin in coins_list:
                        region_notary_ranks[region][notary].update({
                            coin:item['coin_ntx_counts'][coin]
                        })

    else:
        region_notary_ranks = {
            "AR": {},
            "EU": {},
            "NA": {},
            "SH": {},
            "DEV": {}
        }
        for notary in notary_list:
            region = helper.get_notary_region(notary)
            if region in ["AR","EU","NA","SH", "DEV"]:
                region_notary_ranks[region].update({notary:{}})

        for item in ntx_season:
            notary = item['notary']
            if notary in notary_list:
                for coin in item['notary_data']["coins"]:
                    if coin in coins_list:
                        region = helper.get_notary_region(notary)
                        if region in ["AR","EU","NA","SH", "DEV"]:
                            region_notary_ranks[region][notary].update({
                                coin: item['notary_data']["coins"][coin]["ntx_count"]
                            })
    return region_notary_ranks


def get_season_stats_sorted(season, coins_dict=None):
    if not season:
        season = SEASON
    if not coins_dict:
        coins_dict = helper.get_dpow_server_coins_dict(season)
    notary_list = helper.get_notary_list(season)

    mined_last_24hrs = mining.get_mined_data_24hr().values('name')
    seednode_season = query.get_seednode_version_stats_data(season=season).values('name').annotate(sum_score=Sum('score'))
    nn_seednode_season = {}
    for item in seednode_season:
        nn_seednode_season.update({item['name']:round(item['sum_score'],2)})

    mined_season = query.get_mined_count_season_data(season).values()
    

    nn_mined_season = {}
    for item in mined_season:
        nn_mined_season.update({item['name']:item['blocks_mined']})

    season_stats = {}
    for notary in notary_list:

        region = helper.get_notary_region(notary)
        if region not in season_stats:
            season_stats.update({region:[]})

        if notary not in nn_mined_season:
            nn_mined_season.update({notary:0})

        if notary not in nn_seednode_season:
            nn_seednode_season.update({notary:0})

    nn_seednode_season_data = info.get_seednode_version_season_stats_data(season)
    for item in nn_seednode_season_data:
        nn_seednode_season.update({item['name']:round(item['sum_score'],2)})

    notary_ntx_season_data = query.get_notary_ntx_season_data(season).values()
    for item in notary_ntx_season_data:
        region = helper.get_notary_region(item["notary"])
        season_stats[region].append({
            "notary": item["notary"],
            "master": item["notary_data"]["servers"]["KMD"]["ntx_count"],
            "main": item["notary_data"]["servers"]["Main"]["ntx_count"],
            "third_party": item["notary_data"]["servers"]["Third_Party"]["ntx_count"],
            "seed": nn_seednode_season[item["notary"]],
            "mining": nn_mined_season[item["notary"]],
            "score": float(item["notary_data"]["ntx_score"]) + nn_seednode_season[item["notary"]]
        })

    # calc scores
    season_stats_sorted = {}
    for region in season_stats:
        season_stats_sorted.update({region:[]})
        scores_dict = {}
        for item in season_stats[region]:
            scores_dict.update({item['notary']:item['score']})
        sorted_scores = {k: v for k, v in sorted(scores_dict.items(), key=lambda x: x[1])}
        dec_sorted_scores = dict(reversed(list(sorted_scores.items())))
        i = 1
        for notary in dec_sorted_scores:
            for item in season_stats[region]:
                if notary == item['notary']:
                    new_item = item.copy()
                    new_item.update({"rank": i})
                    season_stats_sorted[region].append(new_item)
            i += 1
    return season_stats_sorted

