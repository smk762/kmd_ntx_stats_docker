#!/usr/bin/env python3.12
import numpy as np
from kmd_ntx_api.cache_data import cached
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
def get_base_context(request, notary=None):
    # Helper function to avoid fetching all cached data upfront
    def get_cached_data():
        return {
            "explorers": cached.get_data("explorers_cache"),
            "coin_icons": cached.get_data("coin_icons_cache"),
            "notary_icons": cached.get_data("notary_icons"),
            "nav_data": cached.get_data("navigation"),
        }

    def get_default_values():
        """Fetch default or selected values from the request."""
        return {
            "server": get_page_server(request),
            "region": get_or_none(request, "region", "EU"),
            "epoch": get_or_none(request, "epoch", "Epoch_0"),
            "coin": get_or_none(request, "coin", "KMD"),
            "year": get_or_none(request, "year"),
            "month": get_or_none(request, "month"),
            "address": get_or_none(request, "address"),
            "hide_filters": get_or_none(request, "hide_filters", []),
        }

    def get_notary_selection(notary, notary_list):
        """Select notary based on provided or random notary."""
        return notary if notary else get_or_none(request, "notary", get_random_notary(notary_list))

    def get_dpow_coins_list(dpow_coins_dict):
        """Flatten and sort the DPoW coins list."""
        dpow_coins_dict["Main"] += ["KMD", "LTC"]
        dpow_coins_dict["Main"].sort()
        return [coin for sublist in dpow_coins_dict.values() for coin in sublist]

    # Fetch cached data lazily
    cached_data = get_cached_data()
    
    # Fetch seasons and notaries
    seasons_info = get_seasons_info()
    season = get_page_season(request, seasons_info)
    notary_list = get_notary_list(season, seasons_info)
    notary = get_notary_selection(notary, notary_list)
    
    # Fetch dPoW coins and related data
    dpow_coins_dict = get_dpow_coins_dict(season)
    dpow_coins_list = get_dpow_coins_list(dpow_coins_dict)
    
    # Default and selected values from request
    values = get_default_values()
    
    # Fetch eco data link
    eco_data_link = get_eco_data_link()
    
    # Get selected GET parameters as a dictionary
    selected = {key: request.GET[key] for key in request.GET}

    # Prepare context for the template
    context = {
        "season": season,
        "season_clean": season.replace("_", " "),
        "server": values["server"],
        "region": values["region"],
        "regions": ["AR", "EU", "NA", "SH", "DEV"],
        "epoch": values["epoch"],
        "epoch_clean": values["epoch"].replace("_", " "),
        "coin": values["coin"],
        "notary": notary,
        "notary_clean": get_notary_clean(notary),
        "year": values["year"],
        "month": values["month"],
        "address": values["address"],
        "selected": selected,
        "hide_filters": values["hide_filters"],
        "explorers": cached_data["explorers"],
        "dpow_coins_dict": dpow_coins_dict,
        "coin_icons": cached_data["coin_icons"],
        "dpow_coins_list": dpow_coins_list,
        "notary_icons": cached_data["notary_icons"],
        "notaries": notary_list,
        "nav_data": cached_data["nav_data"],
        "eco_data_link": eco_data_link,
    }

    return context


def get_coin_profile_index_context(request, context):
    logger.info("Preparing Coin Profile Index Context")
    context.update({
        "buttons": buttons.get_server_buttons(),
        "coin_social": get_coin_social_info(request),
    })
    return context


def get_notary_profile_index_context(request, context):
    logger.info("Preparing Notary Profile Index Context")
    context.update({
        "page_title": "Notary Profile Index",
        "buttons": buttons.get_region_buttons(),
        "nn_social": get_nn_social_info(request),
        "nn_regions": get_regions_info(context.get('season'))
    })
    return context


def get_notary_profile_context(request, notary, context):
    try:
        notary_profile_summary_table = get_notary_ntx_season_table_data(request, notary)
        if len(notary_profile_summary_table["notary_ntx_summary_table"]) == 1:

            last_ntx_time = 0
            last_ntx_coin = ""
            last_ltc_ntx_time = 0
            notary_ntx_summary_table = notary_profile_summary_table["notary_ntx_summary_table"][0]

            for coin in notary_ntx_summary_table:
                logger.loop(coin)
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
            logger.info(context["last_ntx_coin"])

            seed_scores = get_seednode_version_score_total(request)
            notarised_data_24hr = get_notarised_date(context['season'], None, None, notary, True)
            region = get_notary_region(notary)
            season_stats_sorted = get_season_stats_sorted(context['season'], context['notaries'])
            logger.calc(region)
            
            ntx_season_data = notary_profile_summary_table["ntx_season_data"][0]
            seed_score = seed_scores[notary]
            total_ntx_score = ntx_season_data["total_ntx_score"]
            logger.query(total_ntx_score)
            total_score = total_ntx_score + seed_score
            logger.merge(f"total_score: {total_score}")
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
        logger.warning(f"Failed to get notary profile context for {notary}: {e}")
    return context




def get_coin_profile_context(request, season, coin, context):
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
            top_region_notarisers, coin, notary_icons
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

