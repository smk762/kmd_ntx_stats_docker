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
    context = get_base_context(request)
    ntx_data = get_notarised_data(season=context["season"], exclude_epoch="Unofficial")
    mined_data = get_mined_data(season=context["season"])
    season_stats_sorted = get_season_stats_sorted(context["season"], context["notaries"])
    context.update({
        "show_ticker": True,
        "page_title": "Index",
        "ntx_24hr": get_ntx_count_24hr(ntx_data),
        "ntx_season": get_ntx_count_season(ntx_data),
        "mined_24hr": get_mined_count_24hr(mined_data),
        "mined_season": get_mined_count_season(mined_data),
        "biggest_block": get_biggest_block_season(mined_data),
        "season_stats_sorted": season_stats_sorted,
        "region_score_stats": get_region_score_stats(season_stats_sorted),
        "daily_stats_sorted": get_daily_stats_sorted(context["notaries"], context["dpow_coins_dict"]),
        "nn_social": get_nn_social_info(request)
    })
    return render(request, 'views/dash_index.html', context)
