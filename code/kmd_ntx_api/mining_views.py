#!/usr/bin/env python3
import random
from django.shortcuts import render
from kmd_ntx_api.context import get_base_context
from kmd_ntx_api.helper import get_notary_clean
from kmd_ntx_api.mining import get_mined_data_24hr


def mining_24hrs_view(request):
    mined_24hrs = get_mined_data_24hr().values()
    context = get_base_context(request)
    context.update({
        "page_title":"KMD Mining Last 24hrs",
        "mined_24hrs":mined_24hrs
    })
    return render(request, 'views/mining/mining_24hrs.html', context)


def mining_overview_view(request):
    context = get_base_context(request)
    context.update({"page_title":f"Mining Overview"})
    return render(request, 'views/mining/mining_overview.html', context)


def notary_last_mined_view(request):
    context = get_base_context(request)
    context.update({"page_title":f"Notary Last Mined"})
    return render(request, 'views/mining/notary_last_mined.html', context)


# TODO: Add Date Form to restrict results returned. merge with "last 24hrs?"
def notary_mining_view(request, notary=None):
    context = get_base_context(request)
    if not notary:
        notary = random.choice(context["notaries"])
    context.update({
        "page_title": f"Mining",
        "notary": notary,
        "notary_clean": get_notary_clean(notary)
    })

    return render(request, 'views/ntx/notary_mining.html', context)
