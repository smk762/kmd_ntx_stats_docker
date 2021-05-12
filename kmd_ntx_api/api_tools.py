#!/usr/bin/env python3
import time
import math
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import permissions, viewsets, authentication
from kmd_ntx_api.serializers import addrFromBase58Serializer
from kmd_ntx_api.lib_info import get_all_coins
from kmd_ntx_api.lib_base58 import *
from kmd_ntx_api.lib_electrum import *


def addr_from_base58_tool(request):
    missing_params = []
    for x in addrFromBase58Serializer.Meta.fields:
        if x not in request.GET:
            example_params = "?pubkey=03b7621b44118017a16043f19b30cc8a4cfe068ac4e42417bae16ba460c80f3828&pubtype=60&wiftype=188&p2shtype=85"
            error = f"You need to specify params like '{example_params}'"
            return JsonResponse({
                "error":f"{error}",
                "note":f"Parameter values for some coins available at /api/info/base_58/"
                })

    resp = calc_addr_tool(request.GET["pubkey"], request.GET["pubtype"],
                         request.GET["p2shtype"], request.GET["wiftype"])
    return JsonResponse(resp)


def address_from_pubkey_tool(request):
    resp = get_address_from_pubkey(request)
    return JsonResponse(resp)


def get_address_from_pubkey(request):
    if "coin" in request.GET:
        coin = request.GET["coin"]
    else:
        coin = "KMD"
    if "pubkey" in request.GET:
        if coin in COIN_PARAMS:
            pubkey = request.GET["pubkey"]

            return {
                "coin": coin,
                "pubkey": pubkey,
                "address": calc_addr_from_pubkey(coin, pubkey)
            }

        else:
            return {
                "error": f"{coin} does not have locally defined COIN_PARAMS. If you know what these are, you can try the /api/tools/addr_from_base58 endpoint instead."
            }

    else:
        return {
            "error": "You need to specify a pubkey and coin, e.g '?coin=BTC&pubkey=03b7621b44118017a16043f19b30cc8a4cfe068ac4e42417bae16ba460c80f3828' (if coin not specified, it will default to KMD)"
        }


def get_notary_utxo_count(request):
    chain = None
    season = None
    server = None
    notary = None

    if "chain" in request.GET:
        chain = request.GET["chain"]
    if "season" in request.GET:
        season = request.GET["season"]
    if "server" in request.GET:
        server = request.GET["server"]
    if "notary" in request.GET:
        notary = request.GET["notary"]

    filters = ["notary", "chain", "season", "server"]
    if not chain or not notary or not server or not season:
        return JsonResponse({
            "filters":filters,
            "error": f"You need to specify all filter params: {filters}"
        })
    endpoint = f"{THIS_SERVER}/api/table/addresses"
    params = f"?season={season}&server={server}&chain={chain}&notary={notary}"
    addr_info = requests.get(f"{endpoint}/{params}").json()["results"]
    if len(addr_info) == 1:
        pubkey = addr_info[0]["pubkey"]
        resp = get_utxo_count(chain, pubkey, server)
        min_height = 999999999
        if "utxos" in resp:
            for item in resp["utxos"]:
                if item["height"] < min_height and item["height"] != 0:
                    min_height = item["height"]
            if min_height == 999999999:
                min_height = 0
            api_resp = {
                "block_tip":resp["block_tip"],
                "oldest_utxo_height":min_height,
                "dpow_utxo_count":resp["dpow_utxo_count"],
                "utxo_count":resp["utxo_count"],
                "utxos":resp["utxos"]
            }
            return JsonResponse({
                "filters":filters,
                "results":api_resp
            })
        else: 
            return JsonResponse({
                "filters":filters,
                "error": f"Bad electrum response! {resp}"
            })
    else:
        return JsonResponse({
            "filters":filters,
            "error": f"Unable to get pubkey for {server} {chain} {notary}"
        })


def get_kmd_rewards(request):
    address = None
    if "address" in request.GET:
        address = request.GET["address"]
    if not address:
        return JsonResponse({"error":"You need to specify an adddress, e.g ?address=RCyANUW2H5985zk8p6NHJfPyNBXnTVzGDh"})
    if len(address) != 34:
        return JsonResponse({"error":f"Invalid address: {address}"})
    else:

        kmd_tiptime = time.time()
        try:
            resp = requests.get(f"https://kmd.explorer.dexstats.info/insight-api-komodo/addr/{address}/utxo")
            utxos = resp.json()
        except:
            return  {"error":f"{resp.text}"}
        utxo_count = len(utxos)
        rewards_info = {
            "address": address,
            "utxo_count": utxo_count,
            "utxos":{}
        }
        total_rewards = 0
        balance = 0
        oldest_utxo_block = 99999999999
        for utxo in utxos:
            balance += utxo['satoshis']/100000000
            if "height" in utxo:
                if utxo['height'] < oldest_utxo_block:
                    oldest_utxo_block = utxo['height']
                if utxo['height'] < KOMODO_ENDOFERA and utxo['satoshis'] >= MIN_SATOSHIS:
                    url = f"https://kmd.explorer.dexstats.info/insight-api-komodo/tx/{utxo['txid']}"
                    resp = requests.get(url).json()
                    locktime = resp['locktime']
                    coinage = math.floor((kmd_tiptime-locktime)/ONE_HOUR)
                    if coinage >= ONE_HOUR and locktime >= LOCKTIME_THRESHOLD:
                        limit = ONE_YEAR
                        if utxo['height'] >= ONE_MONTH_CAP_HARDFORK:
                            limit = ONE_MONTH
                        reward_period = min(coinage, limit) - 59
                        utxo_rewards = math.floor(utxo['satoshis']/DEVISOR)*reward_period
                        if utxo_rewards < 0:
                            logger.info("Rewards should never be negative!")
                        rewards_info['utxos'].update({
                            utxo['txid']:{
                                "locktime":locktime,
                                "utxo_value":utxo['amount'],
                                "sat_rewards":utxo_rewards,
                                "kmd_rewards":utxo_rewards/100000000,
                                "satoshis":utxo['satoshis'],
                                "block_height":utxo['height']
                            }
                        })
                        total_rewards += utxo_rewards/100000000

        eligible_utxo_count = len(rewards_info['utxos'])
        if oldest_utxo_block == 99999999999:
            oldest_utxo_block = 0
        rewards_info.update({
            "eligible_utxo_count":eligible_utxo_count,
            "oldest_utxo_block":oldest_utxo_block,
            "kmd_balance":balance,
            "total_rewards":total_rewards
        })
        return JsonResponse(rewards_info)


def decode_op_return_tool(request):
    if 'OP_RETURN' in request.GET:
        coins_list = get_all_coins() 
        decoded = decode_opret(request.GET['OP_RETURN'], coins_list)
    else:
        decoded = {"error":"You need to include an OP_RETURN, e.g. '?OP_RETURN=fcfc5360a088f031c753b6b63fd76cec9d3e5f5d11d5d0702806b54800000000586123004b4d4400'"}
    return JsonResponse(decoded)


def validate_opret(OP_RETURN):
    coins_list = get_all_coins() 
    decoded = decode_opret(OP_RETURN, coins_list)
    if "error" in decoded:
        return False
    return True

