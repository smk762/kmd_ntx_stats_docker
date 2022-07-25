#!/usr/bin/env python3
import math
import random
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_electrum as electrum
import kmd_ntx_api.lib_dexstats as dexstats
import kmd_ntx_api.lib_base58 as b58
import kmd_ntx_api.serializers as serializers


def get_addr_from_base58(request):
    
    for x in serializers.addrFromBase58Serializer.Meta.fields:
        if x not in request.GET:
            example_params = "?pubkey=03b7621b44118017a16043f19b30cc8a4cfe068ac4e42417bae16ba460c80f3828&pubtype=60&wiftype=188&p2shtype=85"
            error = f"You need to specify params like '{example_params}'"
            return {
                "error":f"{error}",
                "note":f"Parameter values for some coins available at /api/info/base_58/"
            }

    return b58.calc_addr_tool(request.GET["pubkey"], request.GET["pubtype"],
                              request.GET["p2shtype"], request.GET["wiftype"])

def get_address_conversion(request):
    address = helper.get_or_none(request, "address")
    if not address:
        return {"error": "You need to specify an address, like ?address=17VZNX1SN5NtKa8UQFxwQbFeFc3iqRYhem"}
    return b58.convert_addresses(address)


def get_decode_op_return(request):
    op_return = helper.get_or_none(request, "OP_RETURN")
    if not op_return:
        return {"error": "You need to include an OP_RETURN, e.g. '?OP_RETURN=fcfc5360a088f031c753b6b63fd76cec9d3e5f5d11d5d0702806b54800000000586123004b4d4400'"}
    else:
        try:
            resp = b58.decode_opret(op_return)
        except Exception as e:
            resp = {"error": e}
    return resp


def get_pubkey_utxos(request):
    pubkey = helper.get_or_none(request, "pubkey")
    coin = helper.get_or_none(request, "coin")

    if not coin or not pubkey:
        return {"error": f"You need to specify all filter params"}

    resp = get_utxos(coin, pubkey)

    min_height = 999999999
    if "utxos" in resp:
        for item in resp["utxos"]:
            if "height" in item: # avoid unconfirmed
                if item["height"] < min_height and item["height"] != 0:
                    min_height = item["height"]
        if min_height == 999999999:
            min_height = 0

        return {
            "count": resp["utxo_count"],
            "results": {
                "block_tip":resp["block_tip"],
                "oldest_utxo_height":min_height,
                "dpow_utxo_count":resp["dpow_utxo_count"],
                "utxos":resp["utxos"]
            }
        }

    else: 
        return resp


def get_utxos(coin, pubkey):
    if coin in dexstats.DEXSTATS_COINS:
        address = b58.calc_addr_from_pubkey(coin, pubkey)
        block_tip = dexstats.get_sync(coin)["height"]
        resp = dexstats.get_dexstats_utxos(coin, address)

        utxos = []
        utxo_count = 0
        dpow_utxo_count = 0

        for item in resp:

            if item['satoshis'] == 10000:
                dpow_utxo_count += 1
                item.update({"dpow_utxo": True})
            else:
                item.update({"dpow_utxo": False})

            utxo_count += 1
            utxos.append(item)

        return {
            "block_tip": block_tip,
            "utxo_count": utxo_count,
            "dpow_utxo_count": dpow_utxo_count,
            "utxos": utxos
        }            

    else:
        url, port, ssl = electrum.get_coin_electrum(coin)

        if url:
            utxos = []
            utxo_count = 0
            dpow_utxo_count = 0
            p2pk_scripthash = electrum.get_p2pk_scripthash_from_pubkey(pubkey)
            p2pkh_scripthash = electrum.get_p2pkh_scripthash_from_pubkey(pubkey)

            if ssl:
                headers_resp = electrum.get_from_electrum_ssl(
                    url, port, 'blockchain.headers.subscribe')

                p2pk_resp = electrum.get_from_electrum_ssl(
                    url, port, 'blockchain.scripthash.listunspent',
                    p2pk_scripthash)

                p2pkh_resp = electrum.get_from_electrum_ssl(
                    url, port, 'blockchain.scripthash.listunspent',
                    p2pkh_scripthash)

                block_tip = headers_resp['result']['height']
                resp = p2pk_resp['result'] + p2pkh_resp['result']

            else:
                headers_resp = electrum.get_from_electrum(
                    url, port, 'blockchain.headers.subscribe')

                p2pk_resp = electrum.get_from_electrum(
                    url, port, 'blockchain.scripthash.listunspent',
                    p2pk_scripthash)

                p2pkh_resp = electrum.get_from_electrum(
                    url, port, 'blockchain.scripthash.listunspent',
                    p2pkh_scripthash)

            block_tip = headers_resp['result']['height']
            resp = p2pk_resp['result'] + p2pkh_resp['result']

            for item in resp:
                if item["value"] > 0:
                    utxos.append(item)

            if coin in ["AYA", "EMC2", "SFUSD"]:
                utxo_size = 100000
            else:
                utxo_size = 10000

            for item in utxos:
                utxo_count += 1
                if item['value'] == utxo_size:
                    dpow_utxo_count += 1
                    item.update({"dpow_utxo": True})
                else:
                    item.update({"dpow_utxo": False})

            return {
                "block_tip": block_tip,
                "utxo_count": utxo_count,
                "dpow_utxo_count": dpow_utxo_count,
                "utxos": utxos,
            }

        else:
            return {"error": f"No electrum found for {coin}"}


