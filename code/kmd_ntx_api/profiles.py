#!/usr/bin/env python3
import numpy as np

# S7 refactoring
import kmd_ntx_api.buttons as buttons
from kmd_ntx_api.mining import get_nn_mining_summary
from kmd_ntx_api.ntx import get_notarised_date
from kmd_ntx_api.seednodes import get_seednode_version_score_total
from kmd_ntx_api.helper import get_coin_server, get_regions_info, get_time_since, \
    get_notary_region, get_dpow_coins
from kmd_ntx_api.info import get_nn_social_info, get_coins, \
    get_region_rank, get_coin_social_info, get_notary_icons, \
    get_coin_ntx_summary
from kmd_ntx_api.table import get_notary_ntx_season_table_data, \
    get_coin_ntx_season_table_data, get_balances_rows
from kmd_ntx_api.stats import get_coin_notariser_ranks, get_top_region_notarisers, \
    get_top_coin_notarisers, get_season_stats_sorted

def get_notary_profile_index_context(request, season):
    return {
        "page_title": "Notary Profile Index",
        "buttons": buttons.get_region_buttons(),
        "nn_social": get_nn_social_info(request),
        "nn_regions": get_regions_info(season)
    }


def get_notary_profile_context(request, season, notary):
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

        context = {
            "notary_ntx_summary_table": notary_ntx_summary_table,
            "last_ltc_ntx_time": get_time_since(last_ltc_ntx_time)[1],
            "last_ntx_time": get_time_since(last_ntx_time)[1],
            "last_ntx_coin": last_ntx_coin
        }

        seed_scores = get_seednode_version_score_total(request)
        notarised_data_24hr = get_notarised_date(season, None, None, notary, True)
        region = get_notary_region(notary)
        season_stats_sorted = get_season_stats_sorted(season)

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


def get_coin_profile_index_context(request, season):
    coins_dict = get_dpow_coins(season)
    coins_dict["Main"] += ["KMD", "LTC"]
    coins_dict["Main"].sort()
    return { 
        "buttons": buttons.get_server_buttons(),
        "coin_social": get_coin_social_info(request),
        "server_coins": coins_dict
    }


def get_coin_profile_context(request, season, coin):
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
        coin_notariser_ranks = get_coin_notariser_ranks(season)
        top_region_notarisers = get_top_region_notarisers(coin_notariser_ranks)
        top_coin_notarisers = get_top_coin_notarisers(
                                    top_region_notarisers, coin, notary_icons
                                )

        return {
            "page_title": f"{coin} Profile",
            "server": get_coin_server(season, coin),
            "coin": coin,
            "coins_data": coins_data,
            "notary_icons": notary_icons,
            "coin_balances": coin_balances["results"], # Balances in table format
            "max_tick": max_tick,
            "coin_social": get_coin_social_info(request),
            "coin_ntx_summary": get_coin_ntx_summary(season, coin),
            "coin_ntx_summary_table": coin_ntx_summary_table,
            "coin_notariser_ranks": coin_notariser_ranks,
            "top_region_notarisers": top_region_notarisers,
            "top_coin_notarisers": top_coin_notarisers
        }

