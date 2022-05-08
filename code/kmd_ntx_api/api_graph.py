#!/usr/bin/env python3
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_graph as graph
import kmd_ntx_api.lib_helper as helper


def balances_graph(request):
    filters = ['season', 'server', 'coin', 'notary']
    resp = graph.get_balances_graph_data(request)
    return helper.json_resp(resp, filters)


def daily_ntx_graph(request):
    filters = ['notarised_date', 'server', 'coin', 'notary']
    resp = graph.get_daily_ntx_graph_data(request)
    return helper.json_resp(resp, filters)


def mm2gui_piechart(request):
    filters = ['since', 'from_time', 'to_time']
    resp = graph.get_mm2gui_piechart(request)
    return helper.json_resp(resp, filters)
    