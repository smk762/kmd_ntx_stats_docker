#!/usr/bin/env python3
import json
from eth_keys import keys
from kmd_ntx_api.const import SMARTCHAINS
from kmd_ntx_api.info import get_base_58_coin_params
from kmd_ntx_api.based_58 import calc_addr_tool, convert_addresses, decode_opret, \
    calc_addr_from_pubkey, validate_pubkey, pubkey_to_p2pk, pubkey_to_p2pkh, \
    address_to_p2pkh, get_p2pkh_scripthash_from_address
from kmd_ntx_api.electrum import get_coin_electrum, get_p2pk_scripthash_from_pubkey, \
    get_p2pkh_scripthash_from_pubkey, get_from_electrum_ssl, get_from_electrum
from kmd_ntx_api.explorers import get_sync, get_dexstats_utxos
from kmd_ntx_api.serializers import addrFromBase58Serializer
from kmd_ntx_api.helper import get_or_none
from kmd_ntx_api.logger import logger

def get_addr_from_base58(request):
    for x in addrFromBase58Serializer.Meta.fields:
        if x not in request.GET:
            example_params = "?pubkey=03b7621b44118017a16043f19b30cc8a4cfe068ac4e42417bae16ba460c80f3828&pubtype=60&wiftype=188&p2shtype=85"
            error = f"You need to specify params like '{example_params}'"
            return {
                "error":f"{error}",
                "note":f"Parameter values for some coins available at /api/info/base_58/"
            }

    return calc_addr_tool(request.GET["pubkey"], request.GET["pubtype"],
                              request.GET["p2shtype"], request.GET["wiftype"])

def get_address_conversion(request):
    address = get_or_none(request, "address")
    if not address:
        return {"error": "You need to specify an address, like ?address=17VZNX1SN5NtKa8UQFxwQbFeFc3iqRYhem"}
    return convert_addresses(address)


def get_decode_op_return(request):
    op_return = get_or_none(request, "OP_RETURN")
    if not op_return:
        return {"error": "You need to include an OP_RETURN, e.g. '?OP_RETURN=fcfc5360a088f031c753b6b63fd76cec9d3e5f5d11d5d0702806b54800000000586123004b4d4400'"}
    else:
        try:
            resp = decode_opret(op_return)
        except Exception as e:
            resp = {"error": e}
    return resp


def get_pubkey_utxos(request):
    pubkey = get_or_none(request, "pubkey")
    coin = get_or_none(request, "coin")

    if not coin or not pubkey:
        return {"error": f"You need to specify all filter params"}

    resp = get_utxos(coin, pubkey)

    min_height = 999999999
    if not "utxos" in resp:
        return resp
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


