#!/usr/bin/env python3
import random
import numpy as np
from datetime import datetime as dt
from django.shortcuts import render

from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_ntx as ntx
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_stats as stats
import kmd_ntx_api.lib_graph as graph
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_mining as mining
import kmd_ntx_api.lib_table as table


def notary_coin_ntx_detail_view(request):
    context = helper.get_base_context(request)
    notary = helper.get_or_none(request, "notary")
    coin = helper.get_or_none(request, "coin")
    server = helper.get_or_none(request, "server")

    context.update({
        "page_title":"Notary Profile Index",
        "notary":notary,
        "server":server,
        "coin":coin
    })

    return render(request, 'views/ntx/notary_coin_ntx_detail.html', context)


def notary_profile_view(request, notary=None):
    season = helper.get_page_season(request)
    context = helper.get_base_context(request)

    context.update({
        "page_title":"Notary Profile Index",
        "notary_seasons": info.get_notary_seasons()
    })

    if notary:
        if notary in helper.get_notary_list(season):

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

                context.update({
                    "notary_ntx_summary_table": notary_ntx_summary_table,
                    "last_ltc_ntx_time": helper.get_time_since(last_ltc_ntx_time)[1],
                    "last_ntx_time": helper.get_time_since(last_ntx_time)[1],
                    "last_ntx_coin": last_ntx_coin
                })

                ntx_season_data = notary_profile_summary_table["ntx_season_data"][0]
                seed_score = 0
                context.update({
                    "seed_score": seed_score,
                    "ntx_score": ntx_season_data["total_ntx_score"],
                    "season_score": seed_score + ntx_season_data["total_ntx_score"],
                    "master_server_count": ntx_season_data['master_server_count'],
                    "main_server_count": ntx_season_data['main_server_count'],
                    "third_party_server_count": ntx_season_data['third_party_server_count'],
                })

                notarised_data_24hr = ntx.get_notarised_date(season, None, None, notary, True)
                context.update({
                    "master_notarised_24hr": notarised_data_24hr.filter(server='KMD').count(),
                    "main_notarised_24hr": notarised_data_24hr.filter(server='Main').count(),
                    "third_notarised_24hr": notarised_data_24hr.filter(server='Third_Party').count()
                })

                region = helper.get_notary_region(notary)
                season_stats_sorted = stats.get_season_stats_sorted(season)
                rank = info.get_region_rank(season_stats_sorted[region], notary)
                context.update({
                    "rank": rank,
                })

                context.update({
                    "page_title": f"{notary} Notary Profile",
                    "notary": notary,
                    "notary_clean": notary.replace("_", " "),
                    "nn_social": info.get_nn_social_info(request), # Social Media Links
                    "mining_summary": mining.get_nn_mining_summary(notary), #  Mining Summary
                    "notary_balances": table.get_balances_table(request, notary), # Balances in table format
                    "notary_ntx_24hr": table.get_notary_ntx_24hr_table_data(request, notary), # Balances in table format
                })

                return render(request, 'views/ntx/notary_profile.html', context)

    context.update({
        "nn_social": info.get_nn_social_info(request),
        "nn_regions": helper.get_regions_info(season)
    })

    return render(request, 'views/ntx/notary_profile_index.html', context)


# TODO: Add Date Form to restrict results returned. merge with "last 24hrs?"
def notary_mining_view(request, notary=None):
    season = helper.get_page_season(request)
    context = helper.get_base_context(request)
    if not notary:
        return render(request, 'dash_index.html', context)

    context.update({
        "page_title": f"{notary} Notary KMD Mining",
        "notary_mining": query.get_mined_data(None, notary).values().order_by('block_height'),
    })

    return render(request, 'views/ntx/notary_mining.html', context)


def ntx_scoreboard(request):
    season = helper.get_page_season(request)
    season_stats_sorted = stats.get_season_stats_sorted(season)
    context = helper.get_base_context(request)
    context.update({
        "page_title": f"Notarisation Scoreboard",
        "anchored": True,
        "season_stats_sorted": season_stats_sorted,
        "region_score_stats": stats.get_region_score_stats(season_stats_sorted),
        "nn_social": info.get_nn_social_info(request)
    })
    return render(request, 'views/ntx/ntx_scoreboard.html', context)


def ntx_scoreboard_24hrs(request):
    season = helper.get_page_season(request)
    context = helper.get_base_context(request)
    context.update({
        "page_title": f"Last 24hrs Notarisation Scoreboard",
        "anchored": True,
        "daily_stats_sorted": stats.get_daily_stats_sorted(season),
        "nn_social": info.get_nn_social_info(request)
    })
    return render(request, 'views/ntx/ntx_scoreboard_24hrs.html', context)
 

def notary_coin_notarised_view(request):
    season = helper.get_page_season(request)
    notary = helper.get_or_none(request, "notary", random.choice(helper.get_notary_list(season)))
    server = helper.get_or_none(request, "server", "Main")
    coin = helper.get_or_none(request, "coin", "MORTY")

    context = helper.get_base_context(request)
    context.update({
        "server": server,
        "coin": coin,
        "notary": notary, 
        "notary_clean": notary.replace("_"," "),
        "filter_params": f"&notary={{{notary}}}&coin={coin}&season={season}&server={server}"
    })

    return render(request, 'views/ntx/notary_coin_notarised.html', context)


def notary_epoch_scores_view(request):
    season = helper.get_page_season(request)
    notary = helper.get_or_none(request, "notary", random.choice(helper.get_notary_list(season)))
    scoring_table, totals = table.get_notary_epoch_scores_table(request, notary)
    notary_clean = helper.get_notary_clean(notary)
    context = helper.get_base_context(request)
    context.update({
        "page_title":f"{notary_clean} dPoW Notarisation Epoch Scores",
        "notary":notary,
        "notary_clean": notary_clean,
        "scoring_table": scoring_table,
        "total_count":totals["counts"][notary],
        "total_score":totals["scores"][notary],
        "nn_social": info.get_nn_social_info(request)
    })
    return render(request, 'views/ntx/notary_epoch_scores_view.html', context)


def notarised_24hrs(request):    
    context = helper.get_base_context(request)
    context.update({
        "page_title":"dPoW Notarisations (last 200)",
        "notarised_24hrs":notarised_24hrs
    })
    return render(request, 'views/ntx/notarised_24hrs.html', context)


def notary_epoch_coin_notarised_view(request):
    season = helper.get_page_season(request)
    notary = helper.get_or_none(request, "notary", random.choice(helper.get_notary_list(season)))
    server = helper.get_or_none(request, "server", "Main")
    epoch = helper.get_or_none(request, "epoch", "Epoch_0")
    coin = helper.get_or_none(request, "coin", "MORTY")

    context = helper.get_base_context(request)
    context.update({
        "notary": notary,
        "notary_clean": notary.replace("_"," "),
        "server": server,
        "server_clean": server.replace("_"," "),
        "epoch": epoch,
        "epoch_clean": epoch.replace("_"," "),
        "coin": coin,
        "season_clean": season.replace("_"," ")
    })

    return render(request, 'views/ntx/notary_epoch_coin_notarised.html', context)