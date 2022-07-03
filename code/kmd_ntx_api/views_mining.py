#!/usr/bin/env python3
import random
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
        "mined_24hrs":mined_24hrs
    })
    return render(request, 'views/coin/mining_24hrs.html', context)


def mining_overview_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":f"Mining Overview",
    })
    return render(request, 'views/coin/mining_overview.html', context)


def notary_last_mined_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":f"Notary Last Mined"
    })
    return render(request, 'views/coin/notary_last_mined.html', context)


# TODO: Add Date Form to restrict results returned. merge with "last 24hrs?"
def notary_mining_view(request, notary=None):
    context = helper.get_base_context(request)
    if not context["notary"]:
        if not notary:
            notary_list = helper.get_notary_list(context["season"])
            notary = random.choice(context["notaries"])
        context.update({
            "notary": notary,
            "notary_clean": helper.get_notary_clean(notary)
        })

    context.update({
        "page_title": f"Mining"
    })

    return render(request, 'views/ntx/notary_mining.html', context)

