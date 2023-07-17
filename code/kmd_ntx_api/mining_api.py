#!/usr/bin/env python3
import time
from django.http import JsonResponse
from kmd_ntx_api.mining import get_mined_data_24hr, get_mined_count_daily_by_name, \
    get_notary_mining, get_mined_count_season_by_name
from kmd_ntx_api.helper import json_resp, get_notary_list
from kmd_ntx_api.notary_seasons import get_page_season, get_season
from kmd_ntx_api.query import get_mined_data
from kmd_ntx_api.serializers import minedSerializer


def mined_count_daily_by_name(request):
    resp = get_mined_count_daily_by_name(request)
    filters = ['mined_date']
    return json_resp(resp, filters)


def notary_mining_api(request):
    resp = get_notary_mining(request)
    filters = ['notary, season']
    return json_resp(resp, filters)


def mining_24hrs_api(request):
    season = get_page_season(request)
    notary_list = get_notary_list(season)
    resp = get_mined_data_24hr().values()
    serializer = minedSerializer(resp, many=True)
    return json_resp(serializer.data)


def mined_count_season_by_name(request):
    resp = get_mined_count_season_by_name(request)
    filters = ['season']
    return json_resp(resp, filters)


# USED FOR MINING ALERT IN DISCORD
def nn_mined_4hrs_api(request):
    mined_4hrs = get_mined_data().filter(
        block_time__gt=str(int(time.time()-4*60*60))
        ).values()
    serializer = minedSerializer(mined_4hrs, many=True)
    notary_list = get_notary_list(get_season())
    mined_counts_4hr = {}
    for nn in notary_list:
        mined_counts_4hr.update({nn:0})
    for item in serializer.data:
        nn = item['name']
        if nn in mined_counts_4hr:
            count = mined_counts_4hr[nn] + 1
            mined_counts_4hr.update({nn:count})
        else:
            mined_counts_4hr.update({nn:1})
    return JsonResponse(mined_counts_4hr)
