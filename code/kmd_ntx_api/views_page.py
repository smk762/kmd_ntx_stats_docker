#!/usr/bin/env python3
import time
import random
import numpy as np
from datetime import datetime as dt
from django.shortcuts import render
from django.db.models import Sum
from kmd_ntx_api.lib_const import *

import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_mining as mining
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_stats as stats
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_table as table
import kmd_ntx_api.lib_info as info


def dash_view(request, dash_name=None):
    season = helper.get_page_season(request)
    # Table Views
    context = helper.get_base_context(request)

    day_ago = int(time.time()) - SINCE_INTERVALS['day']

    # Get NTX Counts
    data = query.get_notarised_data(season=season, exclude_epoch="Unofficial")
    ntx_season = data.count()
    ntx_24hr = data.filter(block_time__gt=str(day_ago)).count()


    # Get Mining Stats
    try:
        mined_data = query.get_mined_data(season=season)
        mined_season = mined_data.aggregate(Sum('value'))['value__sum']
    except Exception as e:
        print(e)
        mined_season = 0

    try:
        mined_24hr = mined_data.filter(block_time__gt=str(day_ago)).aggregate(Sum('value'))['value__sum']        
    except Exception as e:
        print(e)
        mined_24hr = 0
    
    try:
        biggest_block = mined_data.order_by('-value').first()
    except Exception as e:
        print(e)
        biggest_block = 0
    

    coins_dict = helper.get_dpow_server_coins_dict(season)
    coins_list = []
    for server in coins_dict: 
        coins_list += coins_dict[server]

    daily_stats_sorted = stats.get_daily_stats_sorted(season, coins_dict)
    season_stats_sorted = stats.get_season_stats_sorted(season, coins_list)
    nn_social = info.get_nn_social_info(request)
    region_score_stats = stats.get_region_score_stats(season_stats_sorted)
    sidebar_links = helper.get_sidebar_links(season)

    context.update({
        "page_title": "Index",
        "ntx_24hr": ntx_24hr,
        "ntx_season": ntx_season,
        "mined_24hr": mined_24hr,
        "mined_season": mined_season,
        "biggest_block": biggest_block,
        "season_stats_sorted": season_stats_sorted,
        "region_score_stats": region_score_stats,
        "show_ticker": True,
        "server_coins": coins_dict,
        "coins_list": coins_list,
        "daily_stats_sorted": daily_stats_sorted,
        "nn_social": nn_social
    })
    return render(request, 'views/dash_index.html', context)
    
def test_component(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":f"Test"
    })

    return render(request, 'components/tables/generic_source/notary_vote_table.html', context)
    return render(request, 'tables/ntx_node_daily.html', context)

