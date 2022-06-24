#!/usr/bin/env python3
import sys
import time
import json
import requests

import lib_urls as urls
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


OTHER_PREFIXES = {
    "MIL": {
        "p2shtype": 196,
        "pubtype": 50,
        "wiftype": 239
    }
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
    ],
    "VOTE2022_Testnet": [
        "BLUR",
        "LABS",
    ]
}


VALID_SERVERS = ["Main", "Third_Party", "KMD", "BTC", "LTC"]


NEXT_SEASON_COINS = {
    "Season_6": {
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
            "MGW",
            "MORTY",
            "MSHARK",
            "NINJA",
            "PANGEA",
            "PIRATE",
            "REVS",
            "RICK",
            "SUPERNET",
            "THC"
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
}


EXCLUDE_DECODE_OPRET_COINS = ['D']


EXCLUDED_SERVERS = ["Unofficial"]
EXCLUDED_SEASONS = ["Season_1", "Season_2", "Season_3", "Unofficial", "Season_4", "Season_5_Testnet", "VOTE2022_Testnet"]


RETIRED_DPOW_COINS = ["HUSH3", "GLEEC-OLD", "AXO", "BTCH", "COQUICASH", "OOT"]


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
        "notaries": [],
        "coins": [],
        "servers": {}
    },
    "Season_5": {
        "start_block": 2437000,
        "end_block": 2893460,
        "post_season_end_block": 3436999,
        "start_time": 1623682800,
        "end_time": 1651622400,
        "post_season_end_time": 1656077852,
        "notaries": [],
        "coins": [],
        "servers": {}
    },
    "Season_6": {
        "start_block": 2963330,
        "end_block": 4437000,
        "start_time": 1656077853,
        "end_time": 2773682800,
        "notaries": [],
        "coins": [],
        "servers": {}
    },
    "VOTE2022_Testnet": {
        "start_block": 2903777,
        "end_block": 2923160,
        "start_time": 1651622400,
        "end_time": 1653436800,
        "notaries": [],
        "coins": ["RICK", "MORTY"],
        "servers": {
            "Main": {
                "coins": ["RICK", "MORTY"],
                "addresses": {
                    "RICK": {},
                    "MORTY": {}
                },
                "epochs": {
                    "Epoch_0": {
                        "start_event": "testnet start",
                        "end_event": "testnet end",
                        "start_block": 2903777,
                        "end_block": 2923160,
                        "start_time": 1651622400,
                        "end_time": 1653436800,
                        "coins": ["RICK", "MORTY"]
                    }
                }
            }                        
        }    
    }
}

for _server in NEXT_SEASON_COINS["Season_6"]:
    SEASONS_INFO["Season_6"]["coins"] += NEXT_SEASON_COINS["Season_6"][_server]
    SEASONS_INFO["Season_6"]["servers"].update({
        _server: {
            "epochs": {
                "Epoch_0": {
                    "start_event": "Season start",
                    "end_event": "Season end",
                    "start_block": 2963330,
                    "end_block": 4437000,
                    "start_time": 1656077853,
                    "end_time": 2773682800,
                    "coins": NEXT_SEASON_COINS["Season_6"][_server]
                }
            },
            "coins": NEXT_SEASON_COINS["Season_6"][_server],
            "addresses": {}
        }
    })

    for coin in NEXT_SEASON_COINS["Season_6"][_server]:
        SEASONS_INFO["Season_6"]["servers"][_server]["addresses"].update({
            coin: {}
        })


SCORING_EPOCHS_REPO_DATA = requests.get(urls.get_scoring_epochs_repo_url()).json()
for _season in SCORING_EPOCHS_REPO_DATA:
    _servers = list(SCORING_EPOCHS_REPO_DATA[_season]["Servers"].keys())[:]
    for _server in _servers:

        if _server == "dPoW-Mainnet":
            SCORING_EPOCHS_REPO_DATA[_season]["Servers"].update({
                "Main": SCORING_EPOCHS_REPO_DATA[_season]["Servers"]["dPoW-Mainnet"]
            })
            del SCORING_EPOCHS_REPO_DATA[_season]["Servers"]["dPoW-Mainnet"]

        elif _server == "dPoW-3P":
            SCORING_EPOCHS_REPO_DATA[_season]["Servers"].update({
                "Third_Party": SCORING_EPOCHS_REPO_DATA[_season]["Servers"]["dPoW-3P"]
            })
            del SCORING_EPOCHS_REPO_DATA[_season]["Servers"]["dPoW-3P"]

    if SCORING_EPOCHS_REPO_DATA[_season]["season_end"] > SEASONS_INFO[_season]["end_time"]:
        SCORING_EPOCHS_REPO_DATA[_season]["season_end"] = SEASONS_INFO[_season]["end_time"]

def calc_epoch_score(server, num_coins):
    if num_coins == 0:
        return 0
    if server == "Main":
        return round(0.8698/num_coins, 8)
    elif server == "Third_Party":
        return round(0.0977/num_coins, 8)
    elif server == "KMD":
        return 0.0325
    elif server == "Testnet":
        return 1
    else:
        return 0


def get_season_start_end(season):
    start_time = SEASONS_INFO[season]["start_time"]
    end_time = SEASONS_INFO[season]["end_time"]
    if 'post_season_end_time' in SEASONS_INFO[season]:
        end_time = SEASONS_INFO[season]["post_season_end_time"]
    return start_time, end_time


# Get epoch data from local
def populate_epochs():
    epoch_dict = {}
    epochs_data = requests.get(urls.get_season_scoring_epochs_url()).json()["results"]
    for item in epochs_data:
        _season = item["season"]
        _server = item["server"]
        _epoch = item["epoch"]
        _coins = item["epoch_coins"]

        if item["season"] not in epochs_data:
            epoch_dict.update({_season: {}})

        if item["server"] not in epoch_dict[_season]:
            epoch_dict[_season].update({_server: {}})

        epoch_dict[_season][_server].update({
            _epoch: {
                "coins": _coins,
                "epoch_start": item["epoch_start"],
                "epoch_end": item["epoch_end"],
                "start_event": item["start_event"],
                "end_event": item["end_event"],
                "num_epoch_coins": len(_coins),
                "score_per_ntx": item["score_per_ntx"]
            }
        })
    return epoch_dict

NOW = time.time()

EPOCHS = populate_epochs()
print("Collected epochs data...")

DPOW_COINS_ACTIVE = requests.get(urls.get_dpow_active_coins_url()).json()["results"]

# Get current dpow coins from repo
for _season in SEASONS_INFO:
    if _season.find("Testnet") == -1:
        start_time, end_time = get_season_start_end(_season)

        if NOW >= start_time and NOW <= end_time:
            CURRENT_SEASON = _season
            CURRENT_DPOW_COINS = {_season: {}}

            for _coin in DPOW_COINS_ACTIVE:
                if DPOW_COINS_ACTIVE[_coin]["dpow"]["server"] not in CURRENT_DPOW_COINS[_season]:
                    CURRENT_DPOW_COINS[_season].update({
                        DPOW_COINS_ACTIVE[_coin]["dpow"]["server"]: []
                    })

                CURRENT_DPOW_COINS[_season][DPOW_COINS_ACTIVE[_coin]["dpow"]["server"]].append(_coin)

        elif SEASONS_INFO[_season]["start_time"] > NOW - 96 * 60 * 60:
            EXCLUDED_SEASONS.append(_season)

print("Collected dpow coins data...")

# Get notaries for each season
for _season in SEASONS_INFO:
    if _season in NOTARY_PUBKEYS:
        SEASONS_INFO[_season]["notaries"] = list(NOTARY_PUBKEYS[_season]["Main"].keys())
        SEASONS_INFO[_season]["notaries"].sort()

print("Collected notaries data...")

