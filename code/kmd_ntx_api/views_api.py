#!/usr/bin/env python3
import time
from django.http import JsonResponse
from django.shortcuts import render
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.serializers as serializers

   
# API views (simple)
# TODO: Deprecate or merge into other url files
def api_sidebar_links(request):
    season = helper.get_page_season(request)
    resp = helper.get_sidebar_links(season)
    return JsonResponse(resp)


#TODO: Deprecate once CHMEX migrates to new endpoint
def split_summary_api(request):
    resp = info.get_split_stats()
    return JsonResponse(resp)

