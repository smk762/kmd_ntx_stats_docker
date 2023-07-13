#!/usr/bin/env python3

# S7 refactoring
import kmd_ntx_api.buttons as buttons
from kmd_ntx_api.seednodes import get_seednode_version_month_table, \
    get_seednode_version_score_total, get_seednode_version_date_table

# Older
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_ntx as ntx
import kmd_ntx_api.lib_atomicdex as dex
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_stats as stats
import kmd_ntx_api.lib_mining as mining
import kmd_ntx_api.lib_table as table


def get_notary_profile_index_context(request, season):
    return {
        "page_title": "Notary Profile Index",
        "buttons": buttons.get_region_buttons(),
        "nn_social": info.get_nn_social_info(request),
        "nn_regions": helper.get_regions_info(season)
    }


def get_notary_profile_context(request, season, notary):
    notary_profile_summary_table = table.get_notary_ntx_season_table_data(request, notary)
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
            "last_ltc_ntx_time": helper.get_time_since(last_ltc_ntx_time)[1],
            "last_ntx_time": helper.get_time_since(last_ntx_time)[1],
            "last_ntx_coin": last_ntx_coin
        }

        seed_scores = get_seednode_version_score_total(request)
        notarised_data_24hr = ntx.get_notarised_date(season, None, None, notary, True)
        region = helper.get_notary_region(notary)
        season_stats_sorted = stats.get_season_stats_sorted(season)

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
            "rank": info.get_region_rank(season_stats_sorted[region], notary),
            "buttons": buttons.get_ntx_buttons(),
            "nn_social": info.get_nn_social_info(request), # Social Media Links
            "mining_summary": mining.get_nn_mining_summary(notary), #  Mining Summary
            "master_notarised_24hr": notarised_data_24hr.filter(server='KMD').count(),
            "main_notarised_24hr": notarised_data_24hr.filter(server='Main').count(),
            "third_notarised_24hr": notarised_data_24hr.filter(server='Third_Party').count()
        })


def get_coin_profile_index_context(request, season):
    coins_dict = helper.get_dpow_server_coins_dict(season)
    coins_dict["Main"] += ["KMD", "LTC"]
    coins_dict["Main"].sort()
    return { 
        "buttons": buttons.get_server_buttons(),
        "coin_social": info.get_coin_social_info(request),
        "server_coins": coins_dict
    }


def get_coin_profile_context(request, season, coin):
    coin_profile_summary_table = table.get_coin_ntx_season_table_data(request, coin)
    if len(coin_profile_summary_table["coin_ntx_summary_table"]) == 1:
        coin_ntx_summary_table = coin_profile_summary_table["coin_ntx_summary_table"][0]
        coins_data = info.get_coins(request, coin)
        if coin in coins_data:
            coins_data = coins_data[coin]

        coin_balances = table.get_balances_rows(request)
        max_tick = 0
        for item in coin_balances["results"]:
            if float(item['balance']) > max_tick:
                max_tick = float(item['balance'])
        if max_tick > 0:
            10**(int(round(np.log10(max_tick))))
        else:
            max_tick = 10

        notary_icons = info.get_notary_icons(request)
        coin_notariser_ranks = stats.get_coin_notariser_ranks(season)
        top_region_notarisers = stats.get_top_region_notarisers(coin_notariser_ranks)
        top_coin_notarisers = stats.get_top_coin_notarisers(
                                    top_region_notarisers, coin, notary_icons
                                )

        context.update({
            "page_title": f"{coin} Profile",
            "server": server,
            "coin": coin,
            "coins_data": coins_data,
            "notary_icons": notary_icons,
            "coin_balances": coin_balances["results"], # Balances in table format
            "max_tick": max_tick,
            "coin_social": info.get_coin_social_info(request),
            "coin_ntx_summary": info.get_coin_ntx_summary(season, coin),
            "coin_ntx_summary_table": coin_ntx_summary_table,
            "coin_notariser_ranks": coin_notariser_ranks,
            "top_region_notarisers": top_region_notarisers,
            "top_coin_notarisers": top_coin_notarisers
        })            

