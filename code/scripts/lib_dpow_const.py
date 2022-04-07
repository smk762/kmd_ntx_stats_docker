#!/usr/bin/env python3
import sys
import time
import json
import requests

from lib_urls import *
from lib_crypto import * 
from notary_pubkeys import NOTARY_PUBKEYS
from notary_candidates import CANDIDATE_ADDRESSES


# Notarisation Addresses
NTX_ADDR = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'
BTC_NTX_ADDR = '1P3rU1Nk1pmc2BiWC8dEy9bZa1ZbMp5jfg'
LTC_NTX_ADDR = 'LhGojDga6V1fGzQfNGcYFAfKnDvsWeuAsP'


# SPECIAL CASE BTC TXIDS
S4_INIT_BTC_FUNDING_TX = "13fee57ec60ef4ca42dbed5eb77d576bf7545e7042b334b27afdc33051635611"


# OP_RETURN data sometimes has extra info. Not used yet, but here for future reference
noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'GLEEC-OLD', 'AYA', 'MCL', 'VRSC']


OTHER_LAUNCH_PARAMS = {
    "BTC": "~/bitcoin/src/bitcoind",
    "SFUSD": "~/sfusd-core/src/smartusdd",
    "LTC": "~/litecoin/src/litecoind",
    "KMD": "~/komodo/src/komodod", 
    "AYA": "~/AYAv2/src/aryacoind",
    "CHIPS": "~/chips/src/chipsd",
    "MIL": "~/mil-1/src/mild",
    "EMC2": "~/einsteinium/src/einsteiniumd",
    "TOKEL": "~/tokelkomodo/src/komodod -ac_name=TOKEL -ac_supply=100000000 -ac_eras=2 -ac_cbmaturity=1 -ac_reward=100000000,4250000000 -ac_end=80640,0 -ac_decay=0,77700000 -ac_halving=0,525600 -ac_cc=555 -ac_ccenable=236,245,246,247 -ac_adaptivepow=6 -addnode=135.125.204.169 -addnode=192.99.71.125 -addnode=144.76.140.197 -addnode=135.181.92.123 ",
    "VRSC": "~/VerusCoin/src/verusd",
    "GLEEC": "~/komodo/src/komodod -ac_name=GLEEC -ac_supply=210000000 -ac_public=1 -ac_staked=100 -addnode=95.217.161.126",
    "VOTE2021": "~/komodo/src/komodod  -ac_name=VOTE2021 -ac_public=1 -ac_supply=129848152 -addnode=77.74.197.115",
    "GLEEC-OLD": "~/GleecBTC-FullNode-Win-Mac-Linux/src/gleecbtcd",
    "MCL": "~/marmara/src/komodod -ac_name=MCL -ac_supply=2000000 -ac_cc=2 -addnode=5.189.149.242 -addnode=161.97.146.150 -addnode=149.202.158.145 -addressindex=1 -spentindex=1 -ac_marmara=1 -ac_staked=75 -ac_reward=3000000000 -daemon"
}


OTHER_CONF_FILE = {
    "BTC": "~/.bitcoin/bitcoin.conf",
    "SFUSD": "~/.smartusd/smartusd.conf",
    "LTC": "~/.litecoin/litecoin.conf",
    "KMD": "~/.komodo/komodo.conf",
    "MCL": "~/.komodo/MCL/MCL.conf", 
    "MIL": "~/.mil/mil.conf", 
    "TOKEL": "~/.komodo/TOKEL/TOKEL.conf", 
    "VOTE2021": "~/.komodo/VOTE2021/VOTE2021.conf",
    "AYA": "~/.aryacoin/aryacoin.conf",
    "CHIPS": "~/.chips/chips.conf",
    "EMC2": "~/.einsteinium/einsteinium.conf",
    "VRSC": "~/.komodo/VRSC/VRSC.conf",   
    "GLEEC": "~/.komodo/GLEEC/GLEEC.conf",
    "GLEEC-OLD": "~/.gleecbtc/gleecbtc.conf",   
}


