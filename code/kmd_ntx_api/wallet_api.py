#!/usr/bin/env python3
from django.http import JsonResponse

from kmd_ntx_api.wallet import get_source_addresses, get_source_balances


def notary_addresses_wallet(request) -> JsonResponse:
    # Season > Server > Notary > Coin
    data = get_source_addresses(request).values()
    resp = {}
    for item in data:
        season = item["season"]
        server = item["server"]
        notary = item["notary"]

        if season not in resp:
            resp.update({season: {}})
        if server not in resp[season]:
            resp[season].update({server: {}})
        if notary not in resp[season][server]:
            resp[season][server].update({notary: {
                "pubkey": item["pubkey"],
                "notary_id": item["notary_id"],
                "addresses": {}
            }})

        resp[season][server][notary]["addresses"].update({
            item["coin"]: item["address"]
        })

    return JsonResponse(resp)

def coin_addresses_wallet(request) -> JsonResponse:
    # Season > Server > Coin > Notary
    data = get_source_addresses(request).values()
    resp = {}
    for item in data:
        season = item["season"]
        server = item["server"]
        coin = item["coin"]

        if season not in resp:
            resp.update({season: {}})
        if server not in resp[season]:
            resp[season].update({server: {}})
        if coin not in resp[season][server]:
            resp[season][server].update({coin: {}})

        resp[season][server][coin].update({
            item["notary"]: item["address"]
        })

    return JsonResponse(resp)


def notary_balances_wallet(request) -> JsonResponse:
    # Season > Server > Notary > Coin
    data = get_source_balances(request).values()
    resp = {}
    for item in data:
        season = item["season"]
        server = item["server"]
        notary = item["notary"]
        coin = item["coin"]

        if season not in resp:
            resp.update({season: {}})
        if server not in resp[season]:
            resp[season].update({server: {}})
        if notary not in resp[season][server]:
            resp[season][server].update({notary: {}})
        if notary not in resp[season][server][notary]:
            resp[season][server][notary].update({
                coin: {}
            })

        resp[season][server][notary][coin].update({
            item["address"]: item["balance"]
        })

    return JsonResponse(resp)

# Season > Server > Coin > Notary


def coin_balances_wallet(request) -> JsonResponse:
    data = get_source_balances(request).values()
    resp = {}
    for item in data:
        season = item["season"]
        server = item["server"]
        notary = item["notary"]
        address = item["address"]
        coin = item["coin"]
        balance = item["balance"]

        if season not in resp:
            resp.update({season: {}})
        if server not in resp[season]:
            resp[season].update({server: {}})
        if coin not in resp[season][server]:
            resp[season][server].update({coin: {}})
        if notary not in resp[season][server]:
            resp[season][server][coin].update({
                notary: {}
            })

        resp[season][server][coin][notary].update({
            address: balance
        })

    return JsonResponse(resp)
