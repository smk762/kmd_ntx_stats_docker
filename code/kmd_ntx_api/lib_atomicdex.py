import copy
import json
import time
import requests
from datetime import datetime as dt
from django.db.models import Count
from kmd_ntx_api.lib_const import *
from kmd_ntx_api.lib_const_mm2 import *

import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_struct as struct
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.serializers as serializers

# https://stats-api.atomicdex.io/


#### Standard RPCs # TODO: Confirm TOKEL is handled

def mm2_proxy(params):
    try:
        params.update({"userpass": MM2_USERPASS})
        r = requests.post(MM2_IP, json.dumps(params))
        return r
    except Exception as e:
        return e


def get_orderbook(request):
    params = {
        "method": "orderbook",
        "base": helper.get_or_none(request, "base", "KMD"),
        "rel": helper.get_or_none(request, "rel", "BTC")
    }
    r = mm2_proxy(params)
    return r.json()


def get_bestorders(request):
    params = {
        "method": "best_orders",
        "coin": helper.get_or_none(request, "coin", "KMD"),
        "action": helper.get_or_none(request, "action", "buy"),
        "volume": helper.get_or_none(request, "volume", 100),
    }
    r = mm2_proxy(params)
    return r.json()


def send_raw_tx(request):
    params = {
        "method": "send_raw_transaction",
        "coin": helper.get_or_none(request, "coin", "KMD"),
        "tx_hex": helper.get_or_none(request, "tx_hex", "")
    }
    r = mm2_proxy(params)
    return r.json()


#### SWAPS

def get_last_200_swaps(request):
    data = query.get_swaps_data()
    taker_coin = helper.get_or_none(request, "taker_coin")
    maker_coin = helper.get_or_none(request, "maker_coin")
    data = query.filter_swaps_coins(data, taker_coin, maker_coin)
    data = data.order_by('-time_stamp')[:200]
    data = data.values()
    serializer = serializers.swapsSerializer(data, many=True)
    return serializer.data


def get_failed_swap_by_uuid(request):
    if 'uuid' in request.GET:
        data = query.get_swaps_failed_data(request.GET['uuid']).values()
        serializer = serializers.swapsFailedSerializer(data, many=True)
        data = serializer.data     
    else:
        data = {}
    return data


def get_last_200_failed_swaps(request):
    data = query.get_swaps_failed_data().order_by('-time_stamp')[:200]
    data = data.values()
    serializer = serializers.swapsFailedSerializerPub(data, many=True)
    return serializer.data


def format_gui_os_version(swaps_data):
    for item in swaps_data:

        maker_gui = item["maker_gui"]
        taker_gui = item["taker_gui"]
        if maker_gui is None:
            maker_gui = "Unknown"
        if taker_gui is None:
            taker_gui = "Unknown"
        if taker_gui.find(";") > -1:
            taker_gui = taker_gui.split(';')[0]
        if maker_gui.find(";") > -1:
            maker_gui = maker_gui.split(';')[0]

        maker_gui_version = None
        taker_gui_version = None
        maker_gui_parts = maker_gui.split(" ")
        for part in maker_gui_parts:
            if len(part) == 9:
                maker_gui_version = part
        taker_gui_parts = taker_gui.split(" ")
        for part in taker_gui_parts:
            if part.find("0.") > -1:
                taker_gui_version = part
        if maker_gui_version is None:
            maker_gui_version = "Unknown"
        if taker_gui_version is None:
            taker_gui_version = "Unknown"

        maker_version = item["maker_version"]
        taker_version = item["taker_version"]
        if maker_version is None:
            maker_version = "None"
        if taker_version is None:
            taker_version = "None"

        maker = f"{maker_gui.lower()} {maker_version.lower()}"
        taker = f"{taker_gui.lower()} {taker_version.lower()}"
        for gui in ["AtomicDEX", "DogeDEX", "SmartDEX", 
                    "GleecDEX", "Dexstats", "mpm",
                    "pytomicDEX", "BitcoinZ Dex", "Shibadex"]:
            if gui.lower() in maker:
                maker_gui = gui
            if gui.lower() in taker:
                taker_gui = gui

        maker_os = None
        taker_os = None
        for os in ["iOS", "Android", "Windows", "Linux", "Darwin"]:
            if os.lower() in maker:
                maker_os = os
            if os.lower() in taker:
                taker_os = os
        if maker_os is None:
            maker_os = "Unknown"
        if taker_os is None:
            taker_os = "Unknown"


        maker_mm2_version = None
        taker_mm2_version = None
        maker_version_parts = maker_version.split("_")
        for part in maker_version_parts:
            if len(part) == 9:
                if helper.is_hex(part):
                    maker_mm2_version = part
        taker_version_parts = taker_version.split("_")
        for part in taker_version_parts:
            if len(part) == 9:
                if helper.is_hex(part):
                    taker_mm2_version = part
        if maker_mm2_version is None:
            maker_mm2_version = "Unknown"
        if taker_mm2_version is None:
            taker_mm2_version = "Unknown"

        maker = f"{maker_gui} {maker_os} {maker_gui_version} {maker_mm2_version}"
        taker = f"{taker_gui} {taker_os} {taker_gui_version} {taker_mm2_version}"

        item.update({
            "taker_gui": taker,
            "maker_gui": maker,
        })
    return swaps_data


