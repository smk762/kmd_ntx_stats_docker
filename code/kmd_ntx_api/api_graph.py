#!/usr/bin/env python3
from django.http import JsonResponse
import kmd_ntx_api.lib_graph as lib_graph
import kmd_ntx_api.lib_stats as lib_stats


def keys_to_list(_dict):
    _list = list(_dict.keys())
    _list.sort()
    return _list


def json_resp(resp, filters):

    if "error" in resp:
        return JsonResponse({
            "error": resp["error"],
            "filters": filters
        })

    return JsonResponse({
        "count": len(resp),
        "filters": filters,
        "results": resp
    })


def balances_graph(request):
    resp = lib_graph.get_balances_graph_data(request)
    filters = ['season', 'server', 'chain', 'notary']
    return json_resp(resp, filters)


def daily_ntx_graph(request):
    filters = ['notarised_date', 'server', 'chain', 'notary']
    resp = lib_graph.get_daily_ntx_graph_data(request)
    return json_resp(resp, filters)


def get_chart_json(data, axis_labels, chart_label, total):
    return {
        "chartdata": data,
        "labels": axis_labels,
        "chartLabel": chart_label,
        "total": total
    }


def get_mm2gui_piechart(request):

    resp = {}
    filters = ['since', 'from_time', 'to_time']
    stats_type = ["swap_total", "swap_pct", "pubkey_total"]

    swaps_gui_stats = lib_stats.get_swaps_gui_stats(request)
    stats = {
        "taker": swaps_gui_stats["taker"],
        "maker": swaps_gui_stats["maker"]
    }

    for side in ["taker", "maker"]:
        for x in stats_type:

            data = []
            total = 0
            axis_labels = []

            for category in keys_to_list(stats[side]):
                if category not in stats_type:
                    data.append(stats[side][category][x])
                    axis_labels.append(f"{category}")
                    total += stats[side][category][x]

            base_label = " ".join([i.title() for i in x.split("_")])
            chart_label = f"{side.title()} {base_label}"

            resp.update({
                f"{side}_{x}": get_chart_json(data, axis_labels, chart_label, total)
            })

    return json_resp(resp, filters)

# Distinct pubkeys
# Distinct GUIs

# Pubkeys have used which guis?

