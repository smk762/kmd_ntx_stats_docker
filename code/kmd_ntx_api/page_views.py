#!/usr/bin/env python3
import time
import random
import numpy as np
from datetime import datetime as dt
from django.shortcuts import render
from django.db.models import Sum
from kmd_ntx_api.coins import get_dpow_coins_dict
from kmd_ntx_api.const import SINCE_INTERVALS
from kmd_ntx_api.notary_seasons import get_page_season
from kmd_ntx_api.query import get_notarised_data, get_mined_data
from kmd_ntx_api.stats import get_season_stats_sorted, get_region_score_stats, get_daily_stats_sorted
from kmd_ntx_api.info import get_nn_social_info
from kmd_ntx_api.context import get_base_context
from kmd_ntx_api.cron import days_ago
from kmd_ntx_api.logger import logger
from kmd_ntx_api.ntx import get_ntx_count_season, get_ntx_count_24hr
from kmd_ntx_api.mining import get_mined_count_season, get_mined_count_24hr, get_biggest_block_season


def dash_view(request):
    season = get_page_season(request)
    context = get_base_context(request)
    logger.info("dash_view")
    
    ntx_data = get_notarised_data(season=season, exclude_epoch="Unofficial")
    logger.info("got_notarised_data")
    ntx_season = get_ntx_count_season(ntx_data)
    logger.info("got_notarised_data count")
    ntx_24hr = get_ntx_count_24hr(ntx_data)
    logger.info("got_notarised_data count 24")
    
    # Get Mining Stats
    mined_data = get_mined_data(season=season)
    mined_season = get_mined_count_season(mined_data)
    logger.info("got mined data")
    mined_24hr = get_mined_count_24hr(mined_data)
    logger.info("got mined 24 data")
    biggest_block = get_biggest_block_season(mined_data)
    logger.info("biggest_block")
    daily_stats_sorted = get_daily_stats_sorted(context["notaries"], context["dpow_coins_dict"])
    logger.info("daily_stats_sorted")
    season_stats_sorted = get_season_stats_sorted(season, context["notaries"])
    logger.info("season_stats_sorted")
    region_score_stats = get_region_score_stats(season_stats_sorted)
    logger.info("region_score_stats")

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
        "daily_stats_sorted": daily_stats_sorted,
        "nn_social": get_nn_social_info(request)
    })
    return render(request, 'views/dash_index.html', context)
