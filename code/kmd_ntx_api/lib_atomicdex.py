from .lib_helper import get_or_none
import requests
import json
from kmd_ntx_api.lib_const import *
from kmd_ntx_api.lib_query import *
from kmd_ntx_api.lib_info import *

# https://stats-api.atomicdex.io/

def get_nn_mm2_stats(request):
    name = get_or_none(request, "name")
    version = get_or_none(request, "version")
    limit = get_or_none(request, "limit")
    data = get_nn_mm2_stats_data(name, version, limit)
    data = data.values()
    serializer = mm2statsSerializer(data, many=True)
    return serializer.data


def get_nn_mm2_stats_by_hour(request):
    start = get_or_none(request, "start")
    if not start:
        start = time.time() - 60 * 60 *24
    end = get_or_none(request, "end")
    if not end:
        end = time.time()
    notary = get_or_none(request, "notary")
    print(start)
    print(end)
    if request.GET.get("chart"):
        data = get_nn_mm2_stats_by_hour_chart_data(int(start), int(end), notary)
    else:
        data = get_nn_mm2_stats_by_hour_data(int(start), int(end), notary)

    return data


def mm2_proxy(params):
  params.update({"userpass": MM2_USERPASS})
  print(json.dumps(params))
  r = requests.post(MM2_IP, json.dumps(params))
  print(r.json())
  return r


def get_orderbook(request):
    base = "KMD"
    rel = "BTC"
    if "base" in request.GET:
        base = request.GET["base"]
    if "rel" in request.GET:
        rel = request.GET["rel"]
    params = {
        "method": "orderbook",
        "base": base,
        "rel": rel
    }
    r = mm2_proxy(params)
    return r.json()


def get_bestorders(request):
    coin = "KMD"
    if "coin" in request.GET:
        coin = request.GET["coin"]
    params = {
        "method": "best_orders",
        "coin": coin,
        "action": "buy",
        "volume": 100,

    }
    r = mm2_proxy(params)
    return r.json()


def send_raw_tx(request):
    print(electrum(request))
    coin = "KMD"
    tx_hex = ""
    if "coin" in request.GET:
        coin = request.GET["coin"]
    if "tx_hex" in request.GET:
        tx_hex = request.GET["tx_hex"]
    params = {
        "method": "send_raw_transaction",
        "coin": coin,
        "tx_hex": tx_hex
    }
    r = mm2_proxy(params)
    return r.json()


def electrum(request):
    coin = "KMD"
    if "coin" in request.GET:
        coin = request.GET["coin"]
    electrums = requests.get(f"{THIS_SERVER}/api/info/electrums/").json()["results"]
    server_params = []
    if coin in electrums:
      servers = electrums[coin]
      for server in servers:
          server_params.append({"url": server})
    params = {
        "method": "electrum",
        "coin": coin,
        "servers": server_params
    }
    r = mm2_proxy(params)
    return r.json()


def get_last_200_swaps(request):
    data = get_swaps_data()
    taker_coin = get_or_none(request, "taker_coin")
    maker_coin = get_or_none(request, "maker_coin")
    data = filter_swaps_coins(data, taker_coin, maker_coin)
    data = data.order_by('-time_stamp')[:200]
    data = data.values()
    serializer = swapsSerializer(data, many=True)
    return serializer.data


def get_failed_swap_by_uuid(request):
    if 'uuid' in request.GET:
        data = get_swaps_failed_data(request.GET['uuid']).values()
        serializer = swapsFailedSerializer(data, many=True)
        data = serializer.data     
    else:
        data = {}
    return data


def get_last_200_failed_swaps(request):
    data = get_swaps_failed_data().order_by('-time_stamp')[:200]
    data = data.values()
    serializer = swapsFailedSerializerPub(data, many=True)
    return serializer.data


def format_gui_os_version(swaps_data):
    for item in swaps_data:
        maker_gui = item["maker_gui"]
        taker_gui = item["taker_gui"]
        maker_version = item["maker_version"]
        taker_version = item["taker_version"]
        if maker_gui is None:
            maker_gui = "None"
        if taker_gui is None:
            taker_gui = "None"
        if maker_version is None:
            maker_version = "None"
        if taker_version is None:
            taker_version = "None"
        maker = f"{maker_gui.lower()} {maker_version.lower()}"
        taker = f"{taker_gui.lower()} {taker_version.lower()}"

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

        maker_gui = None
        taker_gui = None
        for gui in ["AtomicDEX", "DogeDEX", "SmartDEX", 
                    "GleecDEX", "Dexstats", "mpm",
                    "pytomicDEX"]:
            if gui.lower() in maker:
                maker_gui = gui
            if gui.lower() in taker:
                taker_gui = gui
        if maker_gui is None:
            maker_gui = "Unknown"
        if taker_gui is None:
            taker_gui = "Unknown"

        maker_mm2_version = None
        taker_mm2_version = None
        maker_version_parts = maker_version.split("_")
        for part in maker_version_parts:
            if len(part) == 9:
                if is_hex(part):
                    maker_mm2_version = part
        taker_version_parts = taker_version.split("_")
        for part in taker_version_parts:
            if len(part) == 9:
                if is_hex(part):
                    taker_mm2_version = part
        if maker_mm2_version is None:
            maker_mm2_version = "Unknown"
        if taker_mm2_version is None:
            taker_mm2_version = "Unknown"

        maker = f"{maker_gui} {maker_os} {maker_gui_version} {maker_mm2_version}"
        taker = f"{taker_gui} {taker_os} {taker_gui_version} {taker_mm2_version}"
        item.update({"maker": maker, "taker": taker})
    return swaps_data


