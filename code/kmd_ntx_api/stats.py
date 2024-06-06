#!/usr/bin/env python3
import time
from django.db.models import Sum, Count
from kmd_ntx_api.const import SINCE_INTERVALS
from kmd_ntx_api.helper import get_notary_region, \
    get_notary_list, safe_div, \
    get_mainnet_coins, get_third_party_coins
from kmd_ntx_api.cron import days_ago
from kmd_ntx_api.mining import get_mined_data_24hr
from kmd_ntx_api.notary_seasons import get_season
from kmd_ntx_api.ntx import get_notarised_date
from kmd_ntx_api.query import get_seednode_version_stats_data, \
    get_mined_count_season_data, get_notary_ntx_season_data, get_mined_data, \
    get_scoring_epochs_data
from kmd_ntx_api.struct import default_top_region_notarisers
from kmd_ntx_api.coins import get_dpow_coins_dict, get_dpow_coins_list
from kmd_ntx_api.logger import logger, timed
from kmd_ntx_api.cache_data import get_from_memcache, refresh_cache


def get_notary_ntx_24hr_summary(ntx_24hr, notary, dpow_coins_dict):
    cache_key = f"{notary}_ntx_24hr_summary"
    if cache_key is not None:
        data = get_from_memcache(cache_key, expire=300)
    if data is not None:
        return data
    else:
        logger.info("get_notary_ntx_24hr_summary")
        notary_ntx_24hr = {
                "master_ntx": 0,
                "main_ntx": 0,
                "third_party_ntx": 0,
                "seed_node_status": 0,
                "most_ntx": "N/A",
                "score": 0
            }

        main_coins = get_mainnet_coins(dpow_coins_dict)
        third_party_coins = get_third_party_coins(dpow_coins_dict)

        notary_coin_ntx_counts = {}

        for item in ntx_24hr:
            notaries = item['notaries']
            coin = item['coin']
            ntx_score = item['score_value']

            if notary in notaries:

                if coin not in notary_coin_ntx_counts:
                    notary_coin_ntx_counts.update({coin:1})

                else:
                    val = notary_coin_ntx_counts[coin]+1
                    notary_coin_ntx_counts.update({coin:val})

                notary_ntx_24hr["score"] += ntx_score

        max_ntx_count = 0
        master_ntx_count = 0
        main_ntx_count = 0
        third_party_ntx_count = 0

        for coin in notary_coin_ntx_counts:
            coin_ntx_count = notary_coin_ntx_counts[coin]
            if coin_ntx_count > max_ntx_count:
                max_coin = coin
                max_ntx_count = coin_ntx_count
            if coin == "KMD": 
                master_ntx_count += coin_ntx_count
            elif coin in main_coins:
                main_ntx_count += coin_ntx_count
            elif coin in third_party_coins:
                third_party_ntx_count += coin_ntx_count

        seed_node_score = 0
        start = time.time() - SINCE_INTERVALS["day"]
        end = time.time()
        seed_data = get_seednode_version_stats_data(start=start, end=end, name=notary).filter(score=0.2).values()
        notary_ntx_24hr["score"] = float(notary_ntx_24hr["score"])
        for item in seed_data:
            seed_node_score += round(item["score"], 2)
            notary_ntx_24hr["score"] += round(item["score"], 2)

        if max_ntx_count > 0:
            notary_ntx_24hr.update({
                    "master_ntx": master_ntx_count,
                    "main_ntx": main_ntx_count,
                    "third_party_ntx": third_party_ntx_count,
                    "seed_node_status": round(seed_node_score, 2),
                    "most_ntx": str(max_ntx_count)+" ("+str(max_coin)+")"
                })
        refresh_cache(data=notary_ntx_24hr, force=True, key=cache_key, expire=300)
        return notary_ntx_24hr
 

def get_seednode_version_season_stats_data(season, notary=None):
    return get_seednode_version_stats_data(season=season, name=notary, score=0.2).values('name').annotate(sum_score=Sum('score'))


