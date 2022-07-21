#!/usr/bin/env python3
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_ntx as ntx
import kmd_ntx_api.lib_stats as stats
import kmd_ntx_api.serializers as serializers


def notarised_date_api(request):
    season = helper.get_page_season(request)
    server = helper.get_page_server(request)
    coin = helper.get_or_none(request, "coin")
    notary = helper.get_or_none(request, "notary")
    last_24hrs = helper.get_or_none(request, "last_24hrs", False) == 'true'
    data = ntx.get_notarised_date(season, server, coin, notary, last_24hrs)
    serializer = serializers.notarisedSerializer(data, many=True)
    filters = ['season', 'server', 'coin', 'notary']
    return helper.json_resp(serializer.data, filters)


def ntx_tenture_api(request):
    data = ntx.get_ntx_tenure_table(request)
    filters = ['season', 'server', 'coin']
    return helper.json_resp(data, filters)


def season_stats_sorted_api(request):
    season = helper.get_page_season(request)
    data = stats.get_season_stats_sorted(season)
    filters = ['season']
    return helper.json_resp(data, filters)


def daily_stats_sorted_api(request):
    season = helper.get_page_season(request)
    data = stats.get_daily_stats_sorted(season)
    filters = []
    return helper.json_resp(data, filters)
