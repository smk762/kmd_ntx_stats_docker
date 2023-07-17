#!/usr/bin/env python3
import time
from django.shortcuts import render
from datetime import datetime as dt
from kmd_ntx_api.const import SINCE_INTERVALS
from kmd_ntx_api.query import get_swaps_data, filter_swaps_timespan, get_swaps_counts
from kmd_ntx_api.helper import get_or_none
from kmd_ntx_api.context import get_base_context
from kmd_ntx_api.swaps import get_last_200_failed_swaps, format_gui_os_version


def recreate_swap_data_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": "Recreate failed swap data"
    })
    return render(request, 'views/atomicdex/recreate_swap_data.html', context)


def gui_stats_view(request):
    context = get_base_context(request)
    since = get_or_none(request, "since", "week")
    to_time = get_or_none(request, "to_time", int(time.time()))
    from_time = get_or_none(request, "from_time", int(to_time - SINCE_INTERVALS[since]))
    swaps_data = get_swaps_data()
    swaps_data = filter_swaps_timespan(swaps_data, from_time, to_time)

    context.update({
        "page_title": "AtomicDEX GUI Stats",
        "since": since,
        "since_options": list(SINCE_INTERVALS.keys()),
        "from_time": from_time,
        "from_time_dt": dt.utcfromtimestamp(from_time),
        "to_time": to_time,
        "to_time_dt": dt.utcfromtimestamp(to_time),
        "swaps_counts": get_swaps_counts(swaps_data)
    })

    return render(request, 'views/atomicdex/gui_stats.html', context)


def last_200_failed_swaps_view(request):
    context = get_base_context(request)
    last_200_failed_swaps = get_last_200_failed_swaps(request)
    last_200_failed_swaps = format_gui_os_version(last_200_failed_swaps)

    context.update({
        "last_200_failed_swaps": last_200_failed_swaps,
        "mm2_coins": True,
        "taker_coin": get_or_none(request, "taker_coin"),
        "maker_coin": get_or_none(request, "maker_coin"),
        "page_title": "Last 200 Failed Swaps"
    })

    return render(request, 'views/atomicdex/last_200_failed_swaps.html', context)