def get_swaps_gui_stats(request):
    now = int(time.time())
    '''
    if "since" in request.GET:
        if request.GET["since"] in SINCE_INTERVALS:
            from_time = to_time - SINCE_INTERVALS[request.GET["since"]]
    '''
    to_time = helper.get_or_none(request, "to_time", now)
    from_time = helper.get_or_none(
        request,
        "from_time",
        now - SINCE_INTERVALS["week"]
    )
    data = query.get_swaps_data()
    data = query.filter_swaps_timespan(data, from_time, to_time)
    taker_pubkeys = data.values('taker_pubkey','taker_gui')\
                        .annotate(num_swaps=Count('taker_pubkey'))
    maker_pubkeys = data.values('maker_pubkey', 'maker_gui')\
                        .annotate(num_swaps=Count('maker_pubkey'))

    resp = struct.default_swap_totals()
    for item in taker_pubkeys:
        category = "other"
        taker_gui = item["taker_gui"]

        for x in list(resp["taker"].keys()):
            if taker_gui is not None:
                if taker_gui.lower().find(x) > -1:
                    category = x

        taker_cat = resp["taker"][category]
        if taker_gui not in taker_cat:
            taker_cat.update({
                taker_gui: {"swap_total": 0,"pubkey_total": 0}
            })

        taker_cat[taker_gui].update({
            item['taker_pubkey']:item['num_swaps'],
        })

        taker_cat[taker_gui]["pubkey_total"] += 1
        taker_cat[taker_gui]["swap_total"] += item['num_swaps']
        taker_cat["pubkey_total"] += 1
        taker_cat["swap_total"] += item['num_swaps']
        resp["taker"]["swap_total"] += item['num_swaps']

    resp["taker"]["pubkey_total"] = len(taker_pubkeys)

    for category in resp["taker"]:
        if category not in ["swap_total", "swap_pct", "pubkey_total"]:
            pct = taker_cat["swap_total"]/resp["taker"]["swap_total"]*100
            taker_cat.update({"swap_pct": pct})

            for gui in taker_cat:
                if gui not in ["swap_total", "swap_pct", "pubkey_total"]:
                    gui_total = taker_cat[gui]["swap_total"]
                    pct = gui_total/resp["taker"]["swap_total"]*100
                    cat_pct = gui_total/taker_cat["swap_total"]*100

                    taker_cat[gui].update({
                        "swap_pct": pct,
                        "swap_category_pct": cat_pct,
                    })


    for item in maker_pubkeys:
        category = "other"
        maker_gui = item["maker_gui"]

        for x in list(resp["maker"].keys()):
            if maker_gui is not None:
                if maker_gui.lower().find(x) > -1:
                    category = x

        maker_cat = resp["maker"][category]
        if maker_gui not in maker_cat:
            maker_cat.update({
                maker_gui:{"swap_total": 0,"pubkey_total": 0}
            })

        maker_cat[maker_gui].update({
            item['maker_pubkey']:item['num_swaps'],
        })

        maker_cat[maker_gui]["pubkey_total"] += 1
        maker_cat[maker_gui]["swap_total"] += item['num_swaps']
        maker_cat["pubkey_total"] += 1
        maker_cat["swap_total"] += item['num_swaps']
        resp["maker"]["swap_total"] += item['num_swaps']

    resp["maker"]["pubkey_total"] = len(maker_pubkeys)

    for category in resp["maker"]:
        if category  not in ["swap_total", "swap_pct", "pubkey_total"]:
            pct = maker_cat["swap_total"]/resp["maker"]["swap_total"]*100
            maker_cat.update({"swap_pct": pct})

            for gui in maker_cat:
                if gui not in ["swap_total", "swap_pct", "pubkey_total"]: 
                    gui_total = maker_cat[gui]["swap_total"]
                    pct = gui_total/resp["maker"]["swap_total"]*100
                    category_pct = gui_total/maker_cat["swap_total"]*100

                    maker_cat[gui].update({
                        "swap_pct": pct,
                        "swap_category_pct": category_pct,
                    })
    return resp


