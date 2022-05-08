#!/usr/bin/env python3
from django.shortcuts import render
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_mining as mining

def mining_24hrs_view(request):
    season = helper.get_page_season(request)
    notary_list = helper.get_notary_list(season)
    mined_24hrs = mining.get_mined_data_24hr().values()

    context = helper.get_base_context(request)
    context.update({
        "page_title":"KMD Mining Last 24hrs",
        "mined_24hrs":mined_24hrs,
        "explorers":info.get_explorers(request)
    })
    return render(request, 'views/coin/mining_24hrs.html', context)


def mining_overview_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":f"Mining Overview",
        "explorers":info.get_explorers(request),
    })
    return render(request, 'views/coin/mining_overview.html', context)

