#!/usr/bin/env python3
from django.http import JsonResponse

from kmd_ntx_api.helper import json_resp
from kmd_ntx_api.swaps import get_swaps_gui_stats
from kmd_ntx_api.atomicdex import get_orderbook, get_bestorders
from kmd_ntx_api.swaps import get_failed_swap_by_uuid
from kmd_ntx_api.activation import get_activation_commands, get_coin_activation_commands
from kmd_ntx_api.seednodes import get_seednode_version_month_table, \
    get_seednode_version_score_total, get_seednode_version_date_table
from kmd_ntx_api.swaps import format_gui_os_version, get_last_200_failed_swaps_private, \
    get_last_200_failed_swaps, get_last_200_swaps
from kmd_ntx_api.table import get_orderbook_table


def orderbook_api(request):
    return JsonResponse(get_orderbook(request))


def orderbook_table_api(request):
    resp = get_orderbook_table(request)
    filters = ["base", "rel"]
    return json_resp(resp, filters)


def seednode_version_date_table_api(request):
    return JsonResponse(get_seednode_version_date_table(request), safe=False)


def seednode_version_month_table_api(request):
    return JsonResponse(get_seednode_version_month_table(request), safe=False)


def seednode_version_score_total_api(request):
    filters = ["season", "start", "end"]
    resp = get_seednode_version_score_total(request)
    return json_resp(resp, filters)
    

def bestorders_api(request):
    return JsonResponse(get_bestorders(request))


def failed_swap_api(request):
    return JsonResponse(get_failed_swap_by_uuid(request), safe=False)


def last_200_swaps_api(request):
    data = get_last_200_swaps(request)
    data = format_gui_os_version(data)
    return JsonResponse(data, safe=False)


def last_200_failed_swaps_api(request):
    data = get_last_200_failed_swaps(request)
    data = format_gui_os_version(data)
    return JsonResponse(data, safe=False)


def last_200_failed_swaps_private_api(request):
    data = get_last_200_failed_swaps_private(request)
    data = format_gui_os_version(data)
    return JsonResponse(data, safe=False)


def swaps_gui_stats_api(request):
    resp = get_swaps_gui_stats(request)
    return JsonResponse(resp)


def activation_commands_api(request):
    resp = get_activation_commands(request)
    return JsonResponse(resp)

def coin_activation_commands_api(request):
    resp = get_coin_activation_commands(request)
    return JsonResponse(resp)