def get_swaps_pubkey_stats(request):
    now = int(time.time())
    to_time = helper.get_or_none(request, "to_time", now)
    from_time = helper.get_or_none(
        request,
        "from_time",
        now - SINCE_INTERVALS["week"]
    )

    if "since" in request.GET:
        if request.GET["since"] in SINCE_INTERVALS:
            from_time = to_time - SINCE_INTERVALS[request.GET["since"]]

    data = query.get_swaps_data()
    data = query.filter_swaps_timespan(data, from_time, to_time)
    taker_pubkeys = data.values('taker_pubkey', 'taker_gui')\
                        .annotate(num_swaps=Count('taker_pubkey'))
    maker_pubkeys = data.values('maker_pubkey', 'maker_gui')\
                        .annotate(num_swaps=Count('maker_pubkey'))

    resp = {}
    for item in taker_pubkeys:
        if item["taker_pubkey"] not in resp:
            resp.update({item["taker_pubkey"]:{"TOTAL": 0}})

        resp[item["taker_pubkey"]].update({
            item['taker_gui']:item['num_swaps'],
        })

        resp[item["taker_pubkey"]]["TOTAL"] += item['num_swaps']
    return resp


#### ACTIVATION 

def get_contracts(platform):
    if is_testnet(platform):
        contract = SWAP_CONTRACTS[platform]["testnet"]["swap_contract"]
        fallback = SWAP_CONTRACTS[platform]["testnet"]["fallback_contract"]
    else:
        contract = SWAP_CONTRACTS[platform]["mainnet"]["swap_contract"]
        fallback = SWAP_CONTRACTS[platform]["mainnet"]["fallback_contract"]

    return {
        "swap_contract_address":contract,
        "fallback_swap_contract":fallback
    }


def is_testnet(coin):
    if coin in TESTNET_COINS:
        return True
    return False


