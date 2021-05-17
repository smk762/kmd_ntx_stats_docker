#!/usr/bin/env python3
import requests
from django.http import JsonResponse
from django.shortcuts import render
from kmd_ntx_api.lib_helper import *
from kmd_ntx_api.lib_info import *

def doc_api_guide(request):
    season = get_page_season(request)
    context = {
        "season":season,
        "season_clean":season.replace("_"," "),
        "page_title":"API Documentation",
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link()
    }

    return render(request, 'docs/api_guide.html', context)

def yaml_api_guide(request):
    context = {}
    return render(request, 'docs/api_guide.yaml', content_type='text/yaml')

def json_api_guide(request):
    context = {}
    return render(request, 'docs/api_guide.json', content_type='text/json')
    #return JsonResponse('docs/api_guide.json')