#!/usr/bin/env python3
import random
import numpy as np
from datetime import datetime as dt
from django.shortcuts import render

from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_stats as stats
import kmd_ntx_api.lib_graph as graph
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_mining as mining
import kmd_ntx_api.lib_table as table
import kmd_ntx_api.lib_wallet as wallet



def notarised_tenure_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":f"Coin Notarisation Tenure"
    })
    return render(request, 'views/ntx/notarised_tenure.html', context)


def coins_last_ntx(request):
    season = helper.get_page_season(request)
    context = helper.get_base_context(request)
    server = helper.get_page_server(request)
    coin = helper.get_or_none(request, "coin")
    context.update({
        "page_title": f"dPoW Last Coin Notarisations",    
        "server": server,
        "coin": coin
    })

    return render(request, 'views/ntx/coins_last_ntx.html', context)


def coin_notarised_24hrs_view(request):
    coin = helper.get_or_none(request, "coin", "MORTY")
    context = helper.get_base_context(request)
    context.update({
        "coin": coin,
    })
    return render(request, 'views/coin/coin_notarised_24hrs.html', context)

