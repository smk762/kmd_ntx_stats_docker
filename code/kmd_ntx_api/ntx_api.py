#!/usr/bin/env python3
from kmd_ntx_api.helper import get_or_none, get_page_server, json_resp
from kmd_ntx_api.notary_seasons import get_page_season
from kmd_ntx_api.ntx import get_notarised_date, get_ntx_tenure_table
from kmd_ntx_api.stats import get_season_stats_sorted, get_daily_stats_sorted
from kmd_ntx_api.serializers import notarisedSerializer


def notarised_date_api(request):
    season = get_page_season(request)
    server = get_page_server(request)
    coin = get_or_none(request, "coin")
    notary = get_or_none(request, "notary")
    last_24hrs = get_or_none(request, "last_24hrs", False) == 'true'
    data = get_notarised_date(season, server, coin, notary, last_24hrs)
    serializer = notarisedSerializer(data, many=True)
    filters = ['season', 'server', 'coin', 'notary']
    return json_resp(serializer.data, filters)


def ntx_tenture_api(request):
    data = get_ntx_tenure_table(request)
    filters = ['season', 'server', 'coin']
    return json_resp(data, filters)


def season_stats_sorted_api(request):
    season = get_page_season(request)
    data = get_season_stats_sorted(season)
    filters = ['season']
    return json_resp(data, filters)


def daily_stats_sorted_api(request):
    season = get_page_season(request)
    data = get_daily_stats_sorted(season)
    filters = []
    return json_resp(data, filters)
