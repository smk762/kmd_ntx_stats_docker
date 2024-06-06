import os
import sys
import time
import json
import requests
from os.path import expanduser, dirname, realpath
from kmd_ntx_api.logger import logger
from kmd_ntx_api.memcached import MEMCACHE


HOME = expanduser('~')
SCRIPT_PATH = dirname(realpath(sys.argv[0]))
CACHE_PATH = f"{SCRIPT_PATH}/cache"
os.makedirs(CACHE_PATH, exist_ok=True)


def get_from_memcache(key, path=None, url=None, expire=600):
    # logger.cached(f"Getting {key} from cache...")
    key = key.lower()
    data = MEMCACHE.get(key)
    if data is None or len(data) == 0:
        if path is None:
            path = f"{CACHE_PATH}/{key}.json"
        data = get_cache_file(path)
        if data is None or len(data) == 0:
            data = refresh_cache(path, url, force=True, expire=expire)
        # logger.cached(f"Returning {key} from {path}")
    else:
        # logger.cached(f"Returning {key} from memcache")
        pass
    return data


def get_cache_file(file):
    if not os.path.exists(file):
        logger.warning(f"Failed to get {file} from cache")
        return None
    with open(file, "r") as f:
        return json.load(f)


def refresh_cache(path=None, url=None, data=None, force=False, key=None, expire=86400):
    '''Only used for notary_seasons / seasons_info at the moment'''
    if path is None and key is not None:
        key = key.lower()
        path = f"{CACHE_PATH}/{key}.json"

    if path is not None:    
        if not os.path.exists(path):
            data = update_cache_file(path, url, data)    
        else:
            mtime = os.path.getmtime(path)
            if int(time.time()) - mtime > expire or force:
                data = update_cache_file(path, url, data)

    if key is not None:
        key = key.lower()
        if data is not None:
            if len(data) > 0:
                MEMCACHE.set(key, data, expire)        
    return data


def update_cache_file(file, url=None, data=None):
    try:
        if url and data is not None:
            data = requests.get(url).json()
        if isinstance(data, dict):
            if "results" in data:
                data = data["results"]
        if data is not None:
            if len(data) > 0:
                with open(file, "w+") as f:
                    json.dump(data, f, indent=4)
        return data
    except Exception as e:
        logger.warning(f"Failed to update {file} from {url}: {e}")
        return None


# Activation commands
ACTIVATION_COMMANDS_URL = "http://127.0.0.1:8762/api/atomicdex/activation_commands/"
ACTIVATION_COMMANDS_PATH = f"{CACHE_PATH}/activation_commands.json"
def activation_commands_cache():
    return get_from_memcache(
        "activation_commands_cache",
        ACTIVATION_COMMANDS_PATH,
        ACTIVATION_COMMANDS_URL
    )


# Base58 Params
B58_PARAMS_URL = "http://127.0.0.1:8762/api/info/base_58/"
B58_PARAMS_PATH = f"{CACHE_PATH}/b58_params.json"
def b58_params_cache():
    return get_from_memcache("b58_params_cache", B58_PARAMS_PATH, B58_PARAMS_URL)


# Unified coins config
COINS_CONFIG_URL = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/utils/coins_config.json"
COINS_CONFIG_PATH = f"{CACHE_PATH}/coins_config.json"
def coins_config_cache():
    return get_from_memcache("coins_config_cache", COINS_CONFIG_PATH, COINS_CONFIG_URL)


# Coin icons
# TODO: we should have these local, not hosted in github
COIN_ICONS_URL = f"http://127.0.0.1:8762/api/info/coin_icons"
COIN_ICONS_PATH = f"{CACHE_PATH}/coins_icons.json"
def coin_icons_cache():
    return get_from_memcache("coin_icons_cache", COIN_ICONS_PATH, COIN_ICONS_URL)


# Coins info
COIN_INFO_URL = f"http://127.0.0.1:8762/api/info/coin"
COIN_INFO_PATH = f"{CACHE_PATH}/coins_info.json"
def coins_info_cache():
    return get_from_memcache("coins_info_cache", COIN_ICONS_PATH, COIN_ICONS_URL)


# Links to ecosystem sites
ECOSYSTEM_LINKS_URL = "https://raw.githubusercontent.com/gcharang/data/master/info/ecosystem.json"
ECOSYSTEM_LINKS_PATH = f"{CACHE_PATH}/ecosystem.json"
def ecosystem_links_cache():
    return get_from_memcache("ecosystem_links_cache", ECOSYSTEM_LINKS_PATH, ECOSYSTEM_LINKS_URL)


# Electrum Status
ELECTRUM_STATUS_URL = "https://electrum-status.dragonhound.info/api/v1/electrums_status"
ELECTRUM_STATUS_PATH = f"{CACHE_PATH}/electrum_status.json"
def get_electrum_status_cache():
    return get_from_memcache(
        "get_electrum_status_cache",
        ELECTRUM_STATUS_PATH,
        ELECTRUM_STATUS_URL
    )


# Block Explorers
EXPLORERS_URL = "http://127.0.0.1:8762/api/info/explorers/"
EXPLORERS_PATH = f"{CACHE_PATH}/explorers.json"
def explorers_cache():
    return get_from_memcache("explorers_cache", EXPLORERS_PATH, EXPLORERS_URL)


# Launch Params
LAUNCH_PARAMS_URL = "http://127.0.0.1:8762/api/info/launch_params/"
LAUNCH_PARAMS_PATH = f"{CACHE_PATH}/launch_params.json"
def launch_params_cache():
    return get_from_memcache("launch_params_cache", LAUNCH_PARAMS_PATH, LAUNCH_PARAMS_URL)


# Notary Icons
NOTARY_ICONS_URL = f"http://127.0.0.1:8762/api/info/notary_icons/"
NOTARY_ICONS_PATH = f"{CACHE_PATH}/notary_icons.json"
def notary_icons_cache():
    return get_from_memcache("notary_icons_cache", NOTARY_ICONS_PATH, NOTARY_ICONS_URL)


# Seed node version epochs
VERSION_TIMESPANS_URL = "https://raw.githubusercontent.com/KomodoPlatform/dPoW/dev/doc/seed_version_epochs.json"
VERSION_TIMESPANS_PATH = f"{CACHE_PATH}/version_timespans.json"
def version_timespans_cache():
    return get_from_memcache(
        "version_timespans_cache",
        VERSION_TIMESPANS_PATH,
        VERSION_TIMESPANS_URL
    )

# Navigation
NAVIGATION_PATH = f"{CACHE_PATH}/navigation.json"
def navigation_cache():
    return get_from_memcache("navigation", NAVIGATION_PATH)


# Notary Pubkeys
NOTARY_PUBKEYS_PATH = f"{CACHE_PATH}/notary_pubkeys.json"
def notary_pubkeys_cache():
    return get_from_memcache("notary_pubkeys", NOTARY_PUBKEYS_PATH)


# Notary Seasons
NOTARY_SEASONS_PATH = f"{CACHE_PATH}/notary_seasons.json"
def notary_seasons_cache():
    return get_from_memcache("notary_seasons", NOTARY_SEASONS_PATH)


# Seasons Info
SEASONS_INFO_PATH = f"{CACHE_PATH}/seasons_info.json"
def seasons_info_cache():
    return get_from_memcache("seasons_info", SEASONS_INFO_PATH)