def get_activation_commands(request):
    protocols = []
    platforms = []
    other_platforms = []
    incompatible_coins = []
    coins_without_electrum = []
    enable_commands = {"commands":{}}
    invalid_configs = {}
    resp_json = {}

    selected_coin = helper.get_or_none(request, "coin")
    coin_info = query.get_coins_data(selected_coin, 1)
    serializer = serializers.coinsSerializer(coin_info, many=True)

    for item in serializer.data:
        protocol = None
        platform = None
        coin = item["coin"]
        electrums = item["electrums"]
        compatible = item["mm2_compatible"] == 1
        
        if coin == "TOKEL":
            coin = "TKL"

        resp_json = {} 
        if "protocol" in item["coins_info"]:
            protocol = item["coins_info"]["protocol"]["type"]
            protocols.append(protocol)

            if "protocol_data" in item["coins_info"]["protocol"]:
                if "platform" in item["coins_info"]["protocol"]["protocol_data"]:
                    platform = item["coins_info"]["protocol"]["protocol_data"]["platform"]
                    platforms.append(platform)

                    if platform not in enable_commands["commands"]:
                        enable_commands["commands"].update({platform: {}})

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
                    "userpass":"'$userpass'",
                    "method":"electrum",
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
                resp_json.update(PLATFORM_URLS["BNB"])

            elif platform == 'ETHR' or coin == 'ETHR':
                platform = 'ETHR'
                resp_json.update(PLATFORM_URLS["ETHR"])

            elif platform == 'ETH' or coin == 'ETH':
                platform = 'ETH'
                resp_json.update(PLATFORM_URLS["ETH"])

            elif platform == 'ETH-ARB20' or coin == 'ETH-ARB20':
                platform = 'ETH-ARB20'
                resp_json.update(PLATFORM_URLS["ETH-ARB20"])

            elif platform == 'ONE' or coin == 'ONE':
                platform = 'ONE'
                resp_json.update(PLATFORM_URLS["ONE"])

            elif platform == 'MATIC' or coin == 'MATIC':
                platform = 'MATIC'
                resp_json.update(PLATFORM_URLS["MATIC"])

            elif platform == 'MATICTEST' or coin == 'MATICTEST':
                platform = 'MATICTEST'
                resp_json.update(PLATFORM_URLS["MATICTEST"])

            elif platform == 'AVAX' or coin == 'AVAX':
                platform = 'AVAX'
                resp_json.update(PLATFORM_URLS["AVAX"])

            elif platform == 'AVAXT' or coin == 'AVAXT':
                platform = 'AVAXT'
                resp_json.update(PLATFORM_URLS["AVAXT"])

            elif platform == 'BNBT' or coin == 'BNBT':
                platform = 'BNBT'
                resp_json.update(PLATFORM_URLS["BNBT"])

            elif platform == 'MOVR' or coin == 'MOVR':
                platform = 'MOVR'
                resp_json.update(PLATFORM_URLS["MOVR"])
                
            elif platform == 'FTM' or coin == 'FTM':
                platform = 'FTM'
                resp_json.update(PLATFORM_URLS["FTM"])

            elif platform == 'FTMT' or coin == 'FTMT':
                platform = 'FTMT'
                resp_json.update(PLATFORM_URLS["FTMT"])

            elif platform == 'KCS' or coin == 'KCS':
                platform = 'KCS'
                resp_json.update(PLATFORM_URLS["KCS"])

            elif platform == 'HT' or coin == 'HT':
                platform = 'HT'
                resp_json.update(PLATFORM_URLS["HT"])

            elif coin == 'UBQ':
                platform = 'Ubiq'
                resp_json.update(PLATFORM_URLS["UBQ"])

            elif platform == 'ETC' or coin == 'ETC':
                platform = 'ETC'
                resp_json.update(PLATFORM_URLS["ETC"])

            elif platform == 'OPT20' or coin == 'ETHK-OPT20':
                platform = 'OPT20'
                resp_json.update(PLATFORM_URLS["OPT20"])

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
                        coin: helper.sort_dict(resp_json)
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
                        coin: helper.sort_dict(resp_json)
                    })
        else:
            incompatible_coins.append(coin)

    if selected_coin is None:
        enable_commands.update({
            "invalid_configs": invalid_configs,
            "incompatible_coins": incompatible_coins,
            "protocols": list(set(protocols)),
            "platforms": list(set(platforms)),
            "other_platforms": list(set(other_platforms)),
            "coins_without_electrum": coins_without_electrum
            })
        return enable_commands
    else: 
        return resp_json