def get_swaps_coin_stats(from_time, to_time):
    data = get_swaps_data()
    data = filter_swaps_timespan(data, from_time, to_time)
    # coin_count, coin_volume
    # pair_count, pair_volume
    # for item in data:


def get_swaps_stats(from_time, to_time):
    data = get_swaps_data()
    print(from_time)
    print(to_time)
    data = filter_swaps_timespan(data, from_time, to_time)
    taker_pubkeys = data.values('taker_pubkey').annotate(num_swaps=Count('taker_pubkey'))
    maker_pubkeys = data.values('maker_pubkey').annotate(num_swaps=Count('maker_pubkey'))
    taker_gui = data.values('taker_gui').annotate(num_swaps=Count('taker_gui'))
    maker_gui = data.values('maker_gui').annotate(num_swaps=Count('maker_gui'))
    taker_version = data.values('taker_version').annotate(num_swaps=Count('taker_version'))
    maker_version = data.values('maker_version').annotate(num_swaps=Count('maker_version'))
    taker_coin = data.values('taker_coin').annotate(num_swaps=Count('taker_coin'))
    maker_coin = data.values('maker_coin').annotate(num_swaps=Count('maker_coin'))
    resp = {
        "count": data.count(),
        "taker_pubkeys": [{i['taker_pubkey']:i['num_swaps']} for i in taker_pubkeys],
        "maker_pubkeys": [{i['maker_pubkey']:i['num_swaps']} for i in maker_pubkeys],
        "taker_gui": [{i['taker_gui']:i['num_swaps']} for i in taker_gui],
        "maker_gui": [{i['maker_gui']:i['num_swaps']} for i in maker_gui],
        "taker_version": [{i['taker_version']:i['num_swaps']} for i in taker_version],
        "maker_version": [{i['maker_version']:i['num_swaps']} for i in maker_version],
        "taker_coin": [{i['taker_coin']:i['num_swaps']} for i in taker_coin],
        "maker_coin": [{i['maker_coin']:i['num_swaps']} for i in maker_coin]
    }
    return resp


