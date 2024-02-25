#!/usr/bin/env python3
import os
import sys
from os.path import expanduser, dirname, realpath
import time
import requests
import logging
import logging.handlers

from lib_dpow_const import *
from lib_db import *
from lib_rpc import *


# Default Logger
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

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


# Electrums & Explorers
EXPLORERS = requests.get(lib_urls.get_explorers_info_url()).json()['results']
ELECTRUMS = requests.get(lib_urls.get_electrums_info_url()).json()['results']
ELECTRUMS_SSL = requests.get(lib_urls.get_electrums_ssl_info_url()).json()['results']
ELECTRUMS_WSS = requests.get(lib_urls.get_electrums_wss_info_url()).json()['results']


# Coins
COINS_INFO = requests.get(lib_urls.get_coins_info_url()).json()['results']
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
    'GLEEC-OLD': 'GleecBTC',
    'PIRATE': "ARRR",
    'TOKEL':'TKL'
}

KNOWN_NOTARIES = []
KNOWN_ADDRESSES = {}

for season in SEASONS_INFO:
    KNOWN_NOTARIES += SEASONS_INFO[season]["notaries"]
    for server in SEASONS_INFO[season]["servers"]:
        for coin in SEASONS_INFO[season]["servers"][server]["addresses"]:
            KNOWN_ADDRESSES.update(SEASONS_INFO[season]["servers"][server]["addresses"][coin])

KNOWN_ADDRESSES.update(NON_NOTARY_ADDRESSES)
KNOWN_NOTARIES = list(set(KNOWN_NOTARIES))
KNOWN_NOTARIES.sort()

CLEAN_UP = False

HOME = expanduser('~')
SCRIPT_PATH = dirname(realpath(sys.argv[0]))
COINS_CONFIG_URL = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/utils/coins_config.json"
COINS_CONFIG_PATH = f"{SCRIPT_PATH}/coins_config.json"

print(f"{int(time.time()) - NOW} sec to complete const")