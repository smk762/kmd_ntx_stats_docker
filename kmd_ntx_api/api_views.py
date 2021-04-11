#!/usr/bin/env python3
import time

from django.http import JsonResponse
from django.shortcuts import render

from kmd_ntx_api.lib_info import *

from kmd_ntx_api.api_viewsets import *
from kmd_ntx_api.page_views import *
from kmd_ntx_api.notary_views import *
from kmd_ntx_api.lib_testnet import get_api_testnet

logger = logging.getLogger("mylogger")

def api_address_btc_txids(request):
    if 'address' in request.GET and 'category' in request.GET:
        resp = get_btc_txid_address(request.GET['address'], request.GET['category'])
    elif 'address' in request.GET:
        resp = get_btc_txid_address(request.GET['address'])
    else:
        resp = {"error":"You need to specify an ADDRESS like '/address_btc_txids?address=1LtvR7B1zmvqKUeJkuaWYzSK2on8dS4u1h'. Category param is optional, e.g. '/address_btc_txids?address=1LtvR7B1zmvqKUeJkuaWYzSK2on8dS4u1h&category=NTX'"}
    return JsonResponse(resp)

def api_btc_ntx_lag(request):
    resp = get_btc_ntx_lag(request)
    return JsonResponse(resp)
    
def api_dpow_server_coins_dict(request):
    if 'season' in request.GET:
        season = request.GET["season"]
    else:
        season = "Season_4"
    resp = get_dpow_server_coins_dict(season)
    return JsonResponse(resp)


def api_sidebar_links(request):
    if 'season' in request.GET:
        season = request.GET["season"]
    else:
        season = "Season_4"
    resp = get_sidebar_links(season)
    return JsonResponse(resp)


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

def api_mining_24hrs(request):
    mined_24hrs = get_mined_data_24hr().values()
    serializer = MinedSerializer(mined_24hrs, many=True)
    return JsonResponse({'data': serializer.data})

# TODO - add search and display frontend
def notarisation_txid(request):
    if 'txid' in request.GET:
        resp = get_notarised_data_txid(request.GET['txid'])
    else:
        resp = {"error":"You need to specify a TXID like '/notarisation_txid?txid=86e23d8415737f1f6a723d1996f3e373e77d7e16a7ae8548b4928eb019237321'"}
    return JsonResponse(resp)

def notary_btc_txids(request):
    if 'notary' in request.GET and 'category' in request.GET:
        resp = get_btc_txid_notary(request.GET['notary'], request.GET['category'])
    elif 'notary' in request.GET:
        resp = get_btc_txid_notary(request.GET['notary'])
    elif 'category' in request.GET:
        resp = get_btc_txid_notary(None, request.GET['category'])
    else:
        resp = {"error":"You need to specify a NOTARY or CATEGORY like '/notary_btc_txids?notary=dragonhound_NA' or '/nn_btc_txid?notary=dragonhound_NA&category=NTX'"}
    return JsonResponse(resp)

def notary_ltc_txids(request):
    if 'notary' in request.GET and 'category' in request.GET:
        resp = get_ltc_txid_notary(None, request.GET['notary'], request.GET['category'])
    elif 'notary' in request.GET:
        resp = get_ltc_txid_notary(None, request.GET['notary'])
    elif 'category' in request.GET:
        resp = get_ltc_txid_notary(None, None, request.GET['category'])
    else:
        resp = {"error":"You need to specify a NOTARY or CATEGORY like '/nn_ltc_txid?notary=dragonhound_NA' or '/nn_ltc_txid?notary=dragonhound_NA&category=NTX'"}
    return JsonResponse(resp)

def nn_btc_txid(request):
    if 'txid' in request.GET:
        results = get_btc_txid_single(request.GET['txid'])
        resp = {
            "results":results,
            "count":len(results)
        }

    else:
        resp = {"error":"You need to specify a TXID like '/nn_btc_txid?txid=86e23d8415737f1f6a723d1996f3e373e77d7e16a7ae8548b4928eb019237321'"}
    return JsonResponse(resp)

