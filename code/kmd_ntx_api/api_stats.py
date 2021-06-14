#!/usr/bin/env python3
from django.http import JsonResponse
from kmd_ntx_api.lib_stats import *


def swaps_gui_stats(request):
    resp = get_swaps_gui_stats(request)
    return JsonResponse(resp)


def swaps_pubkey_stats(request):
    resp = get_swaps_pubkey_stats(request)
    return JsonResponse(resp)
