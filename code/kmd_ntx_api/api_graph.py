#!/usr/bin/env python3
from django.http import JsonResponse
from kmd_ntx_api.lib_graph import *

# Graphs

def balances_graph(request):

    resp = get_balances_graph_data(request)
    filters = ['season', 'server', 'chain', 'notary']
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def daily_ntx_graph(request):
    filters = ['notarised_date', 'server', 'chain', 'notary']
    resp = get_daily_ntx_graph_data(request)
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })
