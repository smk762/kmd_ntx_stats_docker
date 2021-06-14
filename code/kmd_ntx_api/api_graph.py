#!/usr/bin/env python3
from django.http import JsonResponse
from kmd_ntx_api.lib_graph import *
from kmd_ntx_api.lib_stats import *

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

def get_mm2gui_piechart(request):
    resp = {}
    swaps_gui_stats = get_swaps_gui_stats(request)

    taker_stats = swaps_gui_stats["taker"]

    taker_categories = list(taker_stats.keys())
    taker_categories.sort()
    taker_category_stats = []
    taker_category_stats_labels = []
    for category in taker_categories:
        if category not in ["swap_total", "swap_pct", "pubkey_total"]:
            taker_category_stats.append(taker_stats[category]["swap_total"])
            taker_category_stats_labels.append(category)

    resp.update({
        "taker_totals": {
            "chartdata": taker_category_stats,
            "labels": taker_category_stats_labels,
            "chartLabel": "Taker swap totals"
        }
    })

    taker_category_stats = []
    taker_category_stats_labels = []
    for category in taker_categories:
        if category not in ["swap_total", "swap_pct", "pubkey_total"]:
            taker_category_stats.append(taker_stats[category]["swap_pct"])
            taker_category_stats_labels.append(category)

    resp.update({
        "taker_pct": {
            "chartdata": taker_category_stats,
            "labels": taker_category_stats_labels,
            "chartLabel": "Taker swap totals"
        }
    })

    taker_category_stats = []
    taker_category_stats_labels = []
    for category in taker_categories:
        if category not in ["swap_total", "swap_pct", "pubkey_total"]:
            taker_category_stats.append(taker_stats[category]["pubkey_total"])
            taker_category_stats_labels.append(category)

    resp.update({
        "taker_pubkey_total": {
            "chartdata": taker_category_stats,
            "labels": taker_category_stats_labels,
            "chartLabel": "Taker Pubkey totals"
        }
    })

    maker_stats = swaps_gui_stats["maker"]
    maker_categories = list(maker_stats.keys())
    maker_categories.sort()
    maker_category_stats = []
    maker_category_stats_labels = []
    for category in maker_categories:
        if category not in ["swap_total", "swap_pct", "pubkey_total"]:
            maker_category_stats.append(maker_stats[category]["swap_total"])
            maker_category_stats_labels.append(category)

    resp.update({
        "maker_totals": {
            "chartdata": maker_category_stats,
            "labels": maker_category_stats_labels,
            "chartLabel": "Maker swap totals"
        }
    })

    maker_category_stats = []
    maker_category_stats_labels = []
    for category in maker_categories:
        if category not in ["swap_total", "swap_pct", "pubkey_total"]:
            maker_category_stats.append(maker_stats[category]["swap_pct"])
            maker_category_stats_labels.append(category)

    resp.update({
        "maker_pct": {
            "chartdata": maker_category_stats,
            "labels": maker_category_stats_labels,
            "chartLabel": "Maker swap totals"
        }
    })

    maker_category_stats = []
    maker_category_stats_labels = []
    for category in maker_categories:
        if category not in ["swap_total", "swap_pct", "pubkey_total"]:
            maker_category_stats.append(maker_stats[category]["pubkey_total"])
            maker_category_stats_labels.append(category)

    resp.update({
        "maker_pubkey_total": {
            "chartdata": maker_category_stats,
            "labels": maker_category_stats_labels,
            "chartLabel": "Maker Pubkey totals"
        }
    })

    filters = ['since', 'from_time', 'to_time']
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