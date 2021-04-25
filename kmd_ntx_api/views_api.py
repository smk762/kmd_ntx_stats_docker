#!/usr/bin/env python3
import time

from django.http import JsonResponse
from django.shortcuts import render

from kmd_ntx_api.lib_info import *

from kmd_ntx_api.viewsets_api import *
from kmd_ntx_api.views_page import *
from kmd_ntx_api.views_notary import *
from kmd_ntx_api.lib_testnet import get_api_testnet

logger = logging.getLogger("mylogger")

   

# API views (simple)
# TODO: Deprecate or merge into other url files
def api_sidebar_links(request):
    if 'season' in request.GET:
        season = request.GET["season"]
    else:
        season = "Season_4"
    resp = get_sidebar_links(season)
    return JsonResponse(resp)


# TODO: Deprecate after testnet ends
def api_testnet_totals(request):
    resp = get_api_testnet(request)
    return JsonResponse(resp)


# TODO: Awaiting delegation to crons / db table
def api_chain_sync(request):
    r = requests.get('http://138.201.207.24/show_sync_node_data')
    try:
        return JsonResponse(r.json())
    except:
        return JsonResponse({})


# USED FOR MINING ALERT IN DISCORD
def nn_mined_4hrs_api(request):
    mined_4hrs = get_mined_data().filter(
        block_time__gt=str(int(time.time()-4*60*60))
        ).values()
    serializer = minedSerializer(mined_4hrs, many=True)
    season = SEASON
    notary_list = get_notary_list(season)
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


#TODO: Deprecate once CHMEX migrates to new endpoint
def split_summary_api(request):
    resp = get_split_stats()
    return JsonResponse(resp)

