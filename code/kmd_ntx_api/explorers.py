#!/usr/bin/env python3
import requests
from kmd_ntx_api.info import get_api_index, get_pages_index, get_mined_between_blocks, \
    get_mined_between_blocktimes, get_base_58_coin_params, get_balances, get_coins, \
    get_coin_prefixes, get_daemon_cli, get_dpow_server_coins_info, get_explorers, \
    get_coin_icons, get_electrums, get_electrums_ssl, get_launch_params, \
    get_coin_social_info, get_ltc_txid_list, get_nn_social_info, get_notary_icons, \
    get_notarised_coin_daily, get_notarised_count_daily, get_notarised_coins, \
    get_notarised_servers, get_notarisation_txid_list, get_notarised_txid, \
    get_notary_ltc_transactions, get_notary_ltc_txid, get_notary_nodes_info
from kmd_ntx_api.const import SINCE_INTERVALS
from kmd_ntx_api.helper import json_resp, get_page_server, get_time_since, get_or_none
from kmd_ntx_api.notary_seasons import get_page_season, get_season, get_seasons_info
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

    if coin == "MCL":
        return f"https://explorer.marmara.io/insight-api-komodo"

    return f"https://{coin.lower()}.explorer.dexstats.info/insight-api-komodo"


def get_dexstats_utxos(coin, address):
    try:
        subdomain = get_base_endpoint(coin)
        endpoint = f"addr/{address}/utxo"
        url = f"{subdomain}/{endpoint}"
        print(url)
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