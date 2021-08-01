import os
import time
import requests
import logging
import logging.handlers
from dotenv import load_dotenv

import alerts
from lib_dpow_const import *
from lib_db import CONN, CURSOR
from base_58 import COIN_PARAMS, get_addr_from_pubkey
from lib_rpc import def_credentials
from notary_pubkeys import NOTARY_PUBKEYS
from s5_candidates import VOTE2021_ADDRESSES_DICT

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ENV VARS
load_dotenv()

# set this to False in .env when originally populating the table, or rescanning
SKIP_PAST_SEASONS = (os.getenv("SKIP_PAST_SEASONS") == 'True')
# set this to True in .env to quickly update tables with most recent data
SKIP_UNTIL_YESTERDAY = (os.getenv("SKIP_UNTIL_YESTERDAY") == 'True')
# set to IP or domain to allow for external imports of data to avoid API limits
OTHER_SERVER = os.getenv("OTHER_SERVER")
THIS_SERVER = os.getenv("THIS_SERVER")  # IP / domain of the local server
# How many pages back to go with verbose API responses
API_PAGE_BREAK = int(os.getenv("API_PAGE_BREAK"))

if time.time() > 1592146800:
    SEASON = "Season_4"
if time.time() > 1623682800:
    SEASON = "Season_5"


# Notarisation Addresses
NTX_ADDR = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'
BTC_NTX_ADDR = '1P3rU1Nk1pmc2BiWC8dEy9bZa1ZbMp5jfg'
LTC_NTX_ADDR = 'LhGojDga6V1fGzQfNGcYFAfKnDvsWeuAsP'

# KMD RPC Proxy
RPC = {}
RPC["KMD"] = def_credentials("KMD")
RPC["VOTE2021"] = def_credentials("VOTE2021")
noMoM = ['CHIPS', 'GAME', 'EMC2', 'AYA', 'GLEEC-OLD']

# KMD REWARDS CONSTANTS
KOMODO_ENDOFERA = 7777777
LOCKTIME_THRESHOLD = 500000000
MIN_SATOSHIS = 1000000000
ONE_MONTH_CAP_HARDFORK = 1000000
ONE_HOUR = 60
ONE_MONTH = 31 * 24 * 60
ONE_YEAR = 365 * 24 * 60
DEVISOR = 10512000

# Some coins are named differently between dpow and coins repo...
TRANSLATE_COINS = {'COQUI': 'COQUICASH', 'OURC': 'OUR',
                   'WLC': 'WLC21', 'GleecBTC': 'GLEEC-OLD'}

# Coins categorised
OTHER_COINS = []
ANTARA_COINS = []
THIRD_PARTY_COINS = []
RETIRED_SMARTCHAINS = ["HUSH3"]

COINS_INFO = requests.get(f'{THIS_SERVER}/api/info/coins/').json()['results']
ELECTRUMS = requests.get(f'{THIS_SERVER}/api/info/electrums/').json()['results']

SEASON = 'Season_5'

ANTARA_COINS = requests.get(f'{THIS_SERVER}/api/info/dpow_server_coins/?season={SEASON}&server=Main').json()["results"]
THIRD_PARTY_COINS = requests.get(f'{THIS_SERVER}/api/info/dpow_server_coins/?season={SEASON}&server=Third_Party').json()["results"]

ALL_COINS = ANTARA_COINS + THIRD_PARTY_COINS + ['BTC', 'KMD', 'LTC']
ALL_ANTARA_COINS = ANTARA_COINS + \
    RETIRED_SMARTCHAINS  # add retired smartchains here


# Defines BASE_58 coin parameters
for coin in ALL_ANTARA_COINS:
    COIN_PARAMS.update({coin: COIN_PARAMS["KMD"]})

for coin in THIRD_PARTY_COINS:
    if coin in COIN_PARAMS:
        COIN_PARAMS.update({coin: COIN_PARAMS[coin]})
    else:
        print(alerts.send_telegram(f"{__name__}: {coin} doesnt have params defined!"))


# set at post season to use "post_season_end_time" for aggreagates (e.g. mining)
POSTSEASON = True

# BTC specific addresses. TODO: This could be reduced / merged.
NOTARIES = {}
ALL_SEASON_NOTARIES = []


for season in SEASONS_INFO:
    NOTARIES.update({season: []})
    try:
        addresses = requests.get(f"{THIS_SERVER}/api/source/addresses/?chain=KMD&season={season}").json()
        for item in addresses['results']:
            NOTARIES[season].append(item["notary"])
            ALL_SEASON_NOTARIES.append(item["notary"])
    except Exception as e:
        logger.info(f"Addresses API might be down! {e}")
ALL_SEASON_NOTARIES = list(set(ALL_SEASON_NOTARIES))

NN_BTC_ADDRESSES_DICT = {}
NOTARY_BTC_ADDRESSES = {}
ALL_SEASON_NN_BTC_ADDRESSES_DICT = {}
ALL_SEASON_NOTARY_BTC_ADDRESSES = []

