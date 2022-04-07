#!/usr/bin/env python3
from lib_const import *
from lib_urls import *


def get_electrum_url_port(electrum):
    return electrum.split(":")


def safe_div(x,y):
    if y==0: return 0
    return float(x/y)


def handle_translate_coins(coin):
    if coin in TRANSLATE_COINS:
        return TRANSLATE_COINS[coin]
    return coin


def get_dpow_coin_src(src):
    try:
        return src.split("(")[1].replace(")","")
    except:
        return src


def get_dpow_coin_server(server):
    if server.lower() == "dpow-3p":
        return "Third_Party"
    elif server.lower() == "dpow-mainnet":
        return "Main"


def get_assetchain_launch_params(item):
    params = "~/komodo/src/komodod"
    for k, v in item.items():
        if k == 'addnode':
            for ip in v:
                params += " -"+k+"="+ip
        else:
            params += " -"+k+"="+str(v)
    return params



def get_local_addresses(local_info):
    local_addresses = []
    for item in local_info:
        if item["input_index"] != -1:
            local_addresses.append(item["address"])
    return local_addresses


def get_notary_address_lists(vin):
    notary_list = []
    address_list = []
    for item in vin:
        if "address" in item:
            address_list.append(item['address'])
            if item['address'] in KNOWN_ADDRESSES:
                notary = KNOWN_ADDRESSES[item['address']]
                notary_list.append(notary)
            else:
                notary_list.append(item['address'])
    notary_list.sort()
    return notary_list, address_list


def is_notary_ltc_address(addr):
    if addr in ALL_SEASON_NOTARY_LTC_ADDRESSES:
        return True
    return False


def decode_opret_coin(coin):
    """Gets rid of extra data by matching to known coins"""
    # TODO: This could potentially misidentify - be vigilant.
    for x in KNOWN_COINS:
        if len(x) > 2 and x not in EXCLUDE_DECODE_OPRET_COINS:
            if coin.endswith(x):
                coin = x

    # some decodes have a null char error, this gets rid of that so populate script doesnt error out 
    if coin.find('\x00') != -1:
        coin = coin.replace('\x00','')

    return coin


def is_postseason(timestamp=None):
    if not timestamp:
        timestamp = int(time.time())
    for season in SEASONS_INFO:
        if "post_season_end_time" in SEASONS_INFO[season]:
            if timestamp >= SEASONS_INFO[season]["post_season_end_time"]:
                if timestamp <= SEASONS_INFO[season]["end_time"]:
                    return True
    return False


def get_pubkeys(season, server):
    if season in NOTARY_PUBKEYS:
        if server in NOTARY_PUBKEYS[season]:
            return NOTARY_PUBKEYS[season][server]
    return []


def get_address_from_notary(season, notary, coin):
    if season in SEASONS_INFO:
        for server in SEASONS_INFO[season]["servers"]:
            if coin in SEASONS_INFO[season]["servers"][server]["addresses"]:
                for address in SEASONS_INFO[season]["servers"][server]["addresses"][coin]:
                    if SEASONS_INFO[season]["servers"][server]["addresses"][coin][address] == notary:
                        return address
    return "Unknown"


def has_season_started(season):
    now = time.time()
    if season in SEASONS_INFO:
        if SEASONS_INFO[season]["start_time"] < now:
            return True
    return False


def get_season_notaries(season):
    if season in SEASONS_INFO:
        notaries = SEASONS_INFO[season]["notaries"]
        return notaries
    return []