def get_scripthash_from_address(request):
    address = helper.get_or_none(request, "address")
    if address:
        try:
            scripthash = electrum.get_p2pkh_scripthash_from_address(address)
            p2pkh = b58.address_to_p2pkh(address)
            return {
                "address":f"{address}",
                "p2pkh_scripthash":f"{scripthash}",
                "p2pkh":f"{p2pkh}"
            }
        except Exception as e:
            return {
                "error":f"{e}"
            }
    return {"error": "You need to specify an address, like ?address=17VZNX1SN5NtKa8UQFxwQbFeFc3iqRYhem"}



def get_scripthashes_from_pubkey(request):
    pubkey = helper.get_or_none(request, "pubkey")
    if pubkey:
        try:
            p2pkh_scripthash = electrum.get_p2pkh_scripthash_from_pubkey(pubkey)
            p2pk_scripthash = electrum.get_p2pk_scripthash_from_pubkey(pubkey)
            p2pkh = b58.pubkey_to_p2pkh(pubkey)
            p2pk = b58.pubkey_to_p2pk(pubkey)

            return {
                "pubkey":f"{pubkey}",
                "p2pkh_scripthash":f"{p2pkh_scripthash}",
                "p2pk_scripthash":f"{p2pk_scripthash}",
                "p2pkh":f"{p2pkh}",
                "p2pk":f"{p2pk}"
            }

        except Exception as e:
            return {
                "error":f"{e}"
            }

    return {"error": "You need to specify a pubkey, like ?pubkey=<PUBKEY>"}


def get_kmd_rewards(request):
    address = helper.get_or_none(request, "address")
    utxos = []
    balance = 0
    total_rewards = 0
    utxo_count = 0
    eligible_utxo_count = 0
    kmd_tiptime = time.time()
    rewards_info = {"results": {
            "utxos": [],
            "utxo_list": []
        }
    }
    oldest_utxo_block = 99999999999

    if not address or address == "":
        oldest_utxo_block = "N/A"
        rewards_info.update({
            "error": "You need to specify an adddress, e.g ?address=RCyANUW2H5985zk8p6NHJfPyNBXnTVzGDh"
        })

    elif len(address) != 34:
        oldest_utxo_block = "N/A"
        rewards_info.update({
            "error": f"Invalid address: {address}"
        })

    else:
        try:
            resp = requests.get(f"https://kmd.explorer.dexstats.info/insight-api-komodo/addr/{address}/utxo")
            utxos = resp.json()
        except Exception as e:
            oldest_utxo_block = "N/A"
            rewards_info.update({
                "error": f"{resp.text} - {e}"
            })

        if not isinstance(utxos, list):
            utxos = []

        utxo_count = len(utxos)

        if utxo_count == 0 and 'error' not in rewards_info:
            oldest_utxo_block = "N/A"
            rewards_info.update({
                "error": f"{address} has no balance!"
            })
        for utxo in utxos:
            balance += utxo['satoshis']/100000000

            utxo_amount = utxo['amount']
            if "height" in utxo:
                if utxo["height"] < oldest_utxo_block:
                    oldest_utxo_block = utxo['height']

                if utxo["height"] < KOMODO_ENDOFERA and utxo["satoshis"] >= MIN_SATOSHIS:
                    url = f"https://kmd.explorer.dexstats.info/insight-api-komodo/tx/{utxo['txid']}"
                    resp = requests.get(url).json()
                    locktime = resp["locktime"]
                    utxo_age = int(kmd_tiptime - locktime)
                    coinage = math.floor((kmd_tiptime-locktime)/ONE_HOUR)

                    if coinage >= ONE_HOUR and locktime >= LOCKTIME_THRESHOLD:
                        limit = ONE_YEAR

                        if utxo['height'] >= ONE_MONTH_CAP_HARDFORK:
                            limit = ONE_MONTH
                        reward_period = min(coinage, limit) - 59
                        utxo_rewards = math.floor(utxo['satoshis']/DEVISOR)*reward_period

                        if utxo_rewards < 0:
                            logger.info("Rewards should never be negative!")

                        rewards_info["results"]["utxo_list"].append(utxo["txid"])
                        rewards_info["results"]["utxos"].append({
                            "locktime":locktime,
                            "txid":utxo["txid"],
                            "utxo_value": utxo_amount,
                            "utxo_age":utxo_age,
                            "sat_rewards":utxo_rewards,
                            "kmd_rewards":utxo_rewards/100000000,
                            "satoshis":utxo["satoshis"],
                            "block_height":utxo["height"]
                        })

                        total_rewards += utxo_rewards/100000000
                        eligible_utxo_count += 1

                    else:
                        if locktime == 0:
                            utxo_age = "Locktime not set"
                        if coinage < ONE_HOUR:
                            utxo_age = "Less than one hour since tx"
                        if utxo_amount < 10:
                            utxo_age = "UTXO too small (<10 KMD)"

                        rewards_info["results"]["utxo_list"].append(utxo["txid"])
                        rewards_info["results"]["utxos"].append({
                            "locktime":locktime,
                            "txid":utxo["txid"],
                            "utxo_value": utxo_amount,
                            "utxo_age":utxo_age,
                            "sat_rewards":0,
                            "kmd_rewards":0,
                            "satoshis":utxo["satoshis"],
                            "block_height":utxo["height"]
                        })
            else:
                utxo_age = "Transaction in mempool"

                rewards_info["results"]["utxo_list"].append(utxo["txid"])
                rewards_info["results"]["utxos"].update({
                    "txid":utxo["txid"],
                    "locktime":0,
                    "utxo_value": utxo_amount,
                    "utxo_age":utxo_age,
                    "sat_rewards":0,
                    "kmd_rewards":0,
                    "satoshis":utxo["satoshis"],
                    "block_height": "in mempool"
                })

    rewards_info["results"].update({
        "address": address,
        "utxo_count": utxo_count,
        "eligible_utxo_count": eligible_utxo_count,
        "oldest_utxo_block": oldest_utxo_block,
        "kmd_balance": balance,
        "total_rewards": total_rewards
    })
    rewards_info.update({    
        "count": utxo_count
    })

    return rewards_info


