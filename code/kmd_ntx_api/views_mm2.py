#!/usr/bin/env python3
import requests
from django.shortcuts import render
from .lib_helper import get_or_none

from kmd_ntx_api.lib_info import *
from kmd_ntx_api.lib_mm2 import *


def orderbook_view(request):
    context = {
        "season": get_page_season(request),
        "mm2_coins": get_mm2_coins(),
        "scheme_host": get_current_host(request),
        "sidebar_links": get_sidebar_links(season),
        "eco_data_link": get_eco_data_link()
    }
    orderbook = get_orderbook(request)

    if "bids" in orderbook:
        base = orderbook["base"]
        rel = orderbook["rel"]
        context.update({
            "base": base,
            "rel": rel
        })
        bids = []
        for bid in orderbook["bids"]:
            price = bid["price"]
            maxvolume = bid["maxvolume"]
            min_volume = bid["min_volume"]
            bids.append({
                "base": base,
                "rel": rel,
                "price": price,
                "maxvolume": maxvolume,
                "min_volume": min_volume,
                "base_total": float(maxvolume)/float(price)
            })

        context.update({
            "bids": bids
        })

    if "asks" in orderbook:
        base = orderbook["base"]
        rel = orderbook["rel"]
        context.update({
            "base": base,
            "page_title": f"AtomicDEX {base}/{rel} Orderbook",
            "rel": rel
        })

        asks = []
        for ask in orderbook["asks"]:
            price = ask["price"]
            maxvolume = ask["maxvolume"]
            min_volume = ask["min_volume"]
            asks.append({
                "base": base,
                "rel": rel,
                "price": price,
                "maxvolume": maxvolume,
                "min_volume": min_volume,
                "rel_total": float(maxvolume)*float(price)
            })

        context.update({
            "asks": asks
        })

    return render(request, 'mm2/mm2_orderbook.html', context)


def bestorders_view(request):
    coin = "KMD"
    if "coin" in request.GET:
        coin = request.GET["coin"]
    season = get_page_season(request)
    context = {
        "coin": coin,
        "season": season,
        "mm2_coins": get_mm2_coins(),
        "scheme_host": get_current_host(request),
        "sidebar_links": get_sidebar_links(season),
        "eco_data_link": get_eco_data_link()
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
        "bestorders": rows
    })

    return render(request, 'mm2/mm2_bestorders.html', context)


def mm2gui_view(request):
    swaps_data = get_swaps_data()
    since = "week"
    to_time = int(time.time())
    from_time = int(to_time - 60*60*24*14)
    if "from_time" in request.GET:
        from_time = int(request.GET["from_time"])
    if "to_time" in request.GET:
        to_time = int(request.GET["to_time"])
    if "since" in request.GET:
        since = request.GET["since"]
    swaps_data = filter_swaps_timespan(swaps_data, from_time, to_time)
    season = get_page_season(request)
    context = {
        "from_time": from_time,
        "to_time": to_time,
        "from_time_dt": dt.fromtimestamp(from_time),
        "to_time_dt": dt.fromtimestamp(to_time),
        "since_options": list(SINCE_INTERVALS.keys()),
        "since": since,
        "season": season,
        "swaps_counts": get_swaps_counts(swaps_data),
        "scheme_host": get_current_host(request),
        "sidebar_links": get_sidebar_links(season),
        "eco_data_link": get_eco_data_link()
    }

    return render(request, 'mm2/mm2_gui_stats.html', context)


def last200_swaps_view(request):
    season = get_page_season(request)
    last_200_swaps = get_last_200_swaps(request)
    last_200_swaps = format_gui_os_version(last_200_swaps)
    context = {
        "last_200_swaps": last_200_swaps,
        "season": season,
        "mm2_coins": get_mm2_coins(),
        "taker_coin": get_or_none(request, "taker_coin"),
        "maker_coin": get_or_none(request, "maker_coin"),
        "page_title": "Last 200 Swaps",
        "scheme_host": get_current_host(request),
        "sidebar_links": get_sidebar_links(season),
        "eco_data_link": get_eco_data_link()
    }

    return render(request, 'mm2/last_200_swaps.html', context)


def last200_failed_swaps_view(request):
    season = get_page_season(request)
    last_200_failed_swaps = get_last_200_failed_swaps(request)
    last_200_failed_swaps = format_gui_os_version(last_200_failed_swaps)

    context = {
        "last_200_failed_swaps": last_200_failed_swaps,
        "season": season,
        "mm2_coins": get_mm2_coins(),
        "taker_coin": get_or_none(request, "taker_coin"),
        "maker_coin": get_or_none(request, "maker_coin"),
        "page_title": "Last 200 Failed Swaps",
        "scheme_host": get_current_host(request),
        "sidebar_links": get_sidebar_links(season),
        "eco_data_link": get_eco_data_link()
    }

    return render(request, 'mm2/last_200_failed_swaps.html', context)