OTHER_CLI = {
    "BTC": "~/bitcoin/src/bitcoin-cli",
    "SFUSD": "~/sfusd-core/src/smartusd-cli",
    "LTC": "~/litecoin/src/litecoin-cli",
    "KMD": "~/komodo/src/komodo-cli",
    "MIL": "~/mil-1/src/mil-cli",
    "MCL": "~/komodo/src/komodo-cli -ac_name=MCL",
    "TOKEL": "~/komodo/src/komodo-cli -ac_name=TOKEL", 
    "GLEEC": "~/komodo/src/komodo-cli -ac_name=GLEEC",
    "VOTE2021": "~/komodo/src/komodo-cli -ac_name=VOTE2021",
    "AYA": "~/AYAv2/src/aryacoin-cli",
    "CHIPS": "~/chips/src/chips-cli",
    "EMC2": "~/einsteinium/src/einsteinium-cli",
    "VRSC": "~/VerusCoin/src/verus",   
    "GLEEC-OLD": "~/GleecBTC-FullNode-Win-Mac-Linux/src/gleecbtc-cli",   
}

# Rescan full season
RESCAN_SEASON = False
RESCAN_CHUNK_SIZE = 100000


DPOW_EXCLUDED_COINS = {
    "Season_1": [],
    "Season_2": [
        "TXSCLCC",
        "BEER",
        "PIZZA"
    ],
    "Season_3": [
        "TEST1",
        "TEST2",
        "TEST3",
        "TEST4",
        "TEST2FAST",
        "TEST2FAST1",
        "TEST2FAST2",
        "TEST2FAST3",
        "TEST2FAST4",
        "TEST2FAST5",
        "TEST2FAST6",
    ],
    "Season_4": [
        "BLUR",
        "ETOMIC",
        "KSB",
        "KV",
        "OUR",
        "LABS",
        "SEC",
        "ZEXO",
        "GAME",
        "TXSCLI",
        "HUF",
        "K64"
    ],
    "Season_5": [
        "AXO",
        "BTCH",
        "COQUICASH",
        "BLUR",
        "LABS",
        "BTC",
        "ARYA"
    ],
    "Season_5_Testnet": [
        "BLUR",
        "LABS",
        ],
    "Season_6": [
        "BLUR",
        "LABS",
        "BTC",
        "ARYA"
    ]
}


VALID_SERVERS = ["Main", "Third_Party", "KMD", "BTC", "LTC"]


NEXT_SEASON_COINS = {
    "LTC": ["LTC"],
    "KMD": ["KMD"],
    "Main": [
        "AXO",
        "BET",
        "BOTS",
        "BTCH",
        "CLC",
        "CCL",
        "COQUICASH",
        "CRYPTO",
        "DEX",
        "GLEEC",
        "HODL",
        "ILN",
        "JUMBLR",
        "KOIN",
        "MESH",
        "MGW",
        "MORTY",
        "MSHARK",
        "NINJA",
        "PANGEA",
        "PIRATE",
        "REVS",
        "RICK",
        "SUPERNET",
        "THC",
        "ZILLA"
    ],
    "Third_Party": [
        "AYA",
        "CHIPS",
        "EMC2",
        "MIL",
        "MCL",
        "SFUSD",
        "VRSC",
        "TOKEL"
    ]
}


EXCLUDE_DECODE_OPRET_COINS = ['D']


EXCLUDED_SERVERS = ["Unofficial"]
EXCLUDED_SEASONS = ["Season_1", "Season_2", "Season_3", "Unofficial", "Season_4", "Season_5_Testnet"]


RETIRED_DPOW_COINS = ["HUSH3", "GLEEC-OLD", "AXO", "BTCH", "COQUICASH", "OOT"]


SCORING_EPOCHS_REPO_DATA = requests.get(get_scoring_epochs_repo_url('smk762-epochs')).json()
for season in SCORING_EPOCHS_REPO_DATA:
    servers = list(SCORING_EPOCHS_REPO_DATA[season]["Servers"].keys())[:]
    for server in servers:

        if server == "dPoW-Mainnet":
            SCORING_EPOCHS_REPO_DATA[season]["Servers"].update({
                "Main": SCORING_EPOCHS_REPO_DATA[season]["Servers"]["dPoW-Mainnet"]
            })
            del SCORING_EPOCHS_REPO_DATA[season]["Servers"]["dPoW-Mainnet"]

        elif server == "dPoW-3P":
            SCORING_EPOCHS_REPO_DATA[season]["Servers"].update({
                "Third_Party": SCORING_EPOCHS_REPO_DATA[season]["Servers"]["dPoW-3P"]
            })
            del SCORING_EPOCHS_REPO_DATA[season]["Servers"]["dPoW-3P"]