def get_swaps_gui_stats(request):
    print(request.GET)
    to_time = int(time.time())
    from_time = int(time.time()) - SINCE_INTERVALS["week"]
    '''
    if "since" in request.GET:
        if request.GET["since"] in SINCE_INTERVALS:
            from_time = to_time - SINCE_INTERVALS[request.GET["since"]]
    '''
    if "from_time" in request.GET:
        from_time = int(request.GET["from_time"])
    if "to_time" in request.GET:
        to_time = int(request.GET["to_time"])

    data = get_swaps_data()
    print(from_time)
    print(to_time)
    data = filter_swaps_timespan(data, from_time, to_time)
    taker_pubkeys = data.values('taker_pubkey', 'taker_gui').annotate(num_swaps=Count('taker_pubkey'))
    maker_pubkeys = data.values('maker_pubkey', 'maker_gui').annotate(num_swaps=Count('maker_pubkey'))
    resp = {
        "taker": {
            "swap_total": 0,
            "pubkey_total": 0,
            "desktop": {"swap_total": 0,"pubkey_total": 0},
            "android": {"swap_total": 0,"pubkey_total": 0},
            "ios": {"swap_total": 0,"pubkey_total": 0},
            "dogedex": {"swap_total": 0,"pubkey_total": 0},
            "other": {"swap_total": 0,"pubkey_total": 0}
        },
        "maker": {
            "swap_total": 0,
            "pubkey_total": 0,
            "desktop": {"swap_total": 0,"pubkey_total": 0},
            "android": {"swap_total": 0,"pubkey_total": 0},
            "ios": {"swap_total": 0,"pubkey_total": 0},
            "dogedex": {"swap_total": 0,"pubkey_total": 0},
            "other": {"swap_total": 0,"pubkey_total": 0}
        }
    }
    for item in taker_pubkeys:
        category = "other"
        for x in list(resp["taker"].keys()):
            if item["taker_gui"] is not None:
                if item["taker_gui"].lower().find(x) > -1:
                    category = x
        if item["taker_gui"] not in resp["taker"][category]:
            resp["taker"][category].update({item["taker_gui"]:{"swap_total": 0,"pubkey_total": 0}})
        resp["taker"][category][item["taker_gui"]].update({
            item['taker_pubkey']:item['num_swaps'],
        })
        resp["taker"][category][item["taker_gui"]]["pubkey_total"] += 1
        resp["taker"][category][item["taker_gui"]]["swap_total"] += item['num_swaps']
        resp["taker"][category]["pubkey_total"] += 1
        resp["taker"][category]["swap_total"] += item['num_swaps']
        resp["taker"]["swap_total"] += item['num_swaps']

    resp["taker"]["pubkey_total"] = len(taker_pubkeys)

    for category in resp["taker"]:
        if category not in ["swap_total", "swap_pct", "pubkey_total"]:
            pct = resp["taker"][category]["swap_total"]/resp["taker"]["swap_total"]*100
            resp["taker"][category].update({"swap_pct": pct})
            for gui in resp["taker"][category]:
                if gui not in ["swap_total", "swap_pct", "pubkey_total"]:
                    pct = resp["taker"][category][gui]["swap_total"]/resp["taker"]["swap_total"]*100
                    category_pct = resp["taker"][category][gui]["swap_total"]/resp["taker"][category]["swap_total"]*100
                    resp["taker"][category][gui].update({
                        "swap_pct": pct,
                        "swap_category_pct": category_pct,
                    })


    for item in maker_pubkeys:
        category = "other"
        for x in list(resp["maker"].keys()):
            if item["maker_gui"] is not None:
                if item["maker_gui"].lower().find(x) > -1:
                    category = x
        if item["maker_gui"] not in resp["maker"][category]:
            resp["maker"][category].update({item["maker_gui"]:{"swap_total": 0,"pubkey_total": 0}})
        resp["maker"][category][item["maker_gui"]].update({
            item['maker_pubkey']:item['num_swaps'],
        })
        resp["maker"][category][item["maker_gui"]]["pubkey_total"] += 1
        resp["maker"][category][item["maker_gui"]]["swap_total"] += item['num_swaps']
        resp["maker"][category]["pubkey_total"] += 1
        resp["maker"][category]["swap_total"] += item['num_swaps']
        resp["maker"]["swap_total"] += item['num_swaps']

    resp["maker"]["pubkey_total"] = len(maker_pubkeys)

    for category in resp["maker"]:
        if category  not in ["swap_total", "swap_pct", "pubkey_total"]:
            pct = resp["maker"][category]["swap_total"]/resp["maker"]["swap_total"]*100
            resp["maker"][category].update({"swap_pct": pct})
            for gui in resp["maker"][category]:
                if gui not in ["swap_total", "swap_pct", "pubkey_total"]: 
                    pct = resp["maker"][category][gui]["swap_total"]/resp["maker"]["swap_total"]*100
                    category_pct = resp["maker"][category][gui]["swap_total"]/resp["maker"][category]["swap_total"]*100
                    resp["maker"][category][gui].update({
                        "swap_pct": pct,
                        "swap_category_pct": category_pct,
                    })
    return resp


def get_swaps_pubkey_stats(request):
    to_time = int(time.time())
    from_time = int(time.time()) - SINCE_INTERVALS["week"]
    if "since" in request.GET:
        if request.GET["since"] in SINCE_INTERVALS:
            from_time = to_time - SINCE_INTERVALS[request.GET["since"]]
    if "from_time" in request.GET:
        from_time = int(request.GET["from_time"])
    if "to_time" in request.GET:
        to_time = int(request.GET["to_time"])

    data = get_swaps_data()
    data = filter_swaps_timespan(data, from_time, to_time)
    taker_pubkeys = data.values('taker_pubkey', 'taker_gui').annotate(num_swaps=Count('taker_pubkey'))
    maker_pubkeys = data.values('maker_pubkey', 'maker_gui').annotate(num_swaps=Count('maker_pubkey'))
    resp = {}
    for item in taker_pubkeys:
        if item["taker_pubkey"] not in resp:
            resp.update({item["taker_pubkey"]:{"TOTAL": 0}})
        resp[item["taker_pubkey"]].update({
            item['taker_gui']:item['num_swaps'],
        })
        resp[item["taker_pubkey"]]["TOTAL"] += item['num_swaps']
    return resp


def get_contracts(platform):
    print(platform)
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


def is_testnet(coin):
    if coin in ["BNBT", "ETHR", "AVAXT", "tQTUM", "MATICTEST", "AVAXT", "FTMT"]:
        return True
    return False