def get_utxos(coin, pubkey):
    if coin in SMARTCHAINS:
        address = calc_addr_from_pubkey(coin, pubkey)
        block_tip = get_sync(coin)["height"]
        resp = get_dexstats_utxos(coin, address)
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
        url, port, ssl = get_coin_electrum(coin)

        if url:
            utxos = []
            utxo_count = 0
            dpow_utxo_count = 0
            p2pk_scripthash = get_p2pk_scripthash_from_pubkey(pubkey)
            p2pkh_scripthash = get_p2pkh_scripthash_from_pubkey(pubkey)

            if ssl:
                headers_resp = get_from_electrum_ssl(
                    url, port, 'blockchain.headers.subscribe')

                p2pk_resp = get_from_electrum_ssl(
                    url, port, 'blockchain.scripthash.listunspent',
                    p2pk_scripthash)

                p2pkh_resp = get_from_electrum_ssl(
                    url, port, 'blockchain.scripthash.listunspent',
                    p2pkh_scripthash)

                block_tip = headers_resp['result']['height']
                resp = p2pk_resp['result'] + p2pkh_resp['result']

            else:
                headers_resp = get_from_electrum(
                    url, port, 'blockchain.headers.subscribe')

                p2pk_resp = get_from_electrum(
                    url, port, 'blockchain.scripthash.listunspent',
                    p2pk_scripthash)

                p2pkh_resp = get_from_electrum(
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
    address = get_or_none(request, "address")
    if address:
        try:
            scripthash = get_p2pkh_scripthash_from_address(address)
            p2pkh = address_to_p2pkh(address)
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


def get_explorer_status():
    return json.load(open("cache/explorer_status.json", "r"))


def get_scripthashes_from_pubkey(request):
    pubkey = get_or_none(request, "pubkey")
    if pubkey:
        try:
            p2pkh_scripthash = get_p2pkh_scripthash_from_pubkey(pubkey)
            p2pk_scripthash = get_p2pk_scripthash_from_pubkey(pubkey)
            p2pkh = pubkey_to_p2pkh(pubkey)
            p2pk = pubkey_to_p2pk(pubkey)

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


def get_evm_address_from_pubkey(compressed_pubkey):
    try:
        if compressed_pubkey.startswith("0x"):
            compressed_pubkey = compressed_pubkey[2:]
        compressed_pubkey_bytes = bytes.fromhex(compressed_pubkey)
        uncompressed_pubkey = str(keys.PublicKey.from_compressed_bytes(compressed_pubkey_bytes))[2:]
        uncompressed_pubkey_bytes = bytes.fromhex(uncompressed_pubkey)
        address = (keys.PublicKey(uncompressed_pubkey_bytes).to_checksum_address())
        logger.info(address)
    except Exception as e:
        logger.error(f"get_evm_address_from_pubkey: {e}")
        address = "N/A"
    return address


def get_address_from_pubkey(request):
    coin = get_or_none(request, "coin")
    pubkey = get_or_none(request, "pubkey")
    if not pubkey:
        return {
            "error": "You need to specify a pubkey, e.g '?pubkey=03b7621b44118017a16043f19b30cc8a4cfe068ac4e42417bae16ba460c80f3828' (if coin not specified, it will default to KMD)"
        }
    if not validate_pubkey(pubkey):
        return {
            "error": f"Invalid pubkey: {pubkey}"
        }

    address_rows = []
    base_58_coins = get_base_58_coin_params(request)

    if coin:
        if coin not in base_58_coins:
            if not is_evm(coin):
                return {
                    "error": f"{coin} does not have locally defined Base 58 Params.",
                    "supported_coins": list(base_58_coins.keys())
                }
            else:
                logger.info(f"get_address_from_pubkey: {coin} is an EVM coin, using eth_keys to generate address")
                address_row = {
                    "pubkey": pubkey,
                    "pubtype": "N/A",
                    "p2shtype": "N/A",
                    "wiftype": "N/A",
                    "address": get_evm_address_from_pubkey(pubkey),
                    "coin": coin
                }
                address_rows.append(address_row)
                
        else:
            address_row = calc_addr_tool(pubkey,
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
            address_row = calc_addr_tool(pubkey, pubtype, p2shtype, wiftype)
            address_row.update({"coin":coin})
            address_rows.append(address_row)

    return {
        "pubkey": pubkey,
        "results": address_rows,
        "count": len(address_rows)
    }

def is_evm(coin):
    split_coin = coin.replace("_OLD", "").split("-")
    if len(split_coin) == 1:
        return False
    protocols = {
        "AVAX": "AVX20",
        "ETH": "ERC20",
        "BNB": "BEP20",
        "ETH-ARB20": "ARB20",
        "FTM": "FTM20",
        "HT": "HCO20",
        "KCS": "KRC20",
        "MATIC": "PLG20",
        "GLMR": "Moonbeam",
        "MOVR": "Moonriver",
        "ONE": "HRC20",
        "ETC": "Ethereum Classic",
        "RBTC": "RSK Smart Bitcoin",
        "SBCH": "SmartBCH",
        "UBQ": "Ubiq"
    }
    testnet_protocols = {
        "AVAXT": "AVX20",
        "BNBT": "BEP20",
        "FTMT": "FTM20",
        "MATICTEST": "PLG20"
    }
    if coin in protocols.keys() or coin in testnet_protocols.keys():
        return True
    if coin in protocols.values() or coin in testnet_protocols.values():
        return True
    return False
    