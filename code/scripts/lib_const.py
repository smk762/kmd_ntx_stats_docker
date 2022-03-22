#!/usr/bin/env python3
import time
import requests
import logging
import logging.handlers

import alerts
from lib_urls import *
from lib_dpow_const import *
from lib_db import CONN, CURSOR
from lib_crypto import COIN_PARAMS, get_addr_from_pubkey
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



# set to IP or domain to allow for external imports of data to avoid API limits

# How many pages back to go with verbose API responses
API_PAGE_BREAK = int(os.getenv("API_PAGE_BREAK"))

# Notarisation Addresses
NTX_ADDR = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'
BTC_NTX_ADDR = '1P3rU1Nk1pmc2BiWC8dEy9bZa1ZbMp5jfg'
LTC_NTX_ADDR = 'LhGojDga6V1fGzQfNGcYFAfKnDvsWeuAsP'

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


# Coins categorised
OTHER_COINS = []
ANTARA_COINS = []
THIRD_PARTY_COINS = []

COINS_INFO = requests.get(get_coins_info_url()).json()['results']
KNOWN_COINS = COINS_INFO.keys()
ELECTRUMS = requests.get(get_electrums_info_url()).json()['results']


now = time.time()
for s in SEASONS_INFO:
    if now > SEASONS_INFO[s]["start_time"] and now < SEASONS_INFO[s]["end_time"]:
        season = s
        break

ANTARA_COINS = requests.get(get_dpow_server_coins_url(season, 'Main')).json()["results"]
THIRD_PARTY_COINS = requests.get(get_dpow_server_coins_url(season, 'Third_Party')).json()["results"]

ALL_ANTARA_COINS = ANTARA_COINS + RETIRED_SMARTCHAINS


# Defines BASE_58 coin parameters
for coin in ALL_ANTARA_COINS:
    COIN_PARAMS.update({coin: COIN_PARAMS["KMD"]})

for coin in THIRD_PARTY_COINS:
    if coin in COIN_PARAMS:
        COIN_PARAMS.update({coin: COIN_PARAMS[coin]})
    else:
        print(alerts.send_telegram(f"{__name__}: {coin} doesnt have params defined!"))


# BTC specific addresses. TODO: This could be reduced / merged.
NOTARIES = {}

for season in SEASONS_INFO:
    if season in NOTARY_PUBKEYS:
        NOTARIES.update({season: []})
        NOTARIES[season] = NOTARY_PUBKEYS[season].keys()

NN_BTC_ADDRESSES_DICT = {}
NOTARY_BTC_ADDRESSES = {}
ALL_SEASON_NN_BTC_ADDRESSES_DICT = {}
ALL_SEASON_NOTARY_BTC_ADDRESSES = []

for season in SEASONS_INFO:
    NN_BTC_ADDRESSES_DICT.update({season: {}})
    try:
        addresses = requests.get(get_source_addresses_url(season, None, "BTC")).json()
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
        addresses = requests.get(get_source_addresses_url(season, "Main", "LTC")).json()
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
    if season in NOTARY_PUBKEYS:
        notaries = list(NOTARY_PUBKEYS[season].keys())
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

for season in SEASONS_INFO:
    if season in NOTARY_PUBKEYS:
        notaries = list(NOTARY_PUBKEYS[season].keys())
        notaries.sort()
        for notary in notaries:
            if season.find("Season_3") != -1:
                SEASONS_INFO["Season_3"]['notaries'].append(notary)
            elif season.find("Season_4") != -1:
                SEASONS_INFO["Season_4"]['notaries'].append(notary)
            elif season.find("Season_5") != -1:
                SEASONS_INFO["Season_5"]['notaries'].append(notary)
            elif season.find("Season_6") != -1:
                SEASONS_INFO["Season_6"]['notaries'].append(notary)
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


KNOWN_ADDRESSES.update(NON_NOTARY_ADDRESSES)
KNOWN_NOTARIES = list(set(KNOWN_NOTARIES))
KNOWN_NOTARIES.sort()

CLEAN_UP = False
