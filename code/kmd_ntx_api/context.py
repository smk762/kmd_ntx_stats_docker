#!/usr/bin/env python3
import numpy as np
from kmd_ntx_api.cache_data import explorers_cache, coin_icons_cache, \
    notary_icons_cache, navigation_cache
from kmd_ntx_api.coins import get_dpow_coins_dict, get_dpow_coin_server
from kmd_ntx_api.cron import get_time_since
from kmd_ntx_api.helper import get_or_none, get_notary_list, get_page_server, \
    get_notary_clean, get_eco_data_link, \
    get_random_notary, get_regions_info, \
    get_notary_region
from kmd_ntx_api.info import get_nn_social_info, get_coins, \
    get_region_rank, get_coin_social_info, get_notary_icons, \
    get_coin_ntx_summary
from kmd_ntx_api.logger import logger, timed
from kmd_ntx_api.mining import get_nn_mining_summary
from kmd_ntx_api.notary_seasons import get_page_season, get_seasons_info
from kmd_ntx_api.ntx import get_notarised_date
from kmd_ntx_api.seednodes import get_seednode_version_score_total
from kmd_ntx_api.stats import get_coin_notariser_ranks, get_top_region_notarisers, \
    get_top_coin_notarisers, get_season_stats_sorted
from kmd_ntx_api.table import get_notary_ntx_season_table_data, \
    get_coin_ntx_season_table_data, get_balances_rows
import kmd_ntx_api.buttons as buttons


@timed
def get_base_context(request):
    seasons_info = get_seasons_info()
    season = get_page_season(request, seasons_info)
    server = get_page_server(request)
    notary_list = get_notary_list(season, seasons_info)
    region = get_or_none(request, "region", "EU")
    notary = get_or_none(request, "notary", get_random_notary(notary_list))
    epoch = get_or_none(request, "epoch", "Epoch_0")
    coin = get_or_none(request, "coin", "KMD")
    dpow_coins_dict = get_dpow_coins_dict(season)
    logger.info(dpow_coins_dict)
    dpow_coins_dict["Main"] += ["KMD", "LTC"]
    dpow_coins_dict["Main"].sort()
    dpow_coins_list = [item for sublist in dpow_coins_dict.values() for item in sublist]
    year = get_or_none(request, "year")
    month = get_or_none(request, "month")
    address = get_or_none(request, "address")
    hide_filters = get_or_none(request, "hide_filters", [])
    explorers = explorers_cache()
    coin_icons = coin_icons_cache()
    notary_icons = notary_icons_cache()
    nav_data = navigation_cache()
    eco_data_link = get_eco_data_link()
    selected = {}
    [selected.update({i: request.GET[i]}) for i in request.GET]
    context = {
        "season": season,
        "server": server,
        "epoch": epoch,
        "coin": coin,
        "notary": notary,
        "year": year,
        "month": month,
        "address": address,
        "selected": selected,
        "hide_filters": hide_filters,
        "region": region,
        "regions": ["AR", "EU", "NA", "SH", "DEV"],
        "season_clean": season.replace("_"," "),
        "epoch_clean": epoch.replace("_"," "),
        "notary_clean": get_notary_clean(notary),
        "explorers": explorers,
        "dpow_coins_dict": dpow_coins_dict,
        "coin_icons": coin_icons,
        "dpow_coins_list": dpow_coins_list,
        "notary_icons": notary_icons,
        "notaries": notary_list,
        "nav_data": nav_data,
        "eco_data_link": eco_data_link
    }
    return context


def get_notary_profile_index_context(request, context):
    logger.merge("get_notary_profile_index_context")
    context.update({
        "page_title": "Notary Profile Index",
        "buttons": buttons.get_region_buttons(),
        "nn_social": get_nn_social_info(request),
        "nn_regions": get_regions_info(context['season'])
    })
    return context


