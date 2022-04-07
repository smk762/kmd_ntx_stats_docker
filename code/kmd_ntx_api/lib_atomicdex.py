import copy
import json
import requests
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_struct as struct
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.serializers as serializers

# https://stats-api.atomicdex.io/

def get_nn_mm2_stats(request):
    name = helper.get_or_none(request, "name")
    version = helper.get_or_none(request, "version")
    limit = helper.get_or_none(request, "limit")
    data = query.get_nn_mm2_stats_data(name, version, limit)
    data = data.values()
    serializer = serializers.mm2statsSerializer(data, many=True)
    return serializer.data


def get_nn_mm2_stats_by_hour(request):
    notary = helper.get_or_none(request, "notary")
    start = helper.get_or_none(
        request, "start", time.time() - SINCE_INTERVALS["day"]
    )
    end = helper.get_or_none(request, "end", time.time())

    if request.GET.get("chart"):
        data = query.get_nn_mm2_stats_by_hour_chart_data(
            int(start), int(end), notary
        )
    else:
        data = query.get_nn_mm2_stats_by_hour_data(
            int(start), int(end), notary
        )
    return data


def mm2_proxy(params):
    try:
        params.update({"userpass": MM2_USERPASS})
        r = requests.post(MM2_IP, json.dumps(params))
        return r
    except Exception as e:
        return e


# TODO: Handle TOKEL
def get_orderbook(request):
    params = {
        "method": "orderbook",
        "base": helper.get_or_none(request, "base", "KMD"),
        "rel": helper.get_or_none(request, "rel", "BTC")
    }
    r = mm2_proxy(params)
    return r.json()


# TODO: Handle TOKEL
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
