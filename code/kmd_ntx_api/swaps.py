import time
from django.db.models import Count
import kmd_ntx_api.serializers as serializers
from kmd_ntx_api.const import BASIC_PW, SINCE_INTERVALS
from kmd_ntx_api.helper import is_hex, get_or_none, safe_div
from kmd_ntx_api.query import get_swaps_failed_data, filter_swaps_coins, \
    get_swaps_data, filter_swaps_timespan


def get_last_200_failed_swaps(request):
    data = get_swaps_failed_data().order_by('-timestamp')[:200]
    data = data.values()
    serializer = serializers.swapsFailedSerializerPub(data, many=True)
    return serializer.data


def get_last_200_failed_swaps_private(request):
    pw = get_or_none(request, 'pw')
    if pw == BASIC_PW:
        taker_coin = get_or_none(request, "taker_coin")
        maker_coin = get_or_none(request, "maker_coin")
        if taker_coin == "All":
            taker_coin = None
        if maker_coin == "All":
            maker_coin = None
        data = get_swaps_failed_data()
        data = filter_swaps_coins(data, taker_coin, maker_coin)
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

        item.update({
            "taker_gui": taker,
            "maker_gui": maker,
        })
    return swaps_data


def get_last_200_swaps(request):
    data = get_swaps_data()
    taker_coin = get_or_none(request, "taker_coin")
    maker_coin = get_or_none(request, "maker_coin")
    if taker_coin == "All":
        taker_coin = None
    if maker_coin == "All":
        maker_coin = None
    data = filter_swaps_coins(data, taker_coin, maker_coin)
    data = data.order_by('-timestamp')[:200]
    data = data.values()
    serializer = serializers.swapsSerializerPub(data, many=True)
    return serializer.data


def get_failed_swap_by_uuid(request):
    if 'uuid' in request.GET:
        data = get_swaps_failed_data(request.GET['uuid']).values()
        serializer = serializers.swapsFailedSerializerPub(data, many=True)
        data = serializer.data     
    else:
        data = {}
    return data


def get_swaps_gui_stats(request):
    now = int(time.time())
    '''
    if "since" in request.GET:
        if request.GET["since"] in const.SINCE_INTERVALS:
            from_time = to_time - const.SINCE_INTERVALS[request.GET["since"]]
    '''
    to_time = get_or_none(request, "to_time", now)
    from_time = get_or_none(
        request,
        "from_time",
        now - SINCE_INTERVALS["week"]
    )
    data = get_swaps_data()
    data = filter_swaps_timespan(data, from_time, to_time)

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
            "global_swap_pct": safe_div(os_swaps, global_swaps),
            "global_pubkey_pct": safe_div(os_pubkeys, global_taker_pubkeys),
        })

        for ui in taker_dict["os"][os]["ui"]:
            ui_swaps = taker_dict["os"][os]["ui"][ui]["num_swaps"]
            ui_pubkeys = len(taker_dict["os"][os]["ui"][ui]["pubkeys"])

            taker_dict["os"][os]["ui"][ui].update({
                "global_swap_pct": safe_div(ui_swaps, global_swaps),
                "global_pubkey_pct": safe_div(ui_pubkeys, global_taker_pubkeys),
                "os_swap_pct": safe_div(ui_swaps, os_swaps),
                "os_pubkey_pct": safe_div(ui_pubkeys, os_pubkeys),
            })

            for version in taker_dict["os"][os]["ui"][ui]["versions"]:
                version_swaps = taker_dict["os"][os]["ui"][ui]["versions"][version]["num_swaps"]
                version_pubkeys = len(taker_dict["os"][os]["ui"][ui]["versions"][version]["pubkeys"])
                
                taker_dict["os"][os]["ui"][ui]["versions"][version].update({
                    "global_swap_pct": safe_div(version_swaps, global_swaps),
                    "global_pubkey_pct": safe_div(version_pubkeys, global_taker_pubkeys),
                    "os_swap_pct": safe_div(version_swaps, os_swaps),
                    "os_pubkey_pct": safe_div(version_pubkeys, os_pubkeys),
                    "ui_swap_pct": safe_div(version_swaps, ui_swaps),
                    "ui_pubkey_pct": safe_div(version_pubkeys, ui_pubkeys),
                })


    for os in maker_dict["os"]:
        os_swaps = maker_dict["os"][os]["num_swaps"]
        os_pubkeys = len(maker_dict["os"][os]["pubkeys"])

        maker_dict["os"][os].update({
            "global_swap_pct": safe_div(os_swaps, global_swaps),
            "global_pubkey_pct": safe_div(os_pubkeys, global_maker_pubkeys),
        })

        for ui in maker_dict["os"][os]["ui"]:
            ui_swaps = maker_dict["os"][os]["ui"][ui]["num_swaps"]
            ui_pubkeys = len(maker_dict["os"][os]["ui"][ui]["pubkeys"])

            maker_dict["os"][os]["ui"][ui].update({
                "global_swap_pct": safe_div(ui_swaps, global_swaps),
                "global_pubkey_pct": safe_div(ui_pubkeys, global_maker_pubkeys),
                "os_swap_pct": safe_div(ui_swaps, os_swaps),
                "os_pubkey_pct": safe_div(ui_pubkeys, os_pubkeys),
            })

            for version in maker_dict["os"][os]["ui"][ui]["versions"]:
                version_swaps = maker_dict["os"][os]["ui"][ui]["versions"][version]["num_swaps"]
                version_pubkeys = len(maker_dict["os"][os]["ui"][ui]["versions"][version]["pubkeys"])
                
                maker_dict["os"][os]["ui"][ui]["versions"][version].update({
                    "global_swap_pct": safe_div(version_swaps, global_swaps),
                    "global_pubkey_pct": safe_div(version_pubkeys, global_maker_pubkeys),
                    "os_swap_pct": safe_div(version_swaps, os_swaps),
                    "os_pubkey_pct": safe_div(version_pubkeys, os_pubkeys),
                    "ui_swap_pct": safe_div(version_swaps, ui_swaps),
                    "ui_pubkey_pct": safe_div(version_pubkeys, ui_pubkeys),
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
