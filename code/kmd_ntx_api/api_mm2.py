#!/usr/bin/env python3
from django.http import JsonResponse

from kmd_ntx_api.lib_mm2 import *

def orderbook_api(request):
    return JsonResponse(get_orderbook(request))

def bestorders_api(request):
    return JsonResponse(get_bestorders(request))
