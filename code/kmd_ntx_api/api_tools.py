#!/usr/bin/env python3
import time
import math
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from rest_framework import permissions, viewsets, authentication
from kmd_ntx_api.serializers import *
from kmd_ntx_api.lib_info import get_all_coins
from kmd_ntx_api.lib_base58 import *
from kmd_ntx_api.lib_electrum import *
from kmd_ntx_api.lib_mm2 import *


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

def address_conversion_tool(request):
    if "address" in request.GET:
        address = request.GET["address"]
    else:
        return JsonResponse({"error": "You need to specify an address, like ?address=17VZNX1SN5NtKa8UQFxwQbFeFc3iqRYhem"})
    resp = convert_addresses(address)
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
                if "height" in item: # avoid unconfirmed
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
                        rewards_info['utxos'].update({
                            utxo['txid']:{
                                "locktime":locktime,
                                "utxo_value":utxo['amount'],
                                "utxo_age":utxo_age,
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

def scripthash_from_address_tool(request):
    if "address" in request.GET:
        if request.GET["address"] != "":
            try:
                address = request.GET["address"]
                scripthash = get_scripthash_from_address(address)
                p2pkh = address_to_p2pkh(address)
                return JsonResponse({
                    "address":f"{address}",
                    "p2pkh_scripthash":f"{scripthash}",
                    "p2pkh":f"{p2pkh}"
                })
            except Exception as e:
                return JsonResponse({
                    "error":f"{e}"
                })
    return JsonResponse({"error": "You need to specify an address, like ?address=17VZNX1SN5NtKa8UQFxwQbFeFc3iqRYhem"})


def scripthashes_from_pubkey_tool(request):
    if "pubkey" in request.GET:
        if request.GET["pubkey"] != "":
            try:
                pubkey = request.GET["pubkey"]
                p2pkh_scripthash = get_p2pkh_scripthash_from_pubkey(pubkey)
                p2pk_scripthash = get_p2pk_scripthash_from_pubkey(pubkey)
                p2pkh = pubkey_to_p2pkh(pubkey)
                p2pk = pubkey_to_p2pk(pubkey)
                return JsonResponse({
                    "pubkey":f"{pubkey}",
                    "p2pkh_scripthash":f"{p2pkh_scripthash}",
                    "p2pk_scripthash":f"{p2pk_scripthash}",
                    "p2pkh":f"{p2pkh}",
                    "p2pk":f"{p2pk}"
                })
            except Exception as e:
                return JsonResponse({
                    "error":f"{e}"
                })
    return JsonResponse({"error": "You need to specify a pubkey, like ?pubkey=<PUBKEY>"})


def send_raw_tx_tool(request):
    try:
        resp = send_raw_tx(request)
        return JsonResponse({resp})
    except Exception as e:
        return JsonResponse({
            "error":f"{e}"
        })

def is_testnet(coin):
    if coin in ["BNBT", "ETHR", "AVAXT", "tQTUM", "MATICTEST"]:
        return True
    return False


def get_contracts(platform):
    if is_testnet(platform):
        contract = SWAP_CONTRACTS[platform]["testnet"]["swap_contract"]
        fallback_contract = SWAP_CONTRACTS[platform]["testnet"]["fallback_contract"]
    else:
        contract = SWAP_CONTRACTS[platform]["mainnet"]["swap_contract"]
        fallback_contract = SWAP_CONTRACTS[platform]["mainnet"]["fallback_contract"]

    return {
        "swap_contract_address":contract,
        "fallback_swap_contract":fallback_contract,
    }

def get_enable_commands(request):
    coin_info = get_coins_data()
    serializer = coinsSerializer(coin_info, many=True)
    enable_commands = { "commands":{
     "UTXO":{},
     "QTUM":{},
     "ONE":{},
     "QRC20":{},
     "None":{}
     }}
    incompatible_coins = []
    protocols = []
    platforms = []
    other_platforms = []
    coins_without_electrum = []

    need_to_fix = [
        'ONE', 'HPY', 'ZAT', 'BOT', 'EPC', 'QC', 'NVC-QRC20',
        'QIAIR', 'QI', 'XVC-QRC20', 'INK', 'FENIX', 'SPC', 'AWR',
        'HLC', 'MED', 'LSTR', 'QBT', 'PLY', 'TSL', 'OC', 'ENT',
        'CFUN', 'PUT', 'WID', 'AVAX', 'AVAXT', 'ARRR', 'ETC', 'BNB',
        'ETH', 'ETH-ARB20', 'ETHK-OPT20', 'ETHR', 'FTM', 'BNBT', 'HT',
        'KCS', 'SBCH', 'MATICTEST', 'ETHR-ARB20', 'FTMT', 'MATIC', 'MOVR',
        'UBQ', 'tBCH', 'ZOMBIE', 'PAXG-PLG20', 'JST', 'THX',
        'USDT-SLP', 'USDF', 'sTST'
        ]
    
    ignore_coins = [
        "GLEEC-OLD",

    ]
    for item in serializer.data:
        coin = item["chain"]
        electrums = item["electrums"]
        compatible = item["mm2_compatible"] == 1
        protocol = None
        platform = None
        resp_json = {} 
        if "protocol" in item["coins_info"]:
            protocol = item["coins_info"]["protocol"]["type"]
            protocols.append(protocol)
            if "protocol_data" in item["coins_info"]["protocol"]:
                if "platform" in item["coins_info"]["protocol"]["protocol_data"]:
                    platform = item["coins_info"]["protocol"]["protocol_data"]["platform"]
                    platforms.append(platform)
                    if platform not in enable_commands["commands"]:
                        enable_commands["commands"].update({
                            platform: {}
                        })

        if platform in SWAP_CONTRACTS:
            resp_json.update(get_contracts(platform))
        elif coin in SWAP_CONTRACTS:
            resp_json.update(get_contracts(coin))
        else:
            other_platforms.append(platform)
            print(f"{platform} not in {SWAP_CONTRACTS}")


        if protocol == "UTXO":
            if len(electrums) > 0:
                resp_json.update({
                    "userpass":"'$userpass'"
                    ,"method":"electrum",
                    "coin":coin,
                    "servers": []
                })
                for electrum in electrums:
                    resp_json["servers"].append({"url":electrum})
                enable_commands["commands"]["UTXO"].update({
                    coin:resp_json
                })

        elif protocol == "QRC20" or coin == 'QTUM':

            resp_json.update({
                "userpass":"'$userpass'"
                ,"method":"electrum",
                "coin":coin,
                "servers": [
                    {"url":"electrum1.cipig.net:10050"},
                    {"url":"electrum2.cipig.net:10050"},
                    {"url":"electrum3.cipig.net:10050"}
                ]
            })
            enable_commands["commands"]["QTUM"].update({
                coin:resp_json
            })

        elif protocol == "tQTUM" or coin == 'tQTUM':
            resp_json.update({
                "userpass":"'$userpass'"
                ,"method":"electrum",
                "coin":coin,
                "servers": [
                    {"url":"electrum1.cipig.net:10050"},
                    {"url":"electrum2.cipig.net:10050"},
                    {"url":"electrum3.cipig.net:10050"}
                ]
            })

            enable_commands["commands"]["QRC20"].update({
                coin:resp_json
            })

        else:

            resp_json.update({
                "userpass":"'$userpass'",
                "method":"enable",
                "coin":coin,
            })


            if platform == 'BNB' or coin == 'BNB':
                resp_json.update({
                    "urls": [
                        "http://bsc1.cipig.net:8655",
                        "http://bsc2.cipig.net:8655",
                        "http://bsc3.cipig.net:8655"
                    ]
                })

            elif platform == 'ETHR' or coin == 'ETHR':
                resp_json.update({
                    "urls": [
                        "https://ropsten.infura.io/v3/1d059a9aca7d49a3a380c71068bffb1c",
                    ]
                })
            elif platform == 'ETH' or coin == 'ETH':
                resp_json.update({
                    "urls": [
                        "http://eth1.cipig.net:8555",
                        "http://eth2.cipig.net:8555",
                        "http://eth3.cipig.net:8555"
                    ],
                    "gas_station_url":"https://ethgasstation.info/json/ethgasAPI.json"
                })

            elif platform == 'ETH-ARB20' or coin == 'ETH-ARB20':
                resp_json.update({
                    "urls": [
                        "https://arb1.arbitrum.io/rpc"
                    ]
                })
            elif platform == 'ONE' or coin == 'ONE':
                resp_json.update({
                    "urls": [
                        "https://api.harmony.one",
                        "https://api.s0.t.hmny.io"
                    ]
                })
            elif platform == 'MATIC' or coin == 'MATIC':
                resp_json.update({
                    "urls": [
                        "https://polygon-rpc.com"
                    ]
                })
            elif platform == 'MATICTEST' or coin == 'MATICTEST':
                resp_json.update({
                    "urls": [
                        "https://polygon-rpc.com"
                    ]
                })
            elif platform == 'AVAX' or coin == 'AVAX':
                resp_json.update({
                    "urls": [
                        "https://api.avax.network/ext/bc/C/rpc"
                    ]
                })
            elif platform == 'AVAXT' or coin == 'AVAXT':
                resp_json.update({
                    "urls": [
                        "https://api.avax.network/ext/bc/C/rpc"
                    ]
                })
            elif platform == 'BNBT' or coin == 'BNBT':
                resp_json.update({
                    "urls": [
                        "https://data-seed-prebsc-1-s2.binance.org:8545"
                    ]
                })
            elif platform == 'MOVR' or coin == 'MOVR':
                resp_json.update({
                    "urls": [
                        "https://rpc.moonriver.moonbeam.network"
                    ]
                })
            elif platform == 'FTM' or coin == 'FTM':
                resp_json.update({
                    "urls": [
                        "https://rpc.ftm.tools/"
                    ]
                })
            elif platform == 'KCS' or coin == 'KCR':
                resp_json.update({
                    "urls": [
                        "https://rpc-mainnet.kcc.network"
                    ]
                })
            elif platform == 'HT' or coin == 'HCC':
                resp_json.update({
                    "urls": [
                        "https://http-mainnet.hecochain.com"
                    ]
                })

            elif platform == 'QTUM' or coin == 'QTUM':
                resp_json.update({
                    "urls": [
                        "electrum1.cipig.net:10050",
                        "electrum2.cipig.net:10050",
                        "electrum3.cipig.net:10050"
                    ]
                })

            if platform:
                enable_commands["commands"][platform].update({
                    coin:resp_json
                })
            else:
                enable_commands["commands"]["None"].update({
                    coin:resp_json
                })
            
    enable_commands.update({
        "incompatible_coins":incompatible_coins,
        "protocols":list(set(protocols)),
        "platforms":list(set(platforms)),
        "other_platforms":list(set(other_platforms)),
        "coins_without_electrum":coins_without_electrum
        })
    return JsonResponse(enable_commands)

