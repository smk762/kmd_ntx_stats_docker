#!/usr/bin/env python3
import random
from django.http import JsonResponse
from kmd_ntx_api.lib_info import *

from kmd_ntx_api.lib_table import get_mined_count_season_data_table, get_epoch_scoring_table, get_notary_epoch_scoring_table


def mined_count_season_table(request):
    resp = get_mined_count_season_data_table(request)
    return JsonResponse(resp, safe=False)
    

def epoch_scoring_table(request):
    resp = get_epoch_scoring_table(request)
    return JsonResponse(resp, safe=False)
    
def api_table_notary_epoch_scoring(request):
    if not "season" in request.GET:
        season = "Season_4"
    else:
        season = request.GET["season"]

    notary_list = get_notary_list(season)
    if not "notary" in request.GET:
        notary = random.choice(notary_list)
    else:
        notary = request.GET["notary"]

    resp = get_notary_epoch_scoring_table(notary, season)[0]
    return JsonResponse(resp, safe=False)
    
