#!/usr/bin/env python3
import time
import logging
import logging.handlers

from django.http import JsonResponse
from django.shortcuts import render

from kmd_ntx_api.lib_helper import *
from kmd_ntx_api.lib_info import *
from kmd_ntx_api.lib_query import *
from kmd_ntx_api.api_viewsets import *
from kmd_ntx_api.page_views import *

logger = logging.getLogger("mylogger")

def chain_sync_api(request):
    r = requests.get('http://138.201.207.24/show_sync_node_data')
    try:
        return JsonResponse(r.json())
    except:
        return JsonResponse({})

def mining_24hrs_api(request):
    mined_24hrs = mined.objects.filter(
        block_time__gt=str(int(time.time()-24*60*60))
        ).values()
    serializer = MinedSerializer(mined_24hrs, many=True)
    return JsonResponse({'data': serializer.data})

def nn_mined_4hrs_api(request):
    mined_4hrs = mined.objects.filter(
        block_time__gt=str(int(time.time()-4*60*60))
        ).values()
    serializer = MinedSerializer(mined_4hrs, many=True)
    season = get_season(int(time.time()))
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

def nn_mined_last_api(request):
    season = get_season(int(time.time()))
    mined_last = mined.objects.filter(season=season).values("name").annotate(Max("block_time"),Max("block_height"))
    notary_list = get_notary_list(season)
    mined_last_dict = {}
    for item in mined_last:
        if item["name"] in notary_list:
            mined_last_dict.update({
                item["name"]:{
                    "blocktime":item["block_time__max"],
                    "blockheight":item["block_height__max"],
                }
            })

    return JsonResponse(mined_last_dict)

def ntx_24hrs_api(request):
    ntx_24hrs = notarised.objects.filter(
        block_time__gt=str(int(time.time()-24*60*60))
        ).values()
    serializer = NotarisedSerializer(ntx_24hrs, many=True)
    return JsonResponse({'data': serializer.data})




# Notary BTC TXID API Endpoints

def nn_btc_txid(request):
    if 'txid' in request.GET:
        resp = get_btc_txid_single(request.GET['txid'])
    else:
        resp = {"error":"You need to specify a TXID like '/nn_btc_txid?txid=86e23d8415737f1f6a723d1996f3e373e77d7e16a7ae8548b4928eb019237321'"}
    return JsonResponse(resp)

def address_btc_txids(request):
    if 'address' in request.GET and 'category' in request.GET:
        resp = get_btc_txid_address(request.GET['address'], request.GET['category'])
    elif 'address' in request.GET:
        resp = get_btc_txid_address(request.GET['address'])
    else:
        resp = {"error":"You need to specify an ADDRESS like '/address_btc_txids?address=1LtvR7B1zmvqKUeJkuaWYzSK2on8dS4u1h'. Category param is optional, e.g. '/address_btc_txids?address=1LtvR7B1zmvqKUeJkuaWYzSK2on8dS4u1h&category=NTX'"}
    return JsonResponse(resp)

def notary_btc_txids(request):
    if 'notary' in request.GET and 'category' in request.GET:
        resp = get_btc_txid_notary(request.GET['notary'], request.GET['category'])
    elif 'notary' in request.GET:
        resp = get_btc_txid_notary(request.GET['notary'])
    elif 'category' in request.GET:
        resp = get_btc_txid_notary(None, request.GET['category'])
    else:
        resp = {"error":"You need to specify a NOTARY or CATEGORY like '/nn_btc_txid?notary=dragonhound_NA' or '/nn_btc_txid?notary=dragonhound_NA&category=NTX'"}
    return JsonResponse(resp)

def nn_btc_txid_list(request):
    if 'season' in request.GET and 'notary' in request.GET:
        resp = get_btc_txid_list(request.GET['notary'], request.GET['season'])
    elif 'notary' in request.GET:
        resp = get_btc_txid_list(request.GET['notary'])
    elif 'season' in request.GET:
        resp = get_btc_txid_list(None, request.GET['season'])
    else:
        resp = get_btc_txid_list()
    distinct = len(list(set(resp['results'][0])))
    resp.update({"distinct":distinct})
    return JsonResponse(resp)

def nn_btc_txid_other(request):
    resp = get_btc_txid_data("other")
    return JsonResponse(resp)

def nn_btc_txid_ntx(request):
    resp = get_btc_txid_data("NTX")
    return JsonResponse(resp)

def nn_btc_txid_spam(request):
    resp = get_btc_txid_data("SPAM")
    return JsonResponse(resp)

def nn_btc_txid_raw(request):
    resp = get_btc_txid_data()
    return JsonResponse(resp)

def nn_btc_txid_splits(request):
    resp = get_btc_txid_data("splits")
    return JsonResponse(resp)

def split_summary_api(request):
    resp = get_split_stats()
    return JsonResponse(resp)

def split_summary_table(request):
    resp = get_split_stats_table()
    return JsonResponse(resp)

# TESTNET

def api_testnet_raw(request):
    resp = get_api_testnet(request, "raw")
    return JsonResponse(resp)

def api_testnet_raw_24hr(request):
    resp = get_api_testnet(request, "raw_24hr")
    return JsonResponse(resp)

def api_testnet_totals(request):
    resp = get_api_testnet(request, "totals")
    return JsonResponse(resp)

def api_btc_ntx_lag(request):
    resp = get_btc_ntx_lag(request)
    return JsonResponse(resp)

# sync lag graph
# daily ntx category stack graph
# monitor and detect suspicious NN fund exits. To other NN addr is ok, ntx is ok.
# date range mining/ntx for nn/chain

# NOTARY Profile:
# time since ntx graph

# COINS PROFILE (tabbed? changes ajax sources?)
# top section:
# -
# graphs: daily/season chain ntx, notary chain balances
# tables: daily/season chain ntx, notary chain balances