SEASONS_INFO = {
    "Season_1": {
        "start_block": 1,
        "end_block": 813999,
        "start_time": 1473793441,
        "end_time": 1530921600,
        "notaries": [],
        "coins": [],
        "servers": {}
    },
    "Season_2": {
        "start_block": 814000,
        "end_block": 1443999,
        "start_time": 1530921600,
        "end_time": 1563148799,
        "notaries": [],
        "coins": [],
        "servers": {}
    },
    "Season_3": {
        "start_block": 1444000,
        "end_block": 1921999,
        "start_time": 1563148800,
        "end_time": 1592146799,
        "notaries": [],
        "coins": [],
        "servers": {}
    },
    "Season_4": {
        "start_block": 1922000,
        "end_block": 2436999,
        "start_time": 1592146800,
        "end_time": 1617364800,
        "post_season_end_time": 1623682799,
        "notaries": [],
        "coins": [],
        "servers": {}
    },
    "Season_5": {
        "start_block": 2437000,
        "end_block": 3436999,
        "start_time": 1623682800,
        "end_time": 1751328000,
        "notaries": [],
        "coins": [],
        "servers": {}
    },
    "Season_6": {
        "start_block": 3437000,
        "end_block": 4437000,
        "start_time": 1751328000,
        "end_time": 2773682800,
        "notaries": [],
        "coins": [],
        "servers": {}
    }
}
NOW = time.time()
DPOW_COINS_ACTIVE = requests.get(get_dpow_active_coins_url()).json()["results"]

for season in SEASONS_INFO:
    if NOW >= SEASONS_INFO[season]["start_time"] and NOW <= SEASONS_INFO[season]["end_time"]:
        CURRENT_SEASON = season
        CURRENT_DPOW_COINS = {season: {}}
        for coin in DPOW_COINS_ACTIVE:
            if DPOW_COINS_ACTIVE[coin]["dpow"]["server"] not in CURRENT_DPOW_COINS[season]:
                CURRENT_DPOW_COINS[season].update({
                    server: []
                })
            CURRENT_DPOW_COINS[season][server].append(coin)

    elif SEASONS_INFO[season]["start_time"] > NOW:
        EXCLUDED_SEASONS.append(season)