#### SEEDNODES 

def get_active_mm2_versions(ts):
    data = requests.get(VERSION_TIMESPANS_URL).json()
    active_versions = []
    for version in data:
        if int(ts) > data[version]["start"] and int(ts) < data[version]["end"]:
            active_versions.append(version)
    return active_versions


def is_mm2_version_valid(version, timestamp):
    active_versions = get_active_mm2_versions(timestamp)
    if version in active_versions:
        return True
    return False


def get_seednode_version_date_table(request):
    season =  helper.get_or_none(request, "season", SEASON)
    notary_list = helper.get_notary_list(season)
    default_scores = helper.prepopulate_seednode_version_date(notary_list)

    hour_headers = list(default_scores.keys())
    hour_headers.sort()

    table_headers = ["Notary"] + hour_headers + ["Total"]

    start = int(helper.get_or_none(request, "start", time.time() - SINCE_INTERVALS["day"]))
    end = int(helper.get_or_none(request, "end", time.time()))

    date_hour_notary_scores = query.get_seednode_version_stats_data(start, end)

    scores = date_hour_notary_scores.values()
    for item in scores:
        notary = item["name"]
        if notary in notary_list:
            score = item["score"]
            _, hour = helper.date_hour(item["timestamp"]).split(" ")
            hour = hour.replace(":00", "")
            default_scores[hour][notary]["score"] = score
            if item["version"] not in default_scores[hour][notary]["versions"]:
                default_scores[hour][notary]["versions"].append(item["version"])

    table_data = []
    for notary in notary_list:
        notary_row = {"Notary": notary}
        total = 0
        for hour in hour_headers:
            total += default_scores[hour][notary]["score"]
            notary_row.update({
                hour: default_scores[hour][notary]["score"]
            })
        notary_row.update({
            "Total": round(total,1)
        })
        table_data.append(notary_row)

    return {
        "start": start,
        "date": dt.utcfromtimestamp(end).strftime('%a %-d %B %Y'),
        "end": end,
        "headers": table_headers,
        "table_data": table_data,
        "scores": default_scores
    }

    # TODO: Views for day (by hour), month (by day), season (by month)
    # Season view: click on month, goes to month view
    # Month view: click on day, goes to day view
    # TODO: Incorporate these scores into overall NN score, and profile stats.


def get_seednode_version_month_table(request):
    season =  helper.get_or_none(request, "season", SEASON)
    year = helper.get_or_none(request, "year", None)
    month = helper.get_or_none(request, "month", None)
    start, end, last_day = helper.get_month_epoch_range(year, month)

    notary_list = helper.get_notary_list(season)
    default_scores = helper.prepopulate_seednode_version_month(notary_list)

    day_headers = list(default_scores.keys())
    print(day_headers)
    day_headers.sort()

    table_headers = ["Notary"] + day_headers + ["Total"]
    data = query.get_seednode_version_stats_data(start, end).values()

    for item in data:
        notary = item["name"]
        if notary in notary_list:
            score = item["score"]
            date, _ = helper.date_hour(item["timestamp"]).split(" ")
            day = date.split("/")[1]
            print(day)
            default_scores[day][notary]["score"] += score
            if item["version"] not in default_scores[day][notary]["versions"]:
                default_scores[day][notary]["versions"].append(item["version"])

    table_data = []
    for notary in notary_list:
        notary_row = {"Notary": notary}
        total = 0
        for day in day_headers:
            total += default_scores[day][notary]["score"]
            notary_row.update({
                day: round(default_scores[day][notary]["score"],1)
            })
        notary_row.update({
            "Total": round(total,1)
        })
        table_data.append(notary_row)

    return {
        "date_ts": dt.utcfromtimestamp(end).strftime('%m-%Y'),
        "date": dt.utcfromtimestamp(end).strftime('%b %Y'),
        "headers": table_headers,
        "table_data": table_data,
        "scores": default_scores
    }