# For new seasons, will prepopulate from dPoW repo
for _season in SEASONS_INFO:
    if NOW - SEASONS_INFO[_season]["start_time"] < 48 * 60 * 60:
        print("Using DPOW repo to populate season early")

        for _coin in DPOW_COINS_ACTIVE:
            _epoch = "Epoch_0"
            SEASONS_INFO[_season]["coins"].append(_coin)

            if "server" in DPOW_COINS_ACTIVE[_coin]:
                _server = DPOW_COINS_ACTIVE[_coin]["server"]
                if _coin in ["KMD", "LTC", "BTC"]:
                    SEASONS_INFO[_season]["servers"].update({
                        _coin: {
                            "coins": [_coin],
                            "addresses": {_coin: {}},
                            "epochs": {
                                _coin: {
                                    "coins": [_coin],
                                    "start_time": SEASONS_INFO[_season]["start_time"],
                                    "end_time": SEASONS_INFO[_season]["end_time"],
                                    "start_event": ["Season start"],
                                    "end_event": ["Season end"]
                                }
                            }
                        }
                    })
                if _server not in SEASONS_INFO[_season]["servers"]:
                    SEASONS_INFO[_season]["servers"].update({
                        _server: {
                            "coins": [],
                            "addresses": {},
                            "epochs": {}
                        }
                    })

                if _epoch not in SEASONS_INFO[_season]["servers"][_server]["epochs"]:
                    SEASONS_INFO[_season]["servers"][_server]["epochs"].update({
                        _epoch: {"coins":[]}
                    })

                SEASONS_INFO[_season]["servers"][server]["addresses"].update({_coin:{}})

                if _server in ["Main", "Third_Party"] and _coin not in ["KMD", "LTC", "BTC"]:
                    SEASONS_INFO[_season]["servers"][_server]["coins"].append(_coin)
                    SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["coins"].append(_coin)

                SEASONS_INFO[_season]["servers"][_server]["coins"].sort()
                SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["coins"].sort()
        SEASONS_INFO[_season]["coins"].sort()

    else:
        _servers = ["Main", "Third_Party", "KMD", "BTC", "LTC"]
        for _server in _servers:

            # Get coins from scoring epochs data
            server_epoch_coins = []
            if _season in EPOCHS:
                if _server in EPOCHS[_season]:
                    for _epoch in EPOCHS[_season][_server]:
                        server_epoch_coins = EPOCHS[_season][_server][_epoch]["coins"]

            # Get coins from dPoW repo
            current_dpow_coins = []
            if _season == CURRENT_SEASON:
                if _season in CURRENT_DPOW_COINS:
                    if _server in CURRENT_DPOW_COINS[_season]:
                        current_dpow_coins = CURRENT_DPOW_COINS[_season][_server]

            # Get coins from SCORING_EPOCHS_REPO_DATA
            scoring_epoch_repo_coins = []
            if _season in SCORING_EPOCHS_REPO_DATA:
                if _server in SCORING_EPOCHS_REPO_DATA[_season]["Servers"]:
                    scoring_epoch_repo_coins += list(SCORING_EPOCHS_REPO_DATA[_season]["Servers"][_server].keys())

            _coins = list(set(
                server_epoch_coins + current_dpow_coins
                + scoring_epoch_repo_coins + ["KMD", "LTC", "BTC"]
            ))
            _coins.sort()

            for _coin in _coins:
                if _season in DPOW_EXCLUDED_COINS:
                    if _coin not in DPOW_EXCLUDED_COINS[_season]:
                        if _coin == _server:
                            SEASONS_INFO[_season]["servers"].update({
                                _coin: {
                                    "coins": [_coin],
                                    "addresses": {_coin: {}},
                                    "epochs": {
                                        _coin: {
                                            "coins": [_coin],
                                            "start_time": SEASONS_INFO[_season]["start_time"],
                                            "end_time": SEASONS_INFO[_season]["end_time"],
                                            "start_event": ["Season start"],
                                            "end_event": ["Season end"]
                                        }
                                    }
                                }
                            })

                        elif _coin not in ["BTC", "KMD", "LTC"]:
                            if _server not in SEASONS_INFO[_season]["servers"]:
                                SEASONS_INFO[_season]["servers"].update({
                                    _server: {
                                        "coins": [],
                                        "addresses": {
                                            "BTC": {},
                                            "LTC": {},
                                            "KMD": {}
                                        },
                                        "epochs": {}
                                    }
                                })

                            SEASONS_INFO[_season]["servers"][_server]["coins"].append(_coin)
                            SEASONS_INFO[_season]["servers"][_server]["addresses"].update({_coin:{}})
                        SEASONS_INFO[_season]["coins"].append(_coin)

for _season in SEASONS_INFO:
    SEASONS_INFO[_season]["coins"] = list(set(SEASONS_INFO[_season]["coins"]))
    SEASONS_INFO[_season]["coins"].sort()
    for _server in SEASONS_INFO[_season]["servers"]:
            SEASONS_INFO[_season]["servers"][_server]["coins"] = list(set(SEASONS_INFO[_season]["servers"][_server]["coins"]))
            SEASONS_INFO[_season]["servers"][_server]["coins"].sort()


print("Collected season info data...")

# Get Addresses
NOTARY_BTC_ADDRESSES = {}
ALL_SEASON_NOTARY_BTC_ADDRESSES = {}

NOTARY_KMD_ADDRESSES = {}
ALL_SEASON_NOTARY_KMD_ADDRESSES = {}

NOTARY_LTC_ADDRESSES = {}
ALL_SEASON_NOTARY_LTC_ADDRESSES = {}

for _season in SEASONS_INFO:
    for _coin in ["KMD", "BTC", "LTC"]:

        if _season not in NOTARY_BTC_ADDRESSES:
            NOTARY_BTC_ADDRESSES.update({_season: {}})

        if _season not in NOTARY_KMD_ADDRESSES:
            NOTARY_KMD_ADDRESSES.update({_season: {}})

        if _season not in NOTARY_LTC_ADDRESSES:
            NOTARY_LTC_ADDRESSES.update({_season: {}})

        for _server in NOTARY_PUBKEYS[_season]:
            for _notary in SEASONS_INFO[_season]["notaries"]:
                pubkey = NOTARY_PUBKEYS[_season][_server][_notary]
                address = get_addr_from_pubkey(_coin, pubkey)

                if _coin == "BTC":
                    NOTARY_BTC_ADDRESSES[_season].update({address: _notary})
                    ALL_SEASON_NOTARY_BTC_ADDRESSES.update({address: _notary})

                if _coin == "KMD":
                    NOTARY_KMD_ADDRESSES[_season].update({address: _notary})
                    ALL_SEASON_NOTARY_KMD_ADDRESSES.update({address: _notary})
                
                if _coin == "LTC":
                    NOTARY_LTC_ADDRESSES[_season].update({address: _notary})
                    ALL_SEASON_NOTARY_LTC_ADDRESSES.update({address: _notary})


                if _server not in SEASONS_INFO[_season]["servers"]:
                    SEASONS_INFO[_season]["servers"].update({
                        _server: {
                            "coins": [],
                            "epochs": [],
                            "addresses": {}
                        }
                    })

                if _coin not in SEASONS_INFO[_season]["servers"][_server]["addresses"]:
                    SEASONS_INFO[_season]["servers"][_server]["addresses"].update({
                        _coin: {}
                    })

                SEASONS_INFO[_season]["servers"][_server]["addresses"][_coin].update({
                    address: _notary
                })

                    
                if _coin not in SEASONS_INFO[_season]["servers"]:
                    SEASONS_INFO[_season]["servers"].update({
                        _coin: {
                            "coins": [],
                            "epochs": [],
                            "addresses": {}
                        }
                    })
                    
                if _coin not in SEASONS_INFO[_season]["servers"][_coin]["addresses"]:
                    SEASONS_INFO[_season]["servers"][_coin]["addresses"].update({
                        _coin: {}
                    })

                SEASONS_INFO[_season]["servers"][_coin]["addresses"][_coin].update({
                    address: _notary
                })

    for _server in NOTARY_PUBKEYS[_season]:
        for _notary in SEASONS_INFO[_season]["notaries"]:
            pubkey = NOTARY_PUBKEYS[_season][_server][_notary]

            if _server == "Main":
                address = get_addr_from_pubkey("KMD", pubkey)
                for _coin in SEASONS_INFO[_season]["servers"][_server]["coins"]:
                    SEASONS_INFO[_season]["servers"][_server]["addresses"][_coin].update({
                        address: _notary
                    })

            if _server == "Third_Party":
                for _coin in SEASONS_INFO[_season]["servers"][_server]["coins"]:
                    address = get_addr_from_pubkey(_coin, pubkey)
                    SEASONS_INFO[_season]["servers"][_server]["addresses"][_coin].update({
                        address: _notary
                    })


print("Collected addresses data...")

