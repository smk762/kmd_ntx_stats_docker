import json
import requests
from datetime import datetime as dt

from kmd_ntx_api.const import MM2_USERPASS, MM2_IP
from kmd_ntx_api.helper import get_or_none


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
        "base": get_or_none(request, "base", "KMD"),
        "rel": get_or_none(request, "rel", "DGB")
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
    coin = get_or_none(request, "coin", "KMD")
    if coin == 'TOKEL': coin = 'TKL'
    params = {
        "method": "best_orders",
        "coin": coin,
        "action": get_or_none(request, "action", "buy"),
        "volume": get_or_none(request, "volume", 100),
    }
    r = mm2_proxy(params)
    return r.json()


def send_raw_tx(request):
    params = {
        "method": "send_raw_transaction",
        "coin": get_or_none(request, "coin", "KMD"),
        "tx_hex": get_or_none(request, "tx_hex", "")
    }
    r = mm2_proxy(params)
    return r.json()

