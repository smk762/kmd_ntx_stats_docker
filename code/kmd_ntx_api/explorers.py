#!/usr/bin/env python3
import requests
from kmd_ntx_api.helper import get_or_none
from kmd_ntx_api.query import get_coins_data

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
    if coin == "MIL":
        return f"https://mil.kmdexplorer.io/api"
    if coin == "VOTE2024":
        return f"https://vote2024.explorer.lordofthechains.com/insight-api-komodo"

    if coin == "MCL":
        return f"https://explorer.marmara.io/insight-api-komodo"

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


def get_block_info(coin, block_height):
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