def get_address_from_pubkey(request):
    coin = helper.get_or_none(request, "coin")
    pubkey = helper.get_or_none(request, "pubkey")
    if not pubkey:
        return {
            "error": "You need to specify a pubkey, e.g '?pubkey=03b7621b44118017a16043f19b30cc8a4cfe068ac4e42417bae16ba460c80f3828' (if coin not specified, it will default to KMD)"
        }
    if not b58.validate_pubkey(pubkey):
        return {
            "error": f"Invalid pubkey: {pubkey}"
        }

    address_rows = []
    base_58_coins = info.get_base_58_coin_params(request)

    if coin:
        if coin not in base_58_coins: 
            return {
                "error": f"{coin} does not have locally defined Base 58 Params.",
                "supported_coins": list(base_58_params.keys())
            }
        else:
            address_row = b58.calc_addr_tool(pubkey,
                                         base_58_coins[coin]["pubtype"],
                                         base_58_coins[coin]["p2shtype"],
                                         base_58_coins[coin]["wiftype"])
            address_row.update({"coin":coin})
            address_rows.append(address_row)
    else:
        
        for coin in base_58_coins:
            pubtype = base_58_coins[coin]["pubtype"]
            p2shtype = base_58_coins[coin]["p2shtype"]
            wiftype = base_58_coins[coin]["wiftype"]
            address_row = b58.calc_addr_tool(pubkey, pubtype, p2shtype, wiftype)
            address_row.update({"coin":coin})
            address_rows.append(address_row)

    return {
        "pubkey": pubkey,
        "results": address_rows,
        "count": len(address_rows)
    }

def get_send_raw_tx(request):
    coin = helper.get_or_none(request, "coin")
    raw_tx = helper.get_or_none(request, "raw_tx")

    if not coin or not raw_tx:
        return {
            "error":f"Missing params! must specify 'coin' and 'raw_tx' like ?coin=KMD&raw_tx=0400008085202f89010000000000000000000000000000000000000000000000000000000000000000ffffffff0603e3be150101ffffffff016830e2110000000023210360b4805d885ff596f94312eed3e4e17cb56aa8077c6dd78d905f8de89da9499fac3d241b5d000000000000000000000000000000"
        }

    url, port, ssl = electrum.get_coin_electrum(coin)

    if not url:
        return { "error":f"No electrums found for {coin}" }

    return electrum.broadcast_raw_tx(url, port, raw_tx, ssl)