for season in SEASONS_INFO:
    if season in NOTARY_PUBKEYS:
        SEASONS_INFO[season]["notaries"] = list(NOTARY_PUBKEYS[season]["Main"].keys())
        SEASONS_INFO[season]["notaries"].sort()

    if NOW - SEASONS_INFO[season]["start_time"] < 48 * 60 * 60:

        for coin in DPOW_COINS_ACTIVE:
            epoch = "Epoch_0"
            SEASONS_INFO[season]["coins"].append(coin)

            if "server" in DPOW_COINS_ACTIVE[coin]:
                server = DPOW_COINS_ACTIVE[coin]["server"]
                if coin in ["KMD", "LTC", "BTC"]:
                    SEASONS_INFO[season]["servers"].update({
                        coin: {
                            "coins": [coin],
                            "addresses": {
                                coin: {}
                            },
                            "epochs": {
                                coin: {
                                    "coins": [coin],
                                    "start_time": SEASONS_INFO[season]["start_time"],
                                    "end_time": SEASONS_INFO[season]["end_time"],
                                    "start_event": [
                                        "Season start"
                                    ],
                                    "end_event": [
                                        "Season end"
                                    ]
                                }
                            }
                        }
                    })
                if server not in SEASONS_INFO[season]["servers"]:
                    SEASONS_INFO[season]["servers"].update({
                        server:{
                            "coins": [],
                            "addresses": {},
                            "epochs": {}
                        }
                    })

                if epoch not in SEASONS_INFO[season]["servers"][server]["epochs"]:
                    SEASONS_INFO[season]["servers"][server]["epochs"].update({
                        epoch: {
                            "coins":[]
                        }
                    })

                SEASONS_INFO[season]["servers"][server]["addresses"].update({coin:{}})

                if server in ["Main", "Third_Party"] and coin not in ["KMD", "LTC", "BTC"]:
                    SEASONS_INFO[season]["servers"][server]["coins"].append(coin)
                    SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["coins"].append(coin)

                SEASONS_INFO[season]["servers"][server]["coins"].sort()
                SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["coins"].sort()
        SEASONS_INFO[season]["coins"].sort()

    else:
        servers = requests.get(get_notarised_servers_url(season)).json()["results"]
        for server in servers:
            coins = requests.get(get_notarised_coins_url(season, server)).json()["results"]
            if server in SCORING_EPOCHS_REPO_DATA[season]["Servers"]:
                coins = coins + list(SCORING_EPOCHS_REPO_DATA[season]["Servers"][server].keys())
            if season == CURRENT_SEASON:
                if server in CURRENT_DPOW_COINS[season]:
                    coins += CURRENT_DPOW_COINS[season][server]
            coins = list(set(coins))
            coins.sort()
            for coin in coins + ["KMD", "LTC", "BTC"]:
                if season in DPOW_EXCLUDED_COINS:
                    if coin not in DPOW_EXCLUDED_COINS[season]:

                        if coin in ["KMD", "LTC", "BTC"]:
                            SEASONS_INFO[season]["servers"].update({
                                coin:{
                                    "coins": [coin],
                                    "addresses": {
                                        coin: {}
                                    },
                                    "epochs": {
                                        coin: {
                                            "coins": [coin],
                                            "start_time": SEASONS_INFO[season]["start_time"],
                                            "end_time": SEASONS_INFO[season]["end_time"],
                                            "start_event": [
                                                "Season start"
                                            ],
                                            "end_event": [
                                                "Season end"
                                            ]
                                        }
                                    }
                                }
                            })

                        if server not in SEASONS_INFO[season]["servers"]:
                            SEASONS_INFO[season]["servers"].update({
                                server: {
                                    "coins": [],
                                    "addresses": {},
                                    "epochs": {}
                                }
                            })

                        SEASONS_INFO[season]["coins"].append(coin)

                        if server in ["Main", "Third_Party"] and coin not in ["KMD", "LTC", "BTC"]:
                            SEASONS_INFO[season]["servers"][server]["coins"].append(coin)

                        SEASONS_INFO[season]["servers"][server]["addresses"].update({coin:{}})

                SEASONS_INFO[season]["servers"][server]["coins"] = list(set(SEASONS_INFO[season]["servers"][server]["coins"]))
                SEASONS_INFO[season]["servers"][server]["coins"].sort()

        SEASONS_INFO[season]["coins"] = list(set(SEASONS_INFO[season]["coins"]))
        SEASONS_INFO[season]["coins"].sort()

print(json.dumps(SEASONS_INFO["Season_5"], indent=4))

NOTARY_LTC_ADDRESSES = {}
ALL_SEASON_NOTARY_LTC_ADDRESSES = {}

NOTARY_BTC_ADDRESSES = {}
ALL_SEASON_NOTARY_BTC_ADDRESSES = {}

for season in SEASONS_INFO:


    if season not in NOTARY_LTC_ADDRESSES:
        NOTARY_LTC_ADDRESSES.update({season: {}})

    if season not in NOTARY_BTC_ADDRESSES:
        NOTARY_BTC_ADDRESSES.update({season: {}})

    for notary in SEASONS_INFO[season]["notaries"]:

        for server in SEASONS_INFO[season]["servers"]:

            for coin in SEASONS_INFO[season]["servers"][server]["coins"]:

                if server in ["KMD", "LTC", "BTC"]:
                    pubkey = NOTARY_PUBKEYS[season]["Main"][notary]
                    address = get_addr_from_pubkey(coin, pubkey)
                    SEASONS_INFO[season]["servers"]["Main"]["addresses"][coin].update({
                        address: notary
                    })
                    SEASONS_INFO[season]["servers"][server]["addresses"][coin].update({
                        address: notary
                    })

                    if coin == "LTC":
                        NOTARY_LTC_ADDRESSES[season].update({address: notary})
                        ALL_SEASON_NOTARY_LTC_ADDRESSES.update({address: notary})

                    if coin == "BTC":
                        NOTARY_BTC_ADDRESSES[season].update({address: notary})
                        ALL_SEASON_NOTARY_BTC_ADDRESSES.update({address: notary})

                    pubkey = NOTARY_PUBKEYS[season]["Third_Party"][notary]
                    address = get_addr_from_pubkey(coin, pubkey)

                    SEASONS_INFO[season]["servers"]["Third_Party"]["addresses"][coin].update({
                        address: notary
                    })
                    SEASONS_INFO[season]["servers"][server]["addresses"][coin].update({
                        address: notary
                    })

                else:
                    pubkey = NOTARY_PUBKEYS[season][server][notary]
                    address = get_addr_from_pubkey(coin, pubkey)
                    
                    SEASONS_INFO[season]["servers"][server]["addresses"][coin].update({
                        address: notary
                    })



