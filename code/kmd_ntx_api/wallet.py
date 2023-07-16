#!/usr/bin/env python3
from kmd_ntx_api.notary_seasons import get_page_season
from kmd_ntx_api.helper import get_or_none, get_page_server
from kmd_ntx_api.query import get_addresses_data, get_balances_data


def get_source_addresses(request):
    season = get_page_season(request)
    server = get_page_server(request)
    coin = get_or_none(request, "coin")
    notary = get_or_none(request, "notary")
    return get_addresses_data(season, server, coin, notary)


def get_source_balances(request):
    season = get_page_season(request)
    server = get_page_server(request)
    coin = get_or_none(request, "coin")
    notary = get_or_none(request, "notary")
    return get_balances_data(season, server, coin, notary)
