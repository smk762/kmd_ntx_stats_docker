#!/usr/bin/env python3

from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework import permissions, viewsets

from kmd_ntx_api.serializers import *
from kmd_ntx_api.models import *
from kmd_ntx_api.lib_helper import get_season
from kmd_ntx_api.lib_query import get_notary_list 

def get_mined_count_season_table(request):
    resp = []
    data = mined_count_season.objects.all()

    if "season" in request.GET:
        season=request.GET["season"]

    elif len(data) == len(mined_count_season.objects.all()):
        season = get_season()
        
    data = mined_count_season.objects.filter(season=season).order_by('season', 'notary').values()

    # name num sum max last
    for item in data:
        blocks_mined = item['blocks_mined']
        if blocks_mined > 10:
            notary = item['notary']
            sum_value_mined = item['sum_value_mined']
            max_value_mined = item['max_value_mined']
            last_mined_block = item['last_mined_block']
            last_mined_blocktime = item['last_mined_blocktime']
            time_stamp = item['time_stamp']
            season = item['season']

            resp.append({
                    "notary":notary,
                    "blocks_mined":blocks_mined,
                    "sum_value_mined":sum_value_mined,
                    "max_value_mined":max_value_mined,
                    "last_mined_block":last_mined_block,
                    "last_mined_blocktime":last_mined_blocktime
            })

    return resp

def mined_count_season_table(request):
    resp = get_mined_count_season_table(request)
    return JsonResponse(resp, safe=False)
    