for season in SCORING_EPOCHS_REPO_DATA:
    for server in SCORING_EPOCHS_REPO_DATA[season]["Servers"]:

        epoch_times = []
        epoch_times.append(SCORING_EPOCHS_REPO_DATA[season]["season_start"])
        epoch_times.append(SCORING_EPOCHS_REPO_DATA[season]["season_end"])

        for coin in SCORING_EPOCHS_REPO_DATA[season]["Servers"][server]:
            if "start_time" in SCORING_EPOCHS_REPO_DATA[season]["Servers"][server][coin]:
                epoch_times.append(SCORING_EPOCHS_REPO_DATA[season]["Servers"][server][coin]["start_time"])
            if "end_time" in SCORING_EPOCHS_REPO_DATA[season]["Servers"][server][coin]:
                epoch_times.append(SCORING_EPOCHS_REPO_DATA[season]["Servers"][server][coin]["end_time"])

        epoch_times.sort()

        for i in range(len(epoch_times)-1):
            epoch = f"Epoch_{i}"
            epoch_start = epoch_times[i]
            epoch_end = epoch_times[i+1]
            SEASONS_INFO[season]["servers"][server]["epochs"].update({
                epoch: {
                    "start_time": epoch_start,
                    "end_time": epoch_end - 1,
                    "start_event": [],
                    "end_event": [],
                    "coins": []
                }
            })

            if SCORING_EPOCHS_REPO_DATA[season]["season_start"] == epoch_start:
                SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["start_event"].append("Season start")

            if SCORING_EPOCHS_REPO_DATA[season]["season_end"] == epoch_end:
                SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["end_event"].append("Season end")


            for coin in SEASONS_INFO[season]["servers"][server]["coins"]:
                if season in DPOW_EXCLUDED_COINS:
                    if coin not in DPOW_EXCLUDED_COINS[season]:
                        if coin in SCORING_EPOCHS_REPO_DATA[season]["Servers"][server]:

                            partial_coin_info = SCORING_EPOCHS_REPO_DATA[season]["Servers"][server][coin]
                            in_epoch = False

                            if "start_time" in partial_coin_info and "end_time" in partial_coin_info:
                                coin_start = partial_coin_info["start_time"]
                                coin_end = partial_coin_info["end_time"]

                                if epoch_start == coin_start:
                                    SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["start_event"].append(f"{coin} start")

                                if epoch_start == coin_end:
                                    SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["start_event"].append(f"{coin} end")

                                if epoch_end == coin_start:
                                    SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["end_event"].append(f"{coin} start")

                                if epoch_end == coin_end:
                                    SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["end_event"].append(f"{coin} end")

                                if epoch_start >= coin_start and epoch_end <= coin_end:
                                    in_epoch = True

                            elif "start_time" in partial_coin_info:
                                coin_start = partial_coin_info["start_time"]

                                if epoch_start == coin_start:
                                    SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["start_event"].append(f"{coin} start")

                                if epoch_end == coin_start:
                                    SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["end_event"].append(f"{coin} start")

                                if epoch_start >= coin_start:
                                    in_epoch = True

                            elif "end_time" in partial_coin_info:
                                coin_end = partial_coin_info["end_time"]

                                if epoch_start == coin_end:
                                    SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["start_event"].append(f"{coin} end")

                                if epoch_end == coin_end:
                                    SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["end_event"].append(f"{coin} end")

                                if epoch_end <= coin_end:
                                    in_epoch = True

                            if in_epoch:
                                SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["coins"].append(coin)

                        else:
                            SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["coins"].append(coin)

            num_coins = len(SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["coins"])
            SEASONS_INFO[season]["servers"][server]["epochs"][epoch].update({"num_coins": num_coins})



NOW = time.time()
POSTSEASON = False

for _season in SEASONS_INFO:
    if SEASONS_INFO[_season]["start_time"] < NOW:
        if "post_season_end_time" in SEASONS_INFO[_season]:
            if SEASONS_INFO[_season]["post_season_end_time"] > NOW:
                POSTSEASON = True
                SEASON = _season
        elif SEASONS_INFO[_season]["end_time"] > NOW:
                SEASON = _season
