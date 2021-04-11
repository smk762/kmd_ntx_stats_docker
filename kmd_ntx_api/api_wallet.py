#!/usr/bin/env python3
from django.http import JsonResponse

from kmd_ntx_api.lib_info import *


# ADDRESSES

def get_source_addresses_api(request):

    if 'season' in request.GET:
        season = request.GET["season"]
    else:
        season = None

    if 'server' in request.GET:
        server = request.GET["server"]
    else:
        server = None

    if 'chain' in request.GET:
        chain = request.GET["chain"]
    else:
        chain = None

    if 'notary' in request.GET:
        notary = request.GET["notary"]
    else:
        notary = None

    return get_addresses_data(season, server, chain, notary)

# Season > Server > Notary > Chain
def get_notary_addresses_api(request):
    data = get_source_addresses_api(request).values()
    resp = {}
    for item in data:
        season = item["season"]
        server = item["server"]
        notary = item["notary"]
        notary_id = item["notary_id"]
        address = item["address"]
        pubkey = item["pubkey"]
        chain = item["chain"]

        if season not in resp:
            resp.update({season:{}})
        if server not in resp[season]:
            resp[season].update({server:{}})
        if notary not in resp[season][server]:
            resp[season][server].update({notary:{
                "pubkey":pubkey,
                "notary_id":notary_id,
                "addresses":{}
            }})

        resp[season][server][notary]["addresses"].update({chain:address})

    return JsonResponse(resp)

# Season > Server > Chain > Notary
def get_chain_addresses_api(request):
    data = get_source_addresses_api(request).values()
    resp = {}
    for item in data:
        season = item["season"]
        server = item["server"]
        notary = item["notary"]
        address = item["address"]
        pubkey = item["pubkey"]
        chain = item["chain"]

        if season not in resp:
            resp.update({season:{}})
        if server not in resp[season]:
            resp[season].update({server:{}})
        if chain not in resp[season][server]:
            resp[season][server].update({chain:{}})

        resp[season][server][chain].update({notary:address})

    return JsonResponse(resp)


# BALANCES

def get_source_balances_api(request):

    if 'season' in request.GET:
        season = request.GET["season"]
    else:
        season = None

    if 'server' in request.GET:
        server = request.GET["server"]
    else:
        server = None

    if 'chain' in request.GET:
        chain = request.GET["chain"]
    else:
        chain = None

    if 'notary' in request.GET:
        notary = request.GET["notary"]
    else:
        notary = None

    return get_balances_data(season, server, chain, notary)

# Season > Server > Notary > Chain
def get_notary_balances_api(request):
    data = get_source_balances_api(request).values()
    resp = {}
    for item in data:
        season = item["season"]
        server = item["server"]
        notary = item["notary"]
        address = item["address"]
        chain = item["chain"]
        balance = item["balance"]

        if season not in resp:
            resp.update({season:{}})
        if server not in resp[season]:
            resp[season].update({server:{}})
        if notary not in resp[season][server]:
            resp[season][server].update({notary:{}})
        if notary not in resp[season][server][notary]:
            resp[season][server][notary].update({chain:{}})

        resp[season][server][notary][chain].update({address:balance})

    return JsonResponse(resp)

# Season > Server > Chain > Notary
def get_chain_balances_api(request):
    data = get_source_balances_api(request).values()
    resp = {}
    for item in data:
        season = item["season"]
        server = item["server"]
        notary = item["notary"]
        address = item["address"]
        chain = item["chain"]
        balance = item["balance"]

        if season not in resp:
            resp.update({season:{}})
        if server not in resp[season]:
            resp[season].update({server:{}})
        if chain not in resp[season][server]:
            resp[season][server].update({chain:{}})
        if notary not in resp[season][server]:
            resp[season][server][chain].update({notary:{}})

        resp[season][server][chain][notary].update({address:balance})


    return JsonResponse(resp)
