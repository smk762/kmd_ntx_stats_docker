#!/usr/bin/env python3
import time
import random
import numpy as np
from datetime import datetime as dt
from django.shortcuts import render
from django.db.models import Sum

from kmd_ntx_api.const import SINCE_INTERVALS
from kmd_ntx_api.notary_seasons import get_page_season
from kmd_ntx_api.query import get_notarised_data, get_mined_data
from kmd_ntx_api.stats import get_season_stats_sorted, get_region_score_stats, get_daily_stats_sorted
from kmd_ntx_api.info import get_nn_social_info
from kmd_ntx_api.context import get_base_context
from kmd_ntx_api.helper import get_dpow_coins, day_ago
from kmd_ntx_api.logger import logger


def dash_view(request):
    season = get_page_season(request)
    context = get_base_context(request)
    data = get_notarised_data(season=season, exclude_epoch="Unofficial")
    ntx_season = data.count()
    ntx_24hr = data.filter(block_time__gt=str(day_ago())).count()
    # Get Mining Stats
    try:
        mined_data = get_mined_data(season=season)
        mined_season = mined_data.aggregate(Sum('value'))['value__sum']
    except Exception as e:
        logger.error(e)
        mined_season = 0

    try:
        mined_24hr = mined_data.filter(block_time__gt=str(day_ago)).aggregate(Sum('value'))['value__sum']        
    except Exception as e:
        logger.error(e)
        mined_24hr = 0
    
    try:
        biggest_block = mined_data.order_by('-value').first()
    except Exception as e:
        logger.error(e)
        biggest_block = 0
    
    coins_dict = get_dpow_coins(season)
    coins_list = []
    for server in coins_dict: 
        coins_list += coins_dict[server]

    daily_stats_sorted = get_daily_stats_sorted(season, coins_dict)
    season_stats_sorted = get_season_stats_sorted(season, coins_list)
    nn_social = get_nn_social_info(request)
    region_score_stats = get_region_score_stats(season_stats_sorted)

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
