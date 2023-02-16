#!/usr/bin/env python3
from django.http import JsonResponse
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_wallet as wallet
import kmd_ntx_api.lib_helper as helper

# Season > Server > Notary > Coin

def rewards_txids_wallet(request):
    data = wallet.get_distinct_rewards_txids(request).values()
    resp = {}
    for i in data:
        resp.update({"results":i})

    return JsonResponse(resp, safe=False)

def rewards_txid_wallet(request):
    data = wallet.get_rewards_txid(request).values()
    resp = {}
    for i in data:
        resp.update({"results":i})

    return JsonResponse(resp, safe=False)

def notary_addresses_wallet(request):
    data = wallet.get_source_addresses(request).values()
    resp = {}
    for item in data:
        season = item["season"]
        server = item["server"]
        notary = item["notary"]
        notary_id = item["notary_id"]
        address = item["address"]
        pubkey = item["pubkey"]
        coin = item["coin"]

        if season not in resp:
            resp.update({season: {}})
        if server not in resp[season]:
            resp[season].update({server: {}})
        if notary not in resp[season][server]:
            resp[season][server].update({notary: {
                "pubkey": pubkey,
                "notary_id": notary_id,
                "addresses": {}
            }})

        resp[season][server][notary]["addresses"].update({
            coin: address
        })

    return JsonResponse(resp)

# Season > Server > Coin > Notary


def coin_addresses_wallet(request):
    data = wallet.get_source_addresses(request).values()
    resp = {}
    for item in data:
        season = item["season"]
        server = item["server"]
        notary = item["notary"]
        address = item["address"]
        pubkey = item["pubkey"]
        coin = item["coin"]

        if season not in resp:
            resp.update({season: {}})
        if server not in resp[season]:
            resp[season].update({server: {}})
        if coin not in resp[season][server]:
            resp[season][server].update({coin: {}})

        resp[season][server][coin].update({
            notary: address
        })

    return JsonResponse(resp)

# Season > Server > Notary > Coin


def notary_balances_wallet(request):
    data = wallet.get_source_balances(request).values()
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
        if notary not in resp[season][server]:
            resp[season][server].update({notary: {}})
        if notary not in resp[season][server][notary]:
            resp[season][server][notary].update({
                coin: {}
            })

        resp[season][server][notary][coin].update({
            address: balance
        })

    return JsonResponse(resp)

# Season > Server > Coin > Notary


def coin_balances_wallet(request):
    data = wallet.get_source_balances(request).values()
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
