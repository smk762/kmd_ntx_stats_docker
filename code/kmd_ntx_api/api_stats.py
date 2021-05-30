#!/usr/bin/env python3
from django.http import JsonResponse
from kmd_ntx_api.lib_stats import *


def swaps_gui_stats(request):
    to_time = int(time.time())
    from_time = 1
    if "since" in request.GET:
        if request.GET["since"] in SINCE_INTERVALS:
            from_time = to_time - SINCE_INTERVALS[request.GET["since"]]
    if "from_time" in request.GET:
        from_time = int(request.GET["from_time"])
    if "to_time" in request.GET:
        to_time = int(request.GET["to_time"])
    resp = get_swaps_gui_stats(from_time, to_time)
    return JsonResponse(resp)


def swaps_pubkey_stats(request):
    to_time = int(time.time())
    from_time = 1
    if "since" in request.GET:
        if request.GET["since"] in SINCE_INTERVALS:
            from_time = to_time - SINCE_INTERVALS[request.GET["since"]]
    if "from_time" in request.GET:
        from_time = int(request.GET["from_time"])
    if "to_time" in request.GET:
        to_time = int(request.GET["to_time"])
    resp = get_swaps_pubkey_stats(from_time, to_time)
    return JsonResponse(resp)
