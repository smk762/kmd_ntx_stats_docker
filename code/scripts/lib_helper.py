#!/usr/bin/env python3.12
from lib_const import *
from const_seasons import SEASONS
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

def handle_translate_coins_reverse(coin):
    if coin in REVERSE_TRANSLATE_COINS:
        return REVERSE_TRANSLATE_COINS[coin]
    return coin

def get_dpow_coin_src(src):
    try:
        return src.split("(")[1].replace(")","")
    except:
        return src


def get_nn_region_split(notary):
    x = notary.split("_")
    region = x[-1]
    nn = notary.replace(f"_{region}", "")
    return nn, region

def get_results_or_none(cursor):
    try:
        results = cursor.fetchall()
        return results
    except:
        return ()


def translate_dpow_server(server):
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


def get_active_seasons(timestamp=None):
    active_seasons = []
    if not timestamp: timestamp = int(time.time())
    for season in SEASONS.INFO:
        if timestamp >= SEASONS.INFO[season]["start_time"]:
            if "end_time" in SEASONS.INFO[season]:
                if timestamp <= SEASONS.INFO[season]["end_time"]:
                    active_seasons.append(season)
            if "post_season_end_time" in SEASONS.INFO[season]:
                if timestamp <= SEASONS.INFO[season]["post_season_end_time"]:
                    active_seasons.append(season)
        elif timestamp + 86400 * 7 >= SEASONS.INFO[season]["start_time"]:
            active_seasons.append(season)
    return active_seasons


def is_postseason(timestamp=None, block=None):
    if block:
        for season in SEASONS.INFO:
            if "post_season_end_block" in SEASONS.INFO[season]:
                if block >= SEASONS.INFO[season]["end_block"]:
                    if block <= SEASONS.INFO[season]["post_season_end_block"]:
                        return True
        

    if not timestamp:
        timestamp = int(time.time())
    for season in SEASONS.INFO:
        if "post_season_end_time" in SEASONS.INFO[season]:
            if timestamp >= SEASONS.INFO[season]["end_time"]:
                if timestamp <= SEASONS.INFO[season]["post_season_end_time"]:
                    return True
    return False


def get_pubkeys(season, server):
    if season in NOTARY_PUBKEYS:
        if server in NOTARY_PUBKEYS[season]:
            return NOTARY_PUBKEYS[season][server]
    return []


def get_address_from_notary(season, notary, coin):
    if season in SEASONS.INFO:
        for server in SEASONS.INFO[season]["servers"]:
            if coin in SEASONS.INFO[season]["servers"][server]["addresses"]:
                for address in SEASONS.INFO[season]["servers"][server]["addresses"][coin]:
                    if SEASONS.INFO[season]["servers"][server]["addresses"][coin][address] == notary:
                        return address
    return "Unknown"


def has_season_started(season, by_block=False):
    now = time.time()
    if season in SEASONS.INFO:
        if by_block:
            if SEASONS.INFO[season]["start_block"] < now:
                return True

        elif SEASONS.INFO[season]["start_time"] < now:
            return True
    return False


def get_season_notaries(season):
    if season in SEASONS.INFO:
        notaries = SEASONS.INFO[season]["notaries"]
        notaries.sort()
        return notaries
    return []


def get_season_coins(season=None, server=None, epoch=None):
    coins = []
    if not season:
        for season in SEASONS.INFO:
            coins += SEASONS.INFO[season]["coins"]
        coins = list(set(coins))

    if season in SEASONS.INFO:
        coins = SEASONS.INFO[season]["coins"]

        if server in SEASONS.INFO[season]["servers"]:
            coins = SEASONS.INFO[season]["servers"][server]["coins"]

            if epoch in SEASONS.INFO[season]["servers"][server]["epochs"]:
                coins = SEASONS.INFO[season]["servers"][server]["epochs"][epoch]["coins"]
    coins.sort()
    return coins

    
def get_season_servers(season):
    if season in SEASONS.INFO:
        servers = list(SEASONS.INFO[season]["servers"].keys())
        servers.sort()
        return servers
    return []


def get_season_server_epochs(season, server):
    if season in SEASONS.INFO:
        if server in SEASONS.INFO[season]["servers"]:
            epochs = list(SEASONS.INFO[season]["servers"][server]["epochs"].keys())
            epochs.sort()
            return epochs
    return []
