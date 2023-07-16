import os
import sys
import time
import json
import requests
from os.path import expanduser, dirname, realpath
from kmd_ntx_api.logger import logger


def refresh_cache_data(file, url):
    if not os.path.exists(file):
        update_cache_data(file, url)
    now = int(time.time())
    mtime = os.path.getmtime(file)
    if now - mtime > 86400: # 24 hrs
        update_cache_data(file, url)
    return get_cache_data(file)


def get_cache_data(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)


def update_cache_data(file, url):
    try:
        
        data = requests.get(url).json()
        if "results" in data:
            data = data["results"]
        with open(file, "w+") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.warning(f"Failed to {file} from {url}: {e}")



HOME = expanduser('~')
SCRIPT_PATH = dirname(realpath(sys.argv[0]))
CACHE_PATH = f"{SCRIPT_PATH}/cache"
os.makedirs(CACHE_PATH, exist_ok=True)


# Activation commands
ACTIVATION_COMMANDS_URL = "/api/atomicdex/activation_commands/"
ACTIVATION_COMMANDS_PATH = f"{CACHE_PATH}/activation_commands.json"
def activation_commands_cache():
    return refresh_cache_data(ACTIVATION_COMMANDS_PATH, ACTIVATION_COMMANDS_URL)


# Base58 Params
B58_PARAMS_URL = "/api/info/base_58/"
B58_PARAMS_PATH = f"{CACHE_PATH}/b58_params.json"
def b58_params():
    return refresh_cache_data(B58_PARAMS_PATH, B58_PARAMS_URL)


# Unified coins config
COINS_CONFIG_URL = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/utils/coins_config.json"
COINS_CONFIG_PATH = f"{CACHE_PATH}/coins_config.json"
def coins_config_cache():
    return refresh_cache_data(COINS_CONFIG_PATH, COINS_CONFIG_URL)


# Coin icons
COIN_ICONS_URL = f"/api/info/coin_icons"
COIN_ICONS_PATH = f"{CACHE_PATH}/coins_config.json"
def coins_icons():
    return refresh_cache_data(COIN_ICONS_PATH, COIN_ICONS_URL)


# Coins info
COIN_INFO_URL = f"/api/info/coin"
COIN_INFO_PATH = f"{CACHE_PATH}/coins.json"
def coins_info():
    return refresh_cache_data(COIN_ICONS_PATH, COIN_ICONS_URL)


# Links to ecosystem sites
ECOSYSTEM_LINKS_URL = "https://raw.githubusercontent.com/gcharang/data/master/info/ecosystem.json"
ECOSYSTEM_LINKS_PATH = f"{CACHE_PATH}/ecosystem.json"
def ecosystem_links():
    return refresh_cache_data(ECOSYSTEM_LINKS_PATH, ECOSYSTEM_LINKS_URL)


# Electrum Status
ELECTRUM_STATUS_URL = "https://electrum-status.dragonhound.info/api/v1/electrums_status"
ELECTRUM_STATUS_PATH = f"{CACHE_PATH}/electrum_status.json"
def get_electrum_status():
    return refresh_cache_data(ELECTRUM_STATUS_PATH, ELECTRUM_STATUS_URL)


# Block Explorers
EXPLORERS_URL = "/api/info/explorers/"
EXPLORERS_PATH = f"{CACHE_PATH}/explorers.json"
def explorers():
    return refresh_cache_data(EXPLORERS_URL, EXPLORERS_PATH)


# Launch Params
LAUNCH_PARAMS_URL = "/api/info/launch_params/"
LAUNCH_PARAMS_PATH = f"{CACHE_PATH}/launch_params.json"
def launch_params_cache():
    return refresh_cache_data(LAUNCH_PARAMS_URL, LAUNCH_PARAMS_PATH)


# Navigation
NAVIGATION_PATH = f"{CACHE_PATH}/navigation.json"
def navigation():
    return get_cache_data(NAVIGATION_PATH)


# Notary Icons
NOTARY_ICONS_URL = f"/api/info/notary_icons/"
NOTARY_ICONS_PATH = f"{CACHE_PATH}/notary_icons.json"
def notary_icons():
    return refresh_cache_data(NOTARY_ICONS_PATH, NOTARY_ICONS_URL)


# Notary Pubkeys
NOTARY_PUBKEYS_PATH = f"{CACHE_PATH}/notary_pubkeys.json"
def notary_pubkeys():
    return get_cache_data(EXPLORERS_PATH)


# Notary Pubkeys
SEASONS_PATH = f"{CACHE_PATH}/notary_seasons.json"
def notary_seasons_cache():
    return get_cache_data(SEASONS_PATH)


# Seed node version epochs
VERSION_TIMESPANS_URL = "https://raw.githubusercontent.com/KomodoPlatform/dPoW/seednode-update/doc/seed_version_epochs.json"
VERSION_TIMESPANS_PATH = f"{CACHE_PATH}/seed_version_epochs.json"
def version_timespans():
    return refresh_cache_data(VERSION_TIMESPANS_PATH, VERSION_TIMESPANS_URL)

