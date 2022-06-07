#!/usr/bin/env python3
import time
from django.http import JsonResponse
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_mining as mining
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.serializers as serializers


def mined_count_daily_by_name(request):
    resp = mining.get_mined_count_daily_by_name(request)
    filters = ['mined_date']
    return helper.json_resp(resp, filters)


def mined_count_season_by_name(request):
    resp = mining.get_mined_count_season_by_name(request)
    filters = ['season']
    return helper.json_resp(resp, filters)


def notary_last_mined_table(request):
    resp = mining.get_notary_last_mined_table(request)
    filters = ['season']
    return helper.json_resp(resp, filters)


# USED FOR MINING ALERT IN DISCORD
def nn_mined_4hrs_api(request):
    mined_4hrs = query.get_mined_data().filter(
        block_time__gt=str(int(time.time()-4*60*60))
        ).values()
    serializer = serializers.minedSerializer(mined_4hrs, many=True)
    season = SEASON
    notary_list = helper.get_notary_list(season)
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
