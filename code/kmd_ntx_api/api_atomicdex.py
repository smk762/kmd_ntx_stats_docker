#!/usr/bin/env python3
from django.http import JsonResponse
from kmd_ntx_api.lib_atomicdex import *


def orderbook_api(request):
    return JsonResponse(get_orderbook(request))


def seednode_version_stats_api(request):
    return JsonResponse(get_nn_mm2_stats(request), safe=False)


def seednode_version_stats_hourly_api(request):
    return JsonResponse(get_nn_mm2_stats_by_hour(request), safe=False)


def nn_seed_version_scores_table_api(request):
    return JsonResponse(get_nn_seed_version_scores_hourly_table(request), safe=False)

def bestorders_api(request):
    return JsonResponse(get_orderbook(request))


def bestorders_api(request):
    return JsonResponse(get_orderbook(request))


def failed_swap_api(request):
    return JsonResponse(get_failed_swap_by_uuid(request), safe=False)


def last_200_swaps_api(request):
    data = get_last_200_swaps(request)
    data = format_gui_os_version(data)
    return JsonResponse(data, safe=False)


def last_200_failed_swaps_api(request):
    data = get_last_200_failed_swaps(request)
    data = format_gui_os_version(data)
    return JsonResponse(data, safe=False)


def swaps_gui_stats_api(request):
    resp = get_swaps_gui_stats(request)
    return JsonResponse(resp)


def swaps_pubkey_stats_api(request):
    resp = get_swaps_pubkey_stats(request)
    return JsonResponse(resp)


