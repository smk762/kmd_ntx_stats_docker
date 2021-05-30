#!/usr/bin/env python3
import requests
from django.shortcuts import render

from kmd_ntx_api.lib_info import *
from kmd_ntx_api.lib_mm2 import *

def orderbook_view(request):
    season = get_page_season(request)
    mm2_coins = get_mm2_coins()
    context = {
        "season":season,
        "mm2_coins":mm2_coins,
        "scheme_host":get_current_host(request),
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link()
    } 
    orderbook = get_orderbook(request)

    if "bids" in orderbook:
        base = orderbook["base"]
        rel = orderbook["rel"]
        context.update({
            "base":base,
            "rel":rel
        })
        bids = []
        for bid in orderbook["bids"]:
            price = bid["price"]
            maxvolume = bid["maxvolume"]
            min_volume = bid["min_volume"]
            bids.append({
                "base":base,
                "rel":rel,
                "price":price,
                "maxvolume":maxvolume,
                "min_volume":min_volume,
                "base_total":float(maxvolume)/float(price)
            })

        context.update({
            "bids": bids
        })

    if "asks" in orderbook:
        base = orderbook["base"]
        rel = orderbook["rel"]
        context.update({
            "base":base,
            "page_title":f"AtomicDEX {base}/{rel} Orderbook",
            "rel":rel
        })

        asks = []
        for ask in orderbook["asks"]:
            price = ask["price"]
            maxvolume = ask["maxvolume"]
            min_volume = ask["min_volume"]
            asks.append({
                "base":base,
                "rel":rel,
                "price":price,
                "maxvolume":maxvolume,
                "min_volume":min_volume,
                "rel_total":float(maxvolume)*float(price)
            })

        context.update({
            "asks":asks
        })


    return render(request, 'mm2/mm2_orderbook.html', context)

def bestorders_view(request):
    coin = "KMD"
    if "coin" in request.GET:
        coin = request.GET["coin"]
    season = get_page_season(request)
    mm2_coins = get_mm2_coins()
    context = {
        "coin":coin,
        "season":season,
        "mm2_coins":mm2_coins,
        "scheme_host":get_current_host(request),
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link()
    } 
    bestorders = get_bestorders(request)["result"]
    rows = []
    for coin in bestorders:
        rows.append({
            "coin": coin,
            "price": bestorders[coin][0]["price"],
            "maxvolume": bestorders[coin][0]["maxvolume"],
            "min_volume": bestorders[coin][0]["min_volume"],
        })

    context.update({
        "bestorders":rows
    })


    return render(request, 'mm2/mm2_bestorders.html', context)
