import copy
import json
import time
import requests
from datetime import datetime as dt
from django.db.models import Count, Sum

from kmd_ntx_api.lib_const import *
from kmd_ntx_api.lib_const_mm2 import *

import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_struct as struct
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_testnet as testnet
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


def recreate_swap_data(swap_data):
    params = {
        "method": "recreate_swap_data",
        "params": {
            "swap": swap_data
        }
    }
    r = mm2_proxy(params)
    return r.json()


def get_bestorders(request):
    coin = helper.get_or_none(request, "coin", "KMD")
    if coin == 'TOKEL': coin = 'TKL'
    params = {
        "method": "best_orders",
        "coin": coin,
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
    if taker_coin == "All":
        taker_coin = None
    if maker_coin == "All":
        maker_coin = None
    data = query.filter_swaps_coins(data, taker_coin, maker_coin)
    data = data.order_by('-timestamp')[:200]
    data = data.values()
    serializer = serializers.swapsSerializerPub(data, many=True)
    return serializer.data


def get_failed_swap_by_uuid(request):
    if 'uuid' in request.GET:
        data = query.get_swaps_failed_data(request.GET['uuid']).values()
        serializer = serializers.swapsFailedSerializerPub(data, many=True)
        data = serializer.data     
    else:
        data = {}
    return data


def get_last_200_failed_swaps(request):
    data = query.get_swaps_failed_data().order_by('-timestamp')[:200]
    data = data.values()
    serializer = serializers.swapsFailedSerializerPub(data, many=True)
    return serializer.data


def get_last_200_failed_swaps_private(request):
    pw = helper.get_or_none(request, 'pw')
    if pw == BASIC_PW:
        taker_coin = helper.get_or_none(request, "taker_coin")
        maker_coin = helper.get_or_none(request, "maker_coin")
        if taker_coin == "All":
            taker_coin = None
        if maker_coin == "All":
            maker_coin = None
        data = query.get_swaps_failed_data()
        data = query.filter_swaps_coins(data, taker_coin, maker_coin)
        data = data.order_by('-timestamp')[:200].values()
        serializer = serializers.swapsFailedSerializer(data, many=True)
        return serializer.data
    else:
        return []


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
        maker_gui_parts = list(set(maker_gui.split(" ")))
        for part in maker_gui_parts:
            if len(part) == 9:
                maker_gui_version = part
        taker_gui_parts = list(set(taker_gui.split(" ")))
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

    taker_pubkeys = data.values('taker_pubkey','taker_gui','taker_version')\
                        .annotate(num_swaps=Count('taker_pubkey'))
    maker_pubkeys = data.values('maker_pubkey', 'maker_gui','maker_version')\
                        .annotate(num_swaps=Count('maker_pubkey'))
    # resp = struct.default_swap_totals()
    
    taker_data = []
    taker_dict = {
        "global": {
            "num_swaps": 0,
            "pubkeys": []
        },
        "os": {},
        "ui": {}
    }
    # Add pubkey totals
    for item in taker_pubkeys:
        os, ui, gui_version, mm2_version = categorise_trade(item["taker_gui"], item["taker_version"])

        taker_data.append({
            "os": os,
            "ui": ui,
            "gui_version": gui_version,
            "mm2_version": mm2_version,
            "pubkey": item['taker_pubkey'],
            "num_swaps": item['num_swaps']       
        })

        if os not in taker_dict["os"]:
            taker_dict["os"].update({
                os: {
                    "num_swaps": 0,
                    "pubkeys": [],
                    "ui": {}
                }
            })

        if ui not in taker_dict["os"][os]["ui"]:
            taker_dict["os"][os]["ui"].update({
                ui: {
                    "num_swaps": 0,
                    "pubkeys": [],
                    "versions": {}
                }
            })

        if gui_version not in taker_dict["os"][os]["ui"][ui]["versions"]:
            taker_dict["os"][os]["ui"][ui]["versions"].update({
                gui_version: {
                    "num_swaps": 0,
                    "pubkeys": []                
                }
            })

        taker_dict["global"]["num_swaps"] += item['num_swaps']
        if item['taker_pubkey'] not in taker_dict["global"]["pubkeys"]:
            taker_dict["global"]["pubkeys"].append(item['taker_pubkey'])

        taker_dict["os"][os]["num_swaps"] += item['num_swaps']
        if item['taker_pubkey'] not in taker_dict["os"][os]["pubkeys"]:
            taker_dict["os"][os]["pubkeys"].append(item['taker_pubkey'])

        taker_dict["os"][os]["ui"][ui]["num_swaps"] += item['num_swaps']
        if item['taker_pubkey'] not in taker_dict["os"][os]["ui"][ui]["pubkeys"]:
            taker_dict["os"][os]["ui"][ui]["pubkeys"].append(item['taker_pubkey'])

        taker_dict["os"][os]["ui"][ui]["versions"][gui_version]["num_swaps"] += item['num_swaps']
        if item['taker_pubkey'] not in taker_dict["os"][os]["ui"][ui]["versions"][gui_version]["pubkeys"]:
            taker_dict["os"][os]["ui"][ui]["versions"][gui_version]["pubkeys"].append(item['taker_pubkey'])


    maker_data = []
    maker_dict = {
        "global": {
            "num_swaps": 0,
            "pubkeys": []
        },
        "os": {}
    }

    for item in maker_pubkeys:
        os, ui, gui_version, mm2_version = categorise_trade(item["maker_gui"], item["maker_version"])
    
        maker_data.append({
            "os": os,
            "ui": ui,
            "gui_version": gui_version,
            "mm2_version": mm2_version,
            "pubkey": item['maker_pubkey'],
            "num_swaps": item['num_swaps']       
        })

        if os not in maker_dict["os"]:
            maker_dict["os"].update({
                os: {
                    "num_swaps": 0,
                    "pubkeys": [],
                    "ui": {}
                }
            })

        if ui not in maker_dict["os"][os]["ui"]:
            maker_dict["os"][os]["ui"].update({
                ui: {
                    "num_swaps": 0,
                    "pubkeys": [],
                    "versions": {}
                }
            })

        if gui_version not in maker_dict["os"][os]["ui"][ui]["versions"]:
            maker_dict["os"][os]["ui"][ui]["versions"].update({
                gui_version: {
                    "num_swaps": 0,
                    "pubkeys": []                
                }
            })

        maker_dict["global"]["num_swaps"] += item['num_swaps']
        if item['maker_pubkey'] not in maker_dict["global"]["pubkeys"]:
            maker_dict["global"]["pubkeys"].append(item['maker_pubkey'])

        maker_dict["os"][os]["num_swaps"] += item['num_swaps']
        if item['maker_pubkey'] not in maker_dict["os"][os]["pubkeys"]:
            maker_dict["os"][os]["pubkeys"].append(item['maker_pubkey'])

        maker_dict["os"][os]["ui"][ui]["num_swaps"] += item['num_swaps']
        if item['maker_pubkey'] not in maker_dict["os"][os]["ui"][ui]["pubkeys"]:
            maker_dict["os"][os]["ui"][ui]["pubkeys"].append(item['maker_pubkey'])

        maker_dict["os"][os]["ui"][ui]["versions"][gui_version]["num_swaps"] += item['num_swaps']
        if item['maker_pubkey'] not in maker_dict["os"][os]["ui"][ui]["versions"][gui_version]["pubkeys"]:
            maker_dict["os"][os]["ui"][ui]["versions"][gui_version]["pubkeys"].append(item['maker_pubkey'])


    global_swaps = maker_dict["global"]["num_swaps"]
    global_maker_pubkeys = len(list(set(maker_dict["global"]["pubkeys"])))
    global_taker_pubkeys = len(list(set(taker_dict["global"]["pubkeys"])))


    for os in taker_dict["os"]:
        os_swaps = taker_dict["os"][os]["num_swaps"]
        os_pubkeys = len(taker_dict["os"][os]["pubkeys"])

        taker_dict["os"][os].update({
            "global_swap_pct": helper.safe_div(os_swaps, global_swaps),
            "global_pubkey_pct": helper.safe_div(os_pubkeys, global_taker_pubkeys),
        })

        for ui in taker_dict["os"][os]["ui"]:
            ui_swaps = taker_dict["os"][os]["ui"][ui]["num_swaps"]
            ui_pubkeys = len(taker_dict["os"][os]["ui"][ui]["pubkeys"])

            taker_dict["os"][os]["ui"][ui].update({
                "global_swap_pct": helper.safe_div(ui_swaps, global_swaps),
                "global_pubkey_pct": helper.safe_div(ui_pubkeys, global_taker_pubkeys),
                "os_swap_pct": helper.safe_div(ui_swaps, os_swaps),
                "os_pubkey_pct": helper.safe_div(ui_pubkeys, os_pubkeys),
            })

            for version in taker_dict["os"][os]["ui"][ui]["versions"]:
                version_swaps = taker_dict["os"][os]["ui"][ui]["versions"][version]["num_swaps"]
                version_pubkeys = len(taker_dict["os"][os]["ui"][ui]["versions"][version]["pubkeys"])
                
                taker_dict["os"][os]["ui"][ui]["versions"][version].update({
                    "global_swap_pct": helper.safe_div(version_swaps, global_swaps),
                    "global_pubkey_pct": helper.safe_div(version_pubkeys, global_taker_pubkeys),
                    "os_swap_pct": helper.safe_div(version_swaps, os_swaps),
                    "os_pubkey_pct": helper.safe_div(version_pubkeys, os_pubkeys),
                    "ui_swap_pct": helper.safe_div(version_swaps, ui_swaps),
                    "ui_pubkey_pct": helper.safe_div(version_pubkeys, ui_pubkeys),
                })


    for os in maker_dict["os"]:
        os_swaps = maker_dict["os"][os]["num_swaps"]
        os_pubkeys = len(maker_dict["os"][os]["pubkeys"])

        maker_dict["os"][os].update({
            "global_swap_pct": helper.safe_div(os_swaps, global_swaps),
            "global_pubkey_pct": helper.safe_div(os_pubkeys, global_maker_pubkeys),
        })

        for ui in maker_dict["os"][os]["ui"]:
            ui_swaps = maker_dict["os"][os]["ui"][ui]["num_swaps"]
            ui_pubkeys = len(maker_dict["os"][os]["ui"][ui]["pubkeys"])

            maker_dict["os"][os]["ui"][ui].update({
                "global_swap_pct": helper.safe_div(ui_swaps, global_swaps),
                "global_pubkey_pct": helper.safe_div(ui_pubkeys, global_maker_pubkeys),
                "os_swap_pct": helper.safe_div(ui_swaps, os_swaps),
                "os_pubkey_pct": helper.safe_div(ui_pubkeys, os_pubkeys),
            })

            for version in maker_dict["os"][os]["ui"][ui]["versions"]:
                version_swaps = maker_dict["os"][os]["ui"][ui]["versions"][version]["num_swaps"]
                version_pubkeys = len(maker_dict["os"][os]["ui"][ui]["versions"][version]["pubkeys"])
                
                maker_dict["os"][os]["ui"][ui]["versions"][version].update({
                    "global_swap_pct": helper.safe_div(version_swaps, global_swaps),
                    "global_pubkey_pct": helper.safe_div(version_pubkeys, global_maker_pubkeys),
                    "os_swap_pct": helper.safe_div(version_swaps, os_swaps),
                    "os_pubkey_pct": helper.safe_div(version_pubkeys, os_pubkeys),
                    "ui_swap_pct": helper.safe_div(version_swaps, ui_swaps),
                    "ui_pubkey_pct": helper.safe_div(version_pubkeys, ui_pubkeys),
                })

    # By ui
    resp = {
        "to_time": to_time,
        "from_time": from_time,
        "maker_dict": maker_dict,
        "taker_dict": taker_dict,
        "maker_data": maker_data,
        "taker_data": taker_data
    }
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


def get_zhtlc_activation(coins_config, coin):
    return {
        "method": "task::enable_z_coin::init",
        "mmrpc": "2.0",
        "userpass":"'$userpass'",
        "params": {
            "ticker": coin,
            "activation_params": {
                "mode": {
                    "rpc": "Light",
                    "rpc_data": {
                        "electrum_servers": coins_config[coin]["electrum"],
                        "light_wallet_d_servers": coins_config[coin]["light_wallet_d_servers"]
                    }
                }
            }
        }
    }


def get_utxo_activation(coins_config, coin):
    return {
        "userpass": "'$userpass'",
        "method": "electrum",
        "coin": coin,
        "servers": coins_config[coin]["electrum"],
    }


def get_tendermint_activation(coins_config, coin):
    return {
        "method": "enable_tendermint_with_assets",
        "mmrpc": "2.0",
        "params": {
            "ticker": coin,
            "tokens_params": [],
            "rpc_urls": coins_config[coin]["rpc_urls"]
        },
        "userpass": "'$userpass'"
    }


def get_tendermint_token_activation(coin):
    return {
        "userpass": "'$userpass'",
        "method": "enable_tendermint_token",
        "mmrpc": "2.0",
        "params": {
            "ticker": coin,
            "activation_params": {
            "required_confirmations": 3
            }
        }
    }


def get_activation_command(coins_config, coin):
    resp_json = {}
    compatible = coins_config[coin]["mm2"] == 1
    if not compatible:
        resp_json
    protocol = coins_config[coin]["protocol"]["type"]
    platform = None

    for i in ["swap_contract_address", "fallback_swap_contract"]:
        if i in coins_config[coin]:
            resp_json.update({i: coins_config[coin][i]})

    if "protocol_data" in coins_config[coin]["protocol"]:
        if "platform" in coins_config[coin]["protocol"]["protocol_data"]:
            platform = coins_config[coin]["protocol"]["protocol_data"]["platform"]

    if protocol == "ZHTLC":
        platform = "UTXO"
        resp_json.update(get_zhtlc_activation(coins_config, coin))
    elif protocol == "UTXO":
        platform = 'UTXO'
        resp_json.update(get_utxo_activation(coins_config, coin))
    elif protocol == "QRC20" or coin in ['QTUM', 'QTUM-segwit']:
        platform = 'QRC20'
        resp_json.update(get_utxo_activation(coins_config, coin))
    elif protocol == "tQTUM" or coin in ['tQTUM', 'tQTUM-segwit']:
        platform = 'tQTUM'
        resp_json.update(get_utxo_activation(coins_config, coin))
    elif protocol == "TENDERMINT":
        platform = 'TENDERMINT'
        resp_json.update(get_tendermint_activation(coins_config, coin))
    elif protocol == "TENDERMINTTOKEN":
        platform = 'TENDERMINTTOKEN'
        resp_json.update(get_tendermint_token_activation(coins_config, coin))
    elif platform in PLATFORM_URLS:
        resp_json.update({
                "userpass": "'$userpass'",
                "method": "enable",
                "coin": coin
            })
        resp_json.update({PLATFORM_URLS[platform]})
    elif coin in PLATFORM_URLS:
        resp_json.update({
                "userpass": "'$userpass'",
                "method": "enable",
                "coin": coin
            })
        resp_json.update({PLATFORM_URLS[coin]})
    else:
        logger.error("No platform found for coin: {}".format(coin))
        

    return platform, resp_json



def get_activation_commands(request):
    logger.info("Running get_activation_commands")
    enable_commands = {"commands":{}}
    resp_json = {}

    coins_config = helper.get_coins_config()
    selected_coin = helper.get_or_none(request, "coin")
    if selected_coin is None:
        for coin in coins_config:
            platform, resp_json = get_activation_command(coins_config, coin)
            if platform not in enable_commands["commands"]:
                enable_commands["commands"].update({platform: {}})
            enable_commands["commands"][platform].update({coin: helper.sort_dict(resp_json)})
        return enable_commands
    else:
        platform, resp_json = get_activation_command(coins_config, selected_coin)
        return resp_json


def get_coin_activation_commands(request):
    coin_commands = {}
    logger.info("Running get_coin_activation_commands")
    protocol_commands = get_activation_commands(request)["commands"]
    for protocol in protocol_commands:
        for coin in protocol_commands[protocol]:
            coin_commands.update({coin: protocol_commands[protocol][coin]})
    return coin_commands

#### SEEDNODES 

def get_active_mm2_versions(ts):
    data = requests.get(VERSION_TIMESPANS_URL).json()
    active_versions = []
    for version in data:
        if int(ts) < data[version]["end"]:
            active_versions.append(version)
    return active_versions


def is_mm2_version_valid(version, timestamp):
    active_versions = get_active_mm2_versions(timestamp)
    if version in active_versions:
        return True
    return False


def get_seednode_version_date_table(request):
    season = helper.get_page_season(request)
    start = int(helper.get_or_none(request, "start", time.time() - SINCE_INTERVALS["day"]))
    end = int(helper.get_or_none(request, "end", time.time()))

    notary_list = helper.get_notary_list(season)
    default_scores = helper.prepopulate_seednode_version_date(notary_list)

    hour_headers = list(default_scores.keys())
    hour_headers.sort()
    table_headers = ["Notary"] + hour_headers + ["Total"]

    data = query.get_seednode_version_stats_data(start=start, end=end)
    '''
    if is_testnet:
        proposals = testnet.get_candidates_proposals(request)
    '''

    scores = data.values()
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
            if default_scores[hour][notary]["score"] == 0.2:
                total += default_scores[hour][notary]["score"]
            elif default_scores[hour][notary]["score"] == 0.01:
                default_scores[hour][notary]["score"] = f'0 (WSS connection failing)'
            elif default_scores[hour][notary]["score"] == 0:
                default_scores[hour][notary]["score"] = f'0 (Wrong version: {default_scores[hour][notary]["versions"]})'
            notary_row.update({
                hour: default_scores[hour][notary]["score"]
            })

        notary_row.update({
            "Total": round(total,1)
        })

        '''
        if is_testnet:
            notary = testnet.translate_candidate_to_proposal_name(notary)

            if notary.lower() in proposals: proposal = proposals[notary.lower()]
            else: proposal = ""

            notary_row.update({
                "proposal": proposal
            })                          
        '''
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
    season =  helper.get_page_season(request)
    year = helper.get_or_none(request, "year", None)
    month = helper.get_or_none(request, "month", None)
    start, end, last_day = helper.get_month_epoch_range(year, month)

    '''
    if is_testnet:
        proposals = testnet.get_candidates_proposals(request)
        print(proposals)
    '''

    notary_list = helper.get_notary_list(season)
    default_scores = helper.prepopulate_seednode_version_month(notary_list)

    day_headers = list(default_scores.keys())
    day_headers.sort()

    table_headers = ["Notary"] + day_headers + ["Total"]
    data = query.get_seednode_version_stats_data(start=start, end=end).values()

    for item in data:
        notary = item["name"]

        if notary in notary_list:
            score = item["score"]
            if score == 0.2:
                date, _ = helper.date_hour(item["timestamp"]).split(" ")
                day = date.split("/")[1]
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
                day: default_scores[day][notary]["score"]
            })

        notary_row.update({
            "Total": round(total,1)
        })


        '''
        if is_testnet:
            notary = testnet.translate_candidate_to_proposal_name(notary)
            if notary.lower() in proposals: proposal = proposals[notary.lower()]
            else: proposal = ""

            notary_row.update({
                "proposal": proposal
            })
        '''

        table_data.append(notary_row)

    return {
        "date_ts": dt.utcfromtimestamp(end).strftime('%m-%Y'),
        "date": dt.utcfromtimestamp(end).strftime('%b %Y'),
        "headers": table_headers,
        "table_data": table_data,
        "scores": default_scores
    }