# Populate season epochs info
for _season in SCORING_EPOCHS_REPO_DATA:
    for _server in SCORING_EPOCHS_REPO_DATA[_season]["Servers"]:

        epoch_times = []
        epoch_times.append(SCORING_EPOCHS_REPO_DATA[_season]["season_start"])
        epoch_times.append(SCORING_EPOCHS_REPO_DATA[_season]["season_end"])

        for _coin in SCORING_EPOCHS_REPO_DATA[_season]["Servers"][_server]:
            if "start_time" in SCORING_EPOCHS_REPO_DATA[_season]["Servers"][_server][_coin]:
                epoch_times.append(SCORING_EPOCHS_REPO_DATA[_season]["Servers"][_server][_coin]["start_time"])
            if "end_time" in SCORING_EPOCHS_REPO_DATA[_season]["Servers"][_server][_coin]:
                epoch_times.append(SCORING_EPOCHS_REPO_DATA[_season]["Servers"][_server][_coin]["end_time"])

        epoch_times = list(set(epoch_times))
        epoch_times.sort()

        for i in range(len(epoch_times)-1):
            _epoch = f"Epoch_{i}"
            epoch_start = epoch_times[i]
            epoch_end = epoch_times[i+1]
            SEASONS_INFO[_season]["servers"][_server]["epochs"].update({
                _epoch: {
                    "start_time": epoch_start,
                    "end_time": epoch_end - 1,
                    "start_event": [],
                    "end_event": [],
                    "coins": []
                }
            })

            if SCORING_EPOCHS_REPO_DATA[_season]["season_start"] == epoch_start:
                SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["start_event"].append("Season start")

            if SCORING_EPOCHS_REPO_DATA[_season]["season_end"] == epoch_end:
                SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["end_event"].append("Season end")

            for _coin in SEASONS_INFO[_season]["servers"][_server]["coins"]:
                if _season in DPOW_EXCLUDED_COINS:
                    if _coin not in DPOW_EXCLUDED_COINS[_season]:
                        if _coin in SCORING_EPOCHS_REPO_DATA[_season]["Servers"][_server]:

                            in_epoch = False
                            partial_coin_info = SCORING_EPOCHS_REPO_DATA[_season]["Servers"][_server][_coin]

                            if "start_time" in partial_coin_info and "end_time" in partial_coin_info:
                                coin_start = partial_coin_info["start_time"]
                                coin_end = partial_coin_info["end_time"]

                                if epoch_start == coin_start:
                                    SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["start_event"].append(f"{_coin} start")

                                if epoch_start == coin_end:
                                    SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["start_event"].append(f"{_coin} end")

                                if epoch_end == coin_start:
                                    SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["end_event"].append(f"{_coin} start")

                                if epoch_end == coin_end:
                                    SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["end_event"].append(f"{_coin} end")

                                if epoch_start >= coin_start and epoch_end <= coin_end:
                                    in_epoch = True

                            elif "start_time" in partial_coin_info:
                                coin_start = partial_coin_info["start_time"]

                                if epoch_start == coin_start:
                                    SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["start_event"].append(f"{_coin} start")

                                if epoch_end == coin_start:
                                    SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["end_event"].append(f"{_coin} start")

                                if epoch_start >= coin_start:
                                    in_epoch = True

                            elif "end_time" in partial_coin_info:
                                coin_end = partial_coin_info["end_time"]

                                if epoch_start == coin_end:
                                    SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["start_event"].append(f"{_coin} end")

                                if epoch_end == coin_end:
                                    SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["end_event"].append(f"{_coin} end")

                                if epoch_end <= coin_end:
                                    in_epoch = True

                            if in_epoch:
                                SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["coins"].append(_coin)

                        else:
                            SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["coins"].append(_coin)

            num_coins = len(SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["coins"])
            score_per_ntx = calc_epoch_score(_server, num_coins)

            SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch]["coins"].sort()
            SEASONS_INFO[_season]["servers"][_server]["epochs"][_epoch].update({
                "score_per_ntx": score_per_ntx,
                "num_coins": num_coins
            })


print("Collected epochs data...")

# Set season and if postseason
POSTSEASON = False
for _season in SEASONS_INFO:
    if _season.find("Testnet") == -1:
        if SEASONS_INFO[_season]["start_time"] < NOW:
            if "post_season_end_time" in SEASONS_INFO[_season]:
                if SEASONS_INFO[_season]["post_season_end_time"] > NOW:
                    POSTSEASON = True
                    SEASON = _season
            elif SEASONS_INFO[_season]["end_time"] > NOW:
                    SEASON = _season

print(f"{int(time.time()) - NOW} sec to complete dpow const")
