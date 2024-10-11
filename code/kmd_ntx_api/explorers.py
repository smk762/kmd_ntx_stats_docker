#!/usr/bin/env python3.12
import requests
from kmd_ntx_api.helper import get_or_none
from kmd_ntx_api.query import get_coins_data
from kmd_ntx_api.logger import logger

# Grabs data from Dexstats explorer APIs
# e.g. https://kmd.explorer.dexstats.info/insight-api-komodo


def get_explorers(request):
    coin = get_or_none(request, "coin")

    data = get_coins_data(coin)
    data = data.order_by('coin').values('coin', 'explorers')

    resp = {}
    for item in data:
        explorers = item['explorers']
        if len(explorers) > 0:
            coin = item['coin']
            resp.update({coin:explorers})
    return resp


def get_base_endpoint(coin):
    if coin == "MCL":
        return f"https://explorer.marmara.io/insight-api-komodo"
    if coin == "GLEEC":
        return f"https://explorer.gleec.com/insight-api-komodo"
    if coin in ["GLEEC_OLD", "GLEEC-OLD"]:
        return f"https://old.gleec.xyz/insight-api-komodo"

    return f"https://{coin.lower()}.explorer.dexstats.info/insight-api-komodo"


def get_dexstats_utxos(coin, address):
    try:
        subdomain = get_base_endpoint(coin)
        endpoint = f"addr/{address}/utxo"
        url = f"{subdomain}/{endpoint}"
        return requests.get(url).json()
    except Exception as e:
        return f"{e}"


def get_sync(coin):
    try:
        subdomain = get_base_endpoint(coin)
        url = f"{subdomain}/sync"
        return requests.get(f"{url}").json()
    except Exception as e:
        return f"{e}"


def get_blockhash(coin, block_height):
    try:
        subdomain = get_base_endpoint(coin)
        endpoint = f"block-index/{block_height}"
        return requests.get(f"{subdomain}/{endpoint}").json()
    except Exception as e:
        return f"{e}"


def getblock(coin, block_hash):
    try:
        subdomain = get_base_endpoint(coin)
        endpoint = f"block/{block_hash}"
        return requests.get(f"{subdomain}/{endpoint}").json()
    except Exception as e:
        return f"{e}"


def get_balance(coin, addr):
    try:
        subdomain = get_base_endpoint(coin)
        endpoint = f"addr/{addr}"
        return requests.get(f"{subdomain}/{endpoint}").json()
    except Exception as e:
        return f"{e}"
