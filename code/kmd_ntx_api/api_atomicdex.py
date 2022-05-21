#!/usr/bin/env python3
from django.http import JsonResponse
import kmd_ntx_api.lib_atomicdex as dex


def orderbook_api(request):
    return JsonResponse(dex.get_orderbook(request))


def seednode_version_date_table_api(request):
    return JsonResponse(dex.get_seednode_version_date_table(request), safe=False)


def seednode_version_month_table_api(request):
    return JsonResponse(dex.get_seednode_version_month_table(request), safe=False)


def bestorders_api(request):
    return JsonResponse(dex.get_bestorders(request))


def failed_swap_api(request):
    return JsonResponse(dex.get_failed_swap_by_uuid(request), safe=False)


def last_200_swaps_api(request):
    data = dex.get_last_200_swaps(request)
    data = dex.format_gui_os_version(data)
    return JsonResponse(data, safe=False)


def last_200_failed_swaps_api(request):
    data = dex.get_last_200_failed_swaps(request)
    data = dex.format_gui_os_version(data)
    return JsonResponse(data, safe=False)


def swaps_gui_stats_api(request):
    resp = dex.get_swaps_gui_stats(request)
    return JsonResponse(resp)


def swaps_pubkey_stats_api(request):
    resp = dex.get_swaps_pubkey_stats(request)
    return JsonResponse(resp)


def activation_commands_api(request):
    resp = dex.get_activation_commands(request)
    return JsonResponse(resp)