def get_season_stats_sorted(season, notary_list):
    logger.info("get_season_stats_sorted")

    mined_last_24hrs = get_mined_data_24hr().values('name')
    seednode_season = get_seednode_version_stats_data(season=season).values('name')
    seednode_season = seednode_season.annotate(sum_score=Sum('score'))
    nn_seednode_season = {}
    for item in seednode_season:
        nn_seednode_season.update({item['name']:round(item['sum_score'],2)})

    mined_season = get_mined_count_season_data(season).values()
    nn_mined_season = {}
    for item in mined_season:
        nn_mined_season.update({item['name']:item['blocks_mined']})

    season_stats = {}
    for notary in notary_list:
        region = get_notary_region(notary)
        if region not in season_stats:
            season_stats.update({region:[]})

        if notary not in nn_mined_season:
            nn_mined_season.update({notary:0})

        if notary not in nn_seednode_season:
            nn_seednode_season.update({notary:0})

    nn_seednode_season_data = get_seednode_version_season_stats_data(season)
    for item in nn_seednode_season_data:
        nn_seednode_season.update({item['name']:round(item['sum_score'],2)})

    notary_ntx_season_data = get_notary_ntx_season_data(season).values()
    for item in notary_ntx_season_data:
        region = get_notary_region(item["notary"])
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


def get_region_score_stats(notarisation_scores):
    region_score_stats = {}
    for region in notarisation_scores:
        region_total = 0
        notary_count = 0
        for item in notarisation_scores[region]:
            notary_count += 1
            region_total += item["score"]
        region_average = safe_div(region_total,notary_count)
        region_score_stats.update({
            region:{
                "notary_count": notary_count,
                "total_score": region_total,
                "average_score": region_average
            }
        })
    return region_score_stats


def get_daily_stats_sorted(notary_list, dpow_coins_dict):
    logger.info("get_daily_stats_sorted")
    cache_key = f"daily_stats_sorted"
    if cache_key is not None:
        data = get_from_memcache(cache_key, expire=300)
    if data is not None:
        return data
    else:
        data = get_mined_data().filter(block_time__gt=str(days_ago(1)))
        mined_last_24hrs = get_mined_data_24hr().values('name').annotate(mined_24hrs=Sum('value'), blocks_24hrs=Count('value'))
        nn_mined_last_24hrs = {}
        for item in mined_last_24hrs:
            nn_mined_last_24hrs.update({item['name']:item['blocks_24hrs']})

        daily_stats = {}
        for notary in notary_list:
            
            region = get_notary_region(notary)
            if region not in daily_stats:
                daily_stats.update({region:[]})

            if notary not in nn_mined_last_24hrs:
                nn_mined_last_24hrs.update({notary:0})

        ntx_24hr = get_notarised_date().values()
        
        for notary_name in notary_list:
            notary_ntx_24hr_summary = get_notary_ntx_24hr_summary(ntx_24hr, notary_name, dpow_coins_dict)
            region = get_notary_region(notary_name)

            daily_stats[region].append({
                "notary": notary_name,
                "master": notary_ntx_24hr_summary["master_ntx"],
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
        refresh_cache(data=daily_stats_sorted, force=True, key=cache_key, expire=300)
        return daily_stats_sorted


# Functions used in profiles.py
def get_top_region_notarisers(region_notary_ranks):
    top_region_notarisers = default_top_region_notarisers()
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


# returns region > notary > coin > season ntx count
def get_coin_notariser_ranks(season, dpow_coins_list):
    logger.info("get_coin_notariser_ranks")

    ntx_season = get_notary_ntx_season_data(season)
    notary_list = get_notary_list(season)
    ntx_season = ntx_season.values()

    if season.find("estnet") > -1:
        region_notary_ranks = {
            "TESTNET": {}
        }
        coins_list = ["DOC", "MARTY", "LTC"]

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
            region = get_notary_region(notary)
            if region in ["AR","EU","NA","SH", "DEV"]:
                region_notary_ranks[region].update({notary:{}})

        for item in ntx_season:
            notary = item['notary']
            if notary in notary_list:
                for coin in item['notary_data']["coins"]:
                    if coin in coins_list:
                        region = get_notary_region(notary)
                        if region in ["AR","EU","NA","SH", "DEV"]:
                            region_notary_ranks[region][notary].update({
                                coin: item['notary_data']["coins"][coin]["ntx_count"]
                            })
    return region_notary_ranks

