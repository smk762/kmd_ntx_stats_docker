#!/usr/bin/env python3
from django.http import JsonResponse
from kmd_ntx_api.lib_mm2 import *


def orderbook_api(request):
    return JsonResponse(get_orderbook(request))


def nn_mm2_stats_api(request):
    return JsonResponse(get_nn_mm2_stats(request), safe=False)


def nn_mm2_stats_by_hour_api(request):
    return JsonResponse(get_nn_mm2_stats_by_hour(request), safe=False)


def bestorders_api(request):
    return JsonResponse(get_orderbook(request))


def bestorders_api(request):
    return JsonResponse(get_orderbook(request))


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
