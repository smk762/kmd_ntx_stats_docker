import requests
import json
from kmd_ntx_api.lib_const import MM2_USERPASS, MM2_IP

# https://stats-api.atomicdex.io/

def mm2_proxy(params):
  params.update({"userpass":MM2_USERPASS})
  print(json.dumps(params))
  r = requests.post(MM2_IP, json.dumps(params))
  print(r)
  return r

def get_orderbook(request):
    base = "KMD"
    rel = "BTC"
    if "base" in request.GET:
        base = request.GET["base"]
    if "rel" in request.GET:
        rel = request.GET["rel"]
    params = {
        "method":"orderbook",
        "base":base,
        "rel":rel
    }
    r = mm2_proxy(params)
    return r.json()

def get_bestorders(request):
    coin = "KMD"
    if "coin" in request.GET:
        coin = request.GET["coin"]
    params = {
        "method":"best_orders",
        "coin":coin,
        "action":"buy",
        "volume":100,

    }
    r = mm2_proxy(params)
    return r.json()