def nn_btc_txid_list(request):
    if 'season' in request.GET and 'notary' in request.GET:
        resp = get_nn_btc_tx_txid_list(request.GET['notary'], request.GET['season'])
    elif 'notary' in request.GET:
        resp = get_nn_btc_tx_txid_list(request.GET['notary'])
    elif 'season' in request.GET:
        resp = get_nn_btc_tx_txid_list(None, request.GET['season'])
    else:
        resp = get_nn_btc_tx_txid_list()
    distinct = len(list(set(resp)))
    api_resp = {
        "results":resp,
        "count":len(resp)
    }
    return JsonResponse(api_resp)

def nn_ltc_txid(request):
    if 'txid' in request.GET:
        results = get_nn_ltc_tx_txid(request.GET['txid'])
        resp = {
            "results":results,
            "count":len(results)
        }
    else:
        resp = {"error":"You need to specify a TXID like '/nn_ltc_txid?txid=86e23d8415737f1f6a723d1996f3e373e77d7e16a7ae8548b4928eb019237321'"}
    return JsonResponse(resp)


def nn_ltc_txid_list(request):
    if 'season' in request.GET and 'notary' in request.GET:
        resp = get_ltc_txid_list(request.GET['notary'], request.GET['season'])
    elif 'notary' in request.GET:
        resp = get_ltc_txid_list(request.GET['notary'])
    elif 'season' in request.GET:
        resp = get_ltc_txid_list(None, request.GET['season'])
    else:
        resp = get_ltc_txid_list()
    distinct = len(list(set(resp)))
    api_resp = {
        "distinct":distinct,
        "results":resp,
        "count":len(resp)
    }
    return JsonResponse(api_resp)


def chain_notarisation_txid_list(request):

    if 'season' in request.GET and 'chain' in request.GET:
        txid_list = get_chain_notarisation_txid_list(request.GET['chain'], request.GET['season'])

    elif 'chain' in request.GET:
        txid_list = get_chain_notarisation_txid_list(request.GET['chain'])

    else:
        return JsonResponse({"error":"You need to add a chain param like ?chain=PIRATE (season param is optional"})

    distinct = len(list(set(txid_list)))
    
    return JsonResponse({
        "count":distinct,
        "notarisation_txid_list":txid_list
        })


def nn_btc_txid_ntx(request):
    resp = get_btc_txid_data("NTX")
    return JsonResponse(resp)

def nn_btc_txid_splits(request):
    resp = get_btc_txid_data("splits")
    return JsonResponse(resp)


def nn_mined_4hrs_api(request):
    mined_4hrs = get_mined_data().filter(
        block_time__gt=str(int(time.time()-4*60*60))
        ).values()
    serializer = MinedSerializer(mined_4hrs, many=True)
    season = get_season()
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
    season = get_season()
    mined_last = get_mined_data(season).values("name").annotate(Max("block_time"),Max("block_height"))
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
    ntx_24hrs = get_notarised_data_24hr().values()
    serializer = NotarisedSerializer(ntx_24hrs, many=True)
    return JsonResponse({'data': serializer.data})

def split_summary_api(request):
    resp = get_split_stats()
    return JsonResponse(resp)

def split_summary_table(request):
    resp = get_split_stats_table()
    return JsonResponse(resp, safe=False)


def notarised_season_score(request):
    if "season" in request.GET and "chain" in request.GET:
        resp = get_notarised_season_score(request.GET["season"], request.GET["chain"])
    elif "season" in request.GET:
        resp = get_notarised_season_score(request.GET["season"])
    elif "chain" in request.GET:
        resp = get_notarised_season_score(None, request.GET["chain"])
    else:
        resp = get_notarised_season_score()
    return JsonResponse(resp)


