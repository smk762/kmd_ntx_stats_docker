from .lib_helper import get_or_none
import requests
import json
from kmd_ntx_api.lib_const import *
from kmd_ntx_api.lib_query import *

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
