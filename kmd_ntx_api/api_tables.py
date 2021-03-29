#!/usr/bin/env python3

from django.http import JsonResponse
from kmd_ntx_api.lib_query import get_mined_count_season_table, get_epoch_scoring_table


def mined_count_season_table(request):
    resp = get_mined_count_season_table(request)
    return JsonResponse(resp, safe=False)
    

def epoch_scoring_table(request):
    resp = get_epoch_scoring_table(request)
    return JsonResponse(resp, safe=False)
    