def get_seednode_version_score_total(request, season=None, start=None, end=None):
    if not season:
        season = helper.get_page_season(request)
    notary_list = helper.get_notary_list(season)
    start = helper.get_or_none(request, "start", start)
    if not start: start = int(time.time()) - SINCE_INTERVALS["day"]
    end = helper.get_or_none(request, "end", end)
    if not end: end = int(time.time())
    data = query.get_seednode_version_stats_data(start=start, end=end)
    notary_scores = list(data.values('name').order_by('name').annotate(sum_score=Sum('score')))
    notaries_with_scores = data.distinct('name').values_list('name', flat=True)

    for notary in notary_list:
        if notary not in notaries_with_scores:
            notary_scores.append({"name": notary, "sum_score": 0})

    resp = {}
    for i in notary_scores:
        if i["name"] in notary_list:
            resp.update({i["name"]: round(i["sum_score"],2)})

    return resp


def categorise_trade(gui, version):
    os = "Unknown"
    ui = "Unknown"
    gui_version = "Unknown"
    mm2_version = "Unknown"
    if gui:
        gui_split = gui.split(" ")
    else:
        gui_split = []
    if version:
        version_split = version.split("_")
    else:
        version_split = []
    info = gui_split + version_split

    os_list = ["ios", "android", "windows", "darwin", "linux"]

    for gui in gui_split:
        for version in version_split:
            if gui.lower() == version.lower() and gui.lower() not in os_list:
                mm2_version = gui.lower()
                break

    for i in info:
        i = i.replace(';','')
        if i.lower() in os_list:
            os = i.lower()
            break

    for i in gui_split:
        if i.lower().find("beta") > -1:
            gui_version = i.lower()
            break

        if i.lower().startswith("0."):
            gui_version = i.lower()
            break

    ui_list = ["Firo", "pyMakerbot", "MM2CLI", "dexstats", "BumbleBee", 'None',
                        "mpm", "BitcoinZ", "dogedex", "AtomicDex", "SwapCase", "SmartDEX",
                        "air_dex", "shibaDEX", "ColliderDEX"]

    for i in ui_list:
        for gui in gui_split:
            i = i.replace(';','')
            if i.lower() == gui.lower():
                ui = gui.lower()
                break

    return os, ui, gui_version, mm2_version


def get_electrum_status():
    return requests.get("https://electrum-status.dragonhound.info/api/v1/electrums_status").json()


