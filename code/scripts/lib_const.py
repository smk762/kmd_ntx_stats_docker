#!/usr/bin/env python3.12
import os
import sys
from pathlib import Path
from os.path import expanduser, dirname, realpath
import time
import requests

# Ensure project root is on PYTHONPATH so kmd_ntx_api imports work in scripts
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from const_seasons import SEASONS
from lib_dpow_const import *
from lib_db import *
from lib_rpc import *
import lib_urls as urls
from logger import logger
from kmd_ntx_api.cache_data import cached

time_now = time.time()
# How many pages back to go with verbose API responses
API_PAGE_BREAK = int(os.getenv("API_PAGE_BREAK"))


# KMD REWARDS CONSTANTS
KOMODO_ENDOFERA = 7777777
LOCKTIME_THRESHOLD = 500000000
MIN_SATOSHIS = 1000000000
ONE_MONTH_CAP_HARDFORK = 1000000
ONE_HOUR = 60
ONE_MONTH = 31 * 24 * 60
ONE_YEAR = 365 * 24 * 60
DEVISOR = 10512000


def _cached_api_results(cache_key, url, expire=3600):
    """
    Fetch results from memcache if present, otherwise hit the API and store.
    Expects API responses shaped as {"results": {...}} and returns that inner payload.
    """
    data = cached.get_data(cache_key, expire=expire)
    if isinstance(data, dict) and "results" in data:
        data = data["results"]
    if data:
        return data
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        if isinstance(payload, dict) and "results" in payload:
            payload = payload["results"]
        cached.refresh(key=cache_key, data=payload, force=True, expire=expire)
        return payload
    except Exception as e:
        logger.warning(f"[lib_const] Failed to fetch {url}: {e}")
        return {}


# Electrums & Explorers (prefer memcache to cut internal API calls)
EXPLORERS = _cached_api_results("explorers_cache", urls.get_explorers_info_url(), expire=900)
ELECTRUMS = _cached_api_results("electrums_cache", urls.get_electrums_info_url(), expire=900)
ELECTRUMS_SSL = _cached_api_results("electrums_ssl_cache", urls.get_electrums_ssl_info_url(), expire=900)
ELECTRUMS_WSS = _cached_api_results("electrums_wss_cache", urls.get_electrums_wss_info_url(), expire=900)

# Coins
COINS_INFO = _cached_api_results("coins_info_cache", urls.get_coins_info_url(), expire=86400)
KNOWN_COINS = COINS_INFO.keys()


NON_NOTARY_ADDRESSES = {
    "RRDRX84ETUUeAU2bFZr2TScYazYxziofYd": "Luxor (Mining Pool)",
    "RSXGTHQSqwcMw1vowKfEE7sQ8fAmv1tmso": "LuckPool (Mining Pool)",
    "RR7MvgQikm5Mt2wAaRMmWy1qfwAZTQ5eaV": "ZergPool (Mining Pool)",
    "RVtg94k4yjx5JznUt47fpHZkWC2wA5KqCQ": "ZPool (Mining Pool)",
    "RKA3nd9q1s9fqyBCDLMDkK3TAjTgdUxbEV": "Mining-Dutch (Mining Pool)",
    "RAE4r5zQg2jzBq6yHt3DpKppf6hFTpVW2m": "SoloPool (Mining Pool)",
    "RDPYwhSRoE5XRe15WwXQpxL4D9Y6dAhihy": "MiningFool (Mining Pool)",
    "RKLBUAQjAQSP4wybMiVWSFGvFP7nQHcEbN": "Mining-Dutch (Mining Pool)",
    "RHEx3ZVnK9u1AVroUfW3YBCEb7YLuzx775": "Tangery (Mining Pool)",
    "RH9Ti1vkrtE2RMcYCZG1f9UWeaoHPuN24K": "CoolMine (Mining Pool)",
    "RT2v445xYCHZYnQytczFqAwegP6ossURME": "k1pool (Mining Pool)",
    "RUU3qudGCMrZXUuLtcBv9JA7Kh6sqcxdTx": "ProHashing (Mining Pool)",
    "RX6gDozvqSnNeF4sQ9ut4LcBaWz31C3h64": "ProHashing (Mining Pool)",
    "RUvuwoNas63C4nKZvYeDdkJ9cYwbqDg3wR": "ProHashing (Mining Pool)",
    "RXvu9FoSSSSYw9aTP6bfcC66uk1eqvLsfB": "ProHashing (Mining Pool)"
}


# Some coins are named differently between dpow and coins repo...
TRANSLATE_COINS = {
    'COQUI': 'COQUICASH',
    'OURC': 'OUR',
    'WLC': 'WLC21',
    'GleecBTC': 'GLEEC-OLD',
    'ARRR': "PIRATE",
    'TKL':'TOKEL'
}
REVERSE_TRANSLATE_COINS = {
    'COQUICASH': 'COQUI',
    'OUR': 'OURC',
    'WLC21': 'WLC',
    'PIRATE': "ARRR",
    'TOKEL':'TKL'
}

KNOWN_NOTARIES = []
KNOWN_ADDRESSES = {}

for season in SEASONS.INFO:
    KNOWN_NOTARIES += SEASONS.INFO[season]["notaries"]
    for server in SEASONS.INFO[season]["servers"]:
        for coin in SEASONS.INFO[season]["servers"][server]["addresses"]:
            KNOWN_ADDRESSES.update(SEASONS.INFO[season]["servers"][server]["addresses"][coin])

KNOWN_ADDRESSES.update(NON_NOTARY_ADDRESSES)
KNOWN_NOTARIES = list(set(KNOWN_NOTARIES))
KNOWN_NOTARIES.sort()

CLEAN_UP = False

HOME = expanduser('~')
SCRIPT_PATH = dirname(realpath(sys.argv[0]))
COINS_CONFIG_URL = "https://raw.githubusercontent.com/gleecbtc/coins/master/utils/coins_config.json"
COINS_CONFIG_PATH = f"{SCRIPT_PATH}/coins_config.json"

logger.info(f"{int(time.time()) - time_now} sec to complete const")