#!/usr/bin/env python3.12
from functools import lru_cache
from lib_const import *
from const_seasons import SEASONS
from lib_urls import *


@lru_cache(maxsize=None)
def get_electrum_url_port(electrum):
    return electrum.split(":")


def safe_div(x,y):
    if y==0: return 0
    return float(x/y)


@lru_cache(maxsize=None)
def handle_translate_coins(coin):
    if coin in TRANSLATE_COINS:
        return TRANSLATE_COINS[coin]
    return coin

@lru_cache(maxsize=None)
def handle_translate_coins_reverse(coin):
    if coin in REVERSE_TRANSLATE_COINS:
        return REVERSE_TRANSLATE_COINS[coin]
    return coin

def get_dpow_coin_src(src):
    try:
        return src.split("(")[1].replace(")","")
    except:
        return src


@lru_cache(maxsize=None)
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


@lru_cache(maxsize=None)
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


@lru_cache(maxsize=None)
def is_notary_ltc_address(addr):
    if addr in ALL_SEASON_NOTARY_LTC_ADDRESSES:
        return True
    return False


def get_active_seasons(timestamp=None, block=None):
    """
    Determine active seasons using both wall-clock time and chain height.
    Preference: return only the most recent matching season to avoid
    processing historical seasons during live runs.
    """
    active_seasons = []
    if not timestamp:
        timestamp = int(time.time())

    # Try to infer current KMD height if not provided.
    if block is None:
        try:
            block = RPC["KMD"].getblockcount()
        except Exception:
            block = None

    for season in SEASONS.INFO:
        info = SEASONS.INFO[season]

        time_active = (
            timestamp >= info["start_time"] and
            (
                ("end_time" in info and timestamp <= info["end_time"]) or
                ("post_season_end_time" in info and timestamp <= info["post_season_end_time"])
            )
        )

        block_active = False
        if block is not None:
            start_block = info.get("start_block")
            end_block = info.get("post_season_end_block") or info.get("end_block")
            if start_block and end_block:
                block_active = start_block <= block <= end_block

        if time_active or block_active:
            active_seasons.append(season)
        # Upcoming within a week (time-based only)
        elif timestamp + 86400 * 7 >= info["start_time"] and timestamp <= info["end_time"]:
            active_seasons.append(season)

    # Prefer the most recent season by start_block when multiple match.
    if active_seasons:
        active_seasons = sorted(
            set(active_seasons),
            key=lambda s: SEASONS.INFO[s].get("start_block", 0),
            reverse=True
        )
        active_seasons = [active_seasons[0]]

    logger.info(f"Active seasons: {active_seasons}")
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


@lru_cache(maxsize=None)
def get_pubkeys(season, server):
    if season in NOTARY_PUBKEYS:
        if server in NOTARY_PUBKEYS[season]:
            return NOTARY_PUBKEYS[season][server]
    return []


@lru_cache(maxsize=None)
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


@lru_cache(maxsize=None)
def get_season_notaries(season):
    if season in SEASONS.INFO:
        notaries = SEASONS.INFO[season]["notaries"]
        notaries.sort()
        return notaries
    return []

@lru_cache(maxsize=None)
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

    # Dynamically merge currently-active dPoW coins (covers late additions like MDX/RAPH/BCZERO).
    try:
        cache_key = cached.namespaced_key("epochs", "dpow_active_coins")
        active_details = cached.get_data(cache_key, expire=300) or {}
        if server:
            extra = [c for c, meta in active_details.items() if meta.get("dpow", {}).get("server") == server]
        else:
            extra = list(active_details.keys())
        coins = list(set(coins + extra))
    except Exception:
        pass

    coins.sort()
    return coins

    
@lru_cache(maxsize=None)
def get_season_servers(season):
    if season in SEASONS.INFO:
        servers = list(SEASONS.INFO[season]["servers"].keys())
        servers.sort()
        return servers
    return []


@lru_cache(maxsize=None)
def get_season_server_epochs(season, server):
    if season in SEASONS.INFO:
        if server in SEASONS.INFO[season]["servers"]:
            epochs = list(SEASONS.INFO[season]["servers"][server]["epochs"].keys())
            epochs.sort()
            return epochs
    return []