def activation_commands_api(request):
    selected_coin = None
    if "coin" in request.GET:
        selected_coin = request.GET["coin"]

    coin_info = get_coins_data(selected_coin, 1)
    serializer = coinsSerializer(coin_info, many=True)
    enable_commands = { "commands":{
     }}
    incompatible_coins = []
    protocols = []
    platforms = []
    other_platforms = []
    coins_without_electrum = []
    invalid_configs = {}
    resp_json = {} 

    
    ignore_coins = [
        "GLEEC-OLD"
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

        if protocol == "UTXO":
            platform = 'UTXO'
            if len(electrums) > 0:
                resp_json.update({
                    "userpass":"'$userpass'"
                    ,"method":"electrum",
                    "coin":coin,
                    "servers": []
                })
                if "UTXO" not in enable_commands["commands"]:
                    enable_commands["commands"].update({
                        "UTXO": {}
                    })   
                for electrum in electrums:
                    resp_json["servers"].append({"url":electrum})

        elif protocol == "QRC20" or coin in ['QTUM', 'QTUM-segwit']:
            platform = 'QRC20'

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
            if "QTUM" not in enable_commands["commands"]:
                enable_commands["commands"].update({
                    "QTUM": {}
                })    


        elif protocol == "tQTUM" or coin in ['tQTUM', 'tQTUM-segwit']:
            platform = 'tQTUM'
            resp_json.update({
                "userpass":"'$userpass'",
                "method":"electrum",
                "coin":coin,
                "servers": [
                    {"url":"electrum1.cipig.net:10071"},
                    {"url":"electrum2.cipig.net:10071"},
                    {"url":"electrum3.cipig.net:10071"}
                ]
            })
            if "QRC20" not in enable_commands["commands"]:
                enable_commands["commands"].update({
                    "QRC20": {}
                })    

        else:

            resp_json.update({
                "userpass":"'$userpass'",
                "method":"enable",
                "coin":coin,
            })


            if platform == 'BNB' or coin == 'BNB':
                platform = 'BNB'
                resp_json.update({
                    "urls": [
                        "http://bsc1.cipig.net:8655",
                        "http://bsc2.cipig.net:8655",
                        "http://bsc3.cipig.net:8655"
                    ]
                })

            elif platform == 'ETHR' or coin == 'ETHR':
                platform = 'ETHR'
                resp_json.update({
                    "urls": [
                        "https://ropsten.infura.io/v3/1d059a9aca7d49a3a380c71068bffb1c",
                    ]
                })
            elif platform == 'ETH' or coin == 'ETH':
                platform = 'ETH'
                resp_json.update({
                    "urls": [
                        "http://eth1.cipig.net:8555",
                        "http://eth2.cipig.net:8555",
                        "http://eth3.cipig.net:8555"
                    ],
                    "gas_station_url":"https://ethgasstation.info/json/ethgasAPI.json"
                })

            elif platform == 'ETH-ARB20' or coin == 'ETH-ARB20':
                platform = 'ETH-ARB20'
                resp_json.update({
                    "urls": [
                        "https://rinkeby.arbitrum.io/rpc"
                    ]
                })
            elif platform == 'ONE' or coin == 'ONE':
                platform = 'ONE'
                resp_json.update({
                    "urls": [
                        "https://api.harmony.one",
                        "https://api.s0.t.hmny.io"
                    ]
                })
            elif platform == 'MATIC' or coin == 'MATIC':
                platform = 'MATIC'
                resp_json.update({
                    "urls": [
                        "https://polygon-rpc.com"
                    ]
                })
            elif platform == 'MATICTEST' or coin == 'MATICTEST':
                platform = 'MATICTEST'
                resp_json.update({
                    "urls": [
                        "https://polygon-rpc.com"
                    ]
                })
            elif platform == 'AVAX' or coin == 'AVAX':
                platform = 'AVAX'
                resp_json.update({
                    "urls": [
                        "https://api.avax.network/ext/bc/C/rpc"
                    ]
                })
            elif platform == 'AVAXT' or coin == 'AVAXT':
                platform = 'AVAXT'
                resp_json.update({
                    "urls": [
                        "https://api.avax.network/ext/bc/C/rpc"
                    ]
                })
            elif platform == 'BNBT' or coin == 'BNBT':
                platform = 'BNBT'
                resp_json.update({
                    "urls": [
                        "https://data-seed-prebsc-1-s2.binance.org:8545"
                    ]
                })
            elif platform == 'MOVR' or coin == 'MOVR':
                platform = 'MOVR'
                resp_json.update({
                    "urls": [
                        "https://rpc.moonriver.moonbeam.network"
                    ]
                })
                
            elif platform == 'FTM' or coin == 'FTM':
                platform = 'FTM'
                resp_json.update({
                    "urls": [
                        "https://rpc.ftm.tools/"
                    ]
                })
            elif platform == 'FTMT' or coin == 'FTMT':
                platform = 'FTMT'
                resp_json.update({
                    "urls": [
                        "https://rpc.testnet.fantom.network/"
                    ]
                })

            elif platform == 'KCS' or coin == 'KCS':
                platform = 'KCS'
                resp_json.update({
                    "urls": [
                        "https://rpc-mainnet.kcc.network"
                    ]
                })
            elif platform == 'HT' or coin == 'HT':
                platform = 'HT'
                resp_json.update({
                    "urls": [
                        "https://http-mainnet.hecochain.com"
                    ]
                })
            elif platform == 'ETC' or coin == 'UBQ':
                platform = 'ETC'
                resp_json.update({
                    "urls": [
                        "https://rpc.octano.dev/"
                    ]
                })
            elif platform == 'ETC' or coin == 'ETC':
                platform = 'ETC'
                resp_json.update({
                    "urls": [
                        "https://www.ethercluster.com/etc"
                    ]
                })
            elif platform == 'OPT20' or coin == 'ETHK-OPT20':
                platform = 'OPT20'
                resp_json.update({
                    "urls": [
                        "https://kovan.optimism.io"
                    ]
                })
        if compatible and len(resp_json) > 0:
            is_valid_enable = (resp_json['method'] == 'enable' and 'urls' in resp_json)
            is_valid_electrum = (resp_json['method'] == 'electrum' and 'servers' in resp_json)
            if is_valid_enable or is_valid_electrum:
                if platform:
                    if platform not in enable_commands["commands"]:
                        enable_commands["commands"].update({
                            platform: {}
                        })    
                    enable_commands["commands"][platform].update({
                        coin:sort_dict(resp_json)
                    })
                else:
                    print(f"Unknown platform for {coin}")
                    '''
                    if "Unknown" not in enable_commands["commands"]:
                        enable_commands["commands"].update({
                            "Unknown": {}
                        })    
                    enable_commands["commands"]["Unknown"].update({
                        coin:sort_dict(resp_json)
                    })
                    '''
            else:
                invalid_configs.update({
                        coin:sort_dict(resp_json)
                    })
        else:
            incompatible_coins.append(coin)

    if selected_coin is None:
        enable_commands.update({
            "invalid_configs":invalid_configs,
            "incompatible_coins":incompatible_coins,
            "protocols":list(set(protocols)),
            "platforms":list(set(platforms)),
            "other_platforms":list(set(other_platforms)),
            "coins_without_electrum":coins_without_electrum
            })
        return JsonResponse(enable_commands)
    else: 
        return JsonResponse(resp_json)

