#!/usr/bin/env python3
from kmd_ntx_api.graph import get_balances_graph_data, get_daily_ntx_graph_data, \
    get_mm2gui_piechart, get_mined_xy_data, get_supply_xy_data
from kmd_ntx_api.helper import json_resp, region_sort
from kmd_ntx_api.colors import COLORS

def balances_graph(request):
    filters = ['season', 'server', 'coin', 'notary']
    resp = get_balances_graph_data(request)
    return json_resp(resp, filters)


def daily_ntx_graph(request):
    filters = ['notarised_date', 'server', 'coin', 'notary']
    resp = get_daily_ntx_graph_data(request)
    return json_resp(resp, filters)


def mm2gui_piechart(request):
    filters = ['since', 'from_time', 'to_time']
    resp = get_mm2gui_piechart(request)
    return json_resp(resp, filters)


def mined_xy_data(request):
    filters = ['since', 'from_time', 'to_time']
    resp = get_mined_xy_data(request)
    return json_resp(resp, raw=True)
    


def supply_xy_data(request):
    filters = ['since', 'from_time', 'to_time']
    resp = get_supply_xy_data(request)
    return json_resp(resp, raw=True)
    
def prepare_regional_graph_data(graph_data):
    bg_color = []
    border_color = []
    chartdata = []
    chartLabel = ""

    labels = list(graph_data.keys())
    labels.sort()
    labels = region_sort(labels)

    for label in labels:
        if label.endswith("_AR"):
            bg_color.append(COLORS["AR_REGION"])
        elif label.endswith("_EU"):
            bg_color.append(COLORS["EU_REGION"])
        elif label.endswith("_NA"):
            bg_color.append(COLORS["NA_REGION"])
        elif label.endswith("_SH"):
            bg_color.append(COLORS["SH_REGION"])
        else:
            bg_color.append(COLORS["DEV_REGION"])
        border_color.append(COLORS["BLACK"])

    chartdata = []
    for label in labels:
        chartdata.append(graph_data[label])
    
    data = { 
        "labels": labels, 
        "chartLabel": chartLabel, 
        "chartdata": chartdata, 
        "bg_color": bg_color, 
        "border_color": border_color, 
    } 
    return data


def prepare_coins_graph_data(graph_data, dpow_coins_dict):
    bg_color = []
    border_color = []
    chartdata = []
    chartLabel = ""

    labels = list(graph_data.keys())
    labels.sort()

    main_coins = dpow_coins_dict["Main"]
    third_coins = dpow_coins_dict["Third_Party"]

    for label in labels:
        if label in third_coins:
            bg_color.append(COLORS["THIRD_PARTY_COLOR"])
        elif label in main_coins:
            bg_color.append(COLORS["MAIN_COLOR"])
        else:
            bg_color.append(COLORS["OTHER_COIN_COLOR"])
        border_color.append(COLORS["BLACK"])

    chartdata = []
    for label in labels:
        chartdata.append(graph_data[label])
    
    data = { 
        "labels": labels, 
        "chartLabel": chartLabel, 
        "chartdata": chartdata, 
        "bg_color": bg_color, 
        "border_color": border_color, 
    } 
    return data