for season in SEASONS_INFO:
    NN_BTC_ADDRESSES_DICT.update({season: {}})
    try:
        addresses = requests.get(f"{THIS_SERVER}/api/table/addresses/?chain=BTC&season={season}").json()
        for item in addresses['results']:
            ALL_SEASON_NOTARY_BTC_ADDRESSES.append(item["address"])
            ALL_SEASON_NN_BTC_ADDRESSES_DICT.update(
                {item["address"]: item["notary"]})
            NN_BTC_ADDRESSES_DICT[season].update(
                {item["address"]: item["notary"]})
    except Exception as e:
        logger.error(e)
        logger.info("Addresses API might be down!")
    NOTARY_BTC_ADDRESSES.update(
        {season: list(NN_BTC_ADDRESSES_DICT[season].keys())})

ALL_SEASON_NOTARY_BTC_ADDRESSES = list(set(ALL_SEASON_NOTARY_BTC_ADDRESSES))

NN_LTC_ADDRESSES_DICT = {}
NOTARY_LTC_ADDRESSES = {}
ALL_SEASON_NN_LTC_ADDRESSES_DICT = {}
ALL_SEASON_NOTARY_LTC_ADDRESSES = []

for season in SEASONS_INFO:
    NN_LTC_ADDRESSES_DICT.update({season: {}})
    try:
        addresses = requests.get(f"{THIS_SERVER}/api/table/addresses/?chain=LTC&season={season}").json()
        for item in addresses['results']:
            ALL_SEASON_NOTARY_LTC_ADDRESSES.append(item["address"])
            ALL_SEASON_NN_LTC_ADDRESSES_DICT.update(
                {item["address"]: item["notary"]})
            NN_LTC_ADDRESSES_DICT[season].update(
                {item["address"]: item["notary"]})
    except Exception as e:
        logger.error(e)
        logger.info("Addresses API might be down!")
    NOTARY_LTC_ADDRESSES.update(
        {season: list(NN_LTC_ADDRESSES_DICT[season].keys())})

ALL_SEASON_NOTARY_LTC_ADDRESSES = list(set(ALL_SEASON_NOTARY_LTC_ADDRESSES))

# shows addresses for all coins for each notary node, by season.
NOTARY_ADDRESSES_DICT = {}

for season in NOTARY_PUBKEYS:
    NOTARY_ADDRESSES_DICT.update({season: {}})
    notaries = list(NOTARY_PUBKEYS[season].keys())
    notaries.sort()
    for notary in notaries:
        if notary not in NOTARY_ADDRESSES_DICT:
            NOTARY_ADDRESSES_DICT[season].update({notary: {}})

        for coin in COIN_PARAMS:
            NOTARY_ADDRESSES_DICT[season][notary].update({
                coin: get_addr_from_pubkey(coin, NOTARY_PUBKEYS[season][notary])
            })


# lists all season, name, address and id info for each notary
NOTARY_INFO = {}

# detailed address info categories by season. showing notary name, id and pubkey
ADDRESS_INFO = {}

for season in NOTARY_PUBKEYS:
    notary_id = 0
    ADDRESS_INFO.update({season: {}})
    notaries = list(NOTARY_PUBKEYS[season].keys())
    notaries.sort()
    for notary in notaries:
        if notary not in NOTARY_INFO:
            NOTARY_INFO.update({
                notary: {
                    "Notary_ids": [],
                    "Seasons": [],
                    "Addresses": [],
                    "Pubkeys": []
                }})
        addr = get_addr_from_pubkey("KMD", NOTARY_PUBKEYS[season][notary])
        ADDRESS_INFO[season].update({
            addr: {
                "Notary": notary,
                "Notary_id": notary_id,
                "Pubkey": NOTARY_PUBKEYS[season][notary]
            }})
        NOTARY_INFO[notary]['Notary_ids'].append(notary_id)
        NOTARY_INFO[notary]['Seasons'].append(season)
        NOTARY_INFO[notary]['Addresses'].append(addr)
        NOTARY_INFO[notary]['Pubkeys'].append(NOTARY_PUBKEYS[season][notary])
        notary_id += 1

for season in NOTARY_PUBKEYS:
    if season.find("Third_Party") != -1:
        notaries = list(NOTARY_PUBKEYS[season].keys())
        notaries.sort()
        for notary in notaries:
            if season.find("Season_3") != -1:
                SEASONS_INFO["Season_3"]['notaries'].append(notary)
            elif season.find("Season_4") != -1:
                SEASONS_INFO["Season_4"]['notaries'].append(notary)
            elif season.find("Season_5") != -1:
                SEASONS_INFO["Season_5"]['notaries'].append(notary)
            else:
                SEASONS_INFO[season]['notaries'].append(notary)


# SPECIAL CASE BTC TXIDS
S4_INIT_BTC_FUNDING_TX = "13fee57ec60ef4ca42dbed5eb77d576bf7545e7042b334b27afdc33051635611"

KNOWN_NOTARIES = []
KNOWN_ADDRESSES = {}
for season in NOTARY_ADDRESSES_DICT:
    for notary in NOTARY_ADDRESSES_DICT[season]:
        KNOWN_NOTARIES.append(notary)
        for coin in NOTARY_ADDRESSES_DICT[season][notary]:
            address = NOTARY_ADDRESSES_DICT[season][notary][coin]
            KNOWN_ADDRESSES.update({address: notary})

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
    "RT2v445xYCHZYnQytczFqAwegP6ossURME": "k1pool"
}

KNOWN_ADDRESSES.update(NON_NOTARY_ADDRESSES)
