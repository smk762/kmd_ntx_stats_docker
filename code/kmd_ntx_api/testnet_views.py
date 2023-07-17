#!/usr/bin/env python3
import requests
import datetime as dt
from datetime import datetime, timezone
from django.shortcuts import render
from kmd_ntx_api.helper import get_or_none
from kmd_ntx_api.vote import VOTE_YEAR, VOTE_PERIODS
from kmd_ntx_api.context import get_base_context


def testnet_ntx_scoreboard_view(request):
    context = get_base_context(request)
    year = get_or_none(request, "year", VOTE_YEAR)
    context.update({
        "year": year,
        "season": f"{year}_Testnet"
    })
    return render(request, 'views/vote/testnet_scoreboard.html', context)


def notary_vote_view(request):
    context = get_base_context(request)
    year = get_or_none(request, "year", VOTE_YEAR)
    context.update({
        "regions": ["AR", "EU", "NA", "SH"],
        "end_timestamp": VOTE_PERIODS[year]["max_blocktime"],
        "year": year
    })

    return render(request, 'views/vote/notary_vote.html', context)


def notary_vote_detail_view(request):
    context = get_base_context(request)
    year = get_or_none(request, "year", VOTE_YEAR)
    candidate = get_or_none(request, "candidate")
    context.update({
        "candidate": candidate,
        "end_timestamp": VOTE_PERIODS[year]["max_blocktime"],
        "year": year
    })

    return render(request, 'views/vote/notary_vote_detail.html', context)