def get_notary_profile_context(request, notary, context):
    logger.info("get_notary_profile_context")
    try:
        notary_profile_summary_table = get_notary_ntx_season_table_data(request, notary)
        if len(notary_profile_summary_table["notary_ntx_summary_table"]) == 1:

            last_ntx_time = 0
            last_ntx_coin = ""
            last_ltc_ntx_time = 0
            notary_ntx_summary_table = notary_profile_summary_table["notary_ntx_summary_table"][0]

            for coin in notary_ntx_summary_table:
                if "last_ntx_blocktime" in notary_ntx_summary_table[coin]:
                    if coin == "KMD":
                        last_ltc_ntx_time = notary_ntx_summary_table[coin]["last_ntx_blocktime"]
                    if notary_ntx_summary_table[coin]["last_ntx_blocktime"] > last_ntx_time:
                        last_ntx_time = notary_ntx_summary_table[coin]["last_ntx_blocktime"]
                        last_ntx_coin = coin

            context.update({
                "notary_ntx_summary_table": notary_ntx_summary_table,
                "last_ltc_ntx_time": get_time_since(last_ltc_ntx_time)[1],
                "last_ntx_time": get_time_since(last_ntx_time)[1],
                "last_ntx_coin": last_ntx_coin
            })

            seed_scores = get_seednode_version_score_total(request)
            notarised_data_24hr = get_notarised_date(context['season'], None, None, notary, True)
            region = get_notary_region(notary)
            season_stats_sorted = get_season_stats_sorted(context['season'], context['notaries'])

            ntx_season_data = notary_profile_summary_table["ntx_season_data"][0]
            seed_score = seed_scores[notary]
            total_ntx_score = ntx_season_data["total_ntx_score"]
            total_score = total_ntx_score + seed_score
            context.update({
                "page_title": f"{notary} Notary Profile",
                "notary": notary,
                "notary_clean": notary.replace("_", " "),
                "seed_score": seed_score,
                "ntx_score": total_score,
                "season_score": total_score,
                "master_server_count": ntx_season_data['master_server_count'],
                "main_server_count": ntx_season_data['main_server_count'],
                "third_party_server_count": ntx_season_data['third_party_server_count'],
                "rank": get_region_rank(season_stats_sorted[region], notary),
                "buttons": buttons.get_ntx_buttons(),
                "nn_social": get_nn_social_info(request), # Social Media Links
                "mining_summary": get_nn_mining_summary(notary), #  Mining Summary
                "master_notarised_24hr": notarised_data_24hr.filter(server='KMD').count(),
                "main_notarised_24hr": notarised_data_24hr.filter(server='Main').count(),
                "third_notarised_24hr": notarised_data_24hr.filter(server='Third_Party').count()
            })
    except Exception as e:
        logger.warning(e)
    logger.info("g0t_notary_profile_context")
    return context


def get_coin_profile_index_context(request, season, context):
    logger.merge("get_coin_profile_index_context")
    context.update({ 
        "buttons": buttons.get_server_buttons(),
        "coin_social": get_coin_social_info(request)
    })
    return context
    


def get_coin_profile_context(request, season, coin, context):
    logger.merge("get_coin_profile_context")
    coin_profile_summary_table = get_coin_ntx_season_table_data(request, coin)
    if len(coin_profile_summary_table["coin_ntx_summary_table"]) == 1:
        coin_ntx_summary_table = coin_profile_summary_table["coin_ntx_summary_table"][0]
        coins_data = get_coins(request, coin)
        if coin in coins_data:
            coins_data = coins_data[coin]

        coin_balances = get_balances_rows(request)
        max_tick = 0
        for item in coin_balances["results"]:
            if float(item['balance']) > max_tick:
                max_tick = float(item['balance'])
        if max_tick > 0:
            10**(int(round(np.log10(max_tick))))
        else:
            max_tick = 10

        notary_icons = get_notary_icons(request)
        coin_notariser_ranks = get_coin_notariser_ranks(season, context['dpow_coins_list'])
        top_region_notarisers = get_top_region_notarisers(coin_notariser_ranks)
        top_coin_notarisers = get_top_coin_notarisers(
            top_region_notarisers, coin, context["notary_icons"]
        )

        context.update({
            "page_title": f"{coin} Profile",
            "server": get_dpow_coin_server(season, coin),
            "coin": coin,
            "coins_data": coins_data,
            "coin_balances": coin_balances["results"], # Balances in table format
            "max_tick": max_tick,
            "coin_social": get_coin_social_info(request),
            "coin_ntx_summary": get_coin_ntx_summary(season, coin),
            "coin_ntx_summary_table": coin_ntx_summary_table,
            "coin_notariser_ranks": coin_notariser_ranks,
            "top_region_notarisers": top_region_notarisers,
            "top_coin_notarisers": top_coin_notarisers
        })
    return context

