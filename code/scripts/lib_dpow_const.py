#!/usr/bin/env python3
import sys
import time
import json
import requests

import lib_urls as urls
from lib_crypto import * 
from notary_pubkeys import NOTARY_PUBKEYS
from notary_candidates import CANDIDATE_ADDRESSES


def get_scoring_epochs_repo_data(branch='master'):
    url = urls.get_scoring_epochs_repo_url(branch)
    repo_data = requests.get(url).json()
    for _season in repo_data:
        _servers = list(repo_data[_season]["Servers"].keys())[:]
        for _server in _servers:
            # Rename the dict keys. 
            if _server == "dPoW-Mainnet":
                repo_data[_season]["Servers"].update({
                    "Main": repo_data[_season]["Servers"]["dPoW-Mainnet"]
                })
                del repo_data[_season]["Servers"]["dPoW-Mainnet"]

            elif _server == "dPoW-3P":
                repo_data[_season]["Servers"].update({
                    "Third_Party": repo_data[_season]["Servers"]["dPoW-3P"]
                })
                del repo_data[_season]["Servers"]["dPoW-3P"]
    return repo_data


def get_dpow_active_info(seasons):
    '''Get current dpow coins from repo'''
    data = requests.get(urls.get_dpow_active_coins_url()).json()["results"]
    for season in seasons:
        if season.find("Testnet") == -1:
            start_time, end_time = get_season_start_end(season)

            if NOW >= start_time and NOW <= end_time:
                current_season = season
                current_dpow_coins = {season: {}}

                for _coin in data:
                    if data[_coin]["dpow"]["server"] not in current_dpow_coins[season]:
                        current_dpow_coins[season].update({
                            data[_coin]["dpow"]["server"]: []
                        })

                    current_dpow_coins[season][data[_coin]["dpow"]["server"]].append(_coin)

    return current_season, data, current_dpow_coins


def populate_epochs():
    epoch_dict = {}
    for season in SEASONS_INFO:
        epoch_dict.update({season: get_season_epochs(season)})
    return epoch_dict


def get_season_start_end(season):
    start_time = SEASONS_INFO[season]["start_time"]
    end_time = SEASONS_INFO[season]["end_time"]
    if 'post_season_end_time' in SEASONS_INFO[season]:
        end_time = SEASONS_INFO[season]["post_season_end_time"]
    return start_time, end_time



## 2023 Updates


def get_epoch_score(server, num_coins):
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


def get_coin_time_ranges(season):
    '''
    Gets scoring epochs data from dpow repo, then determines the epochs
    for each server and the coins valid during that epoch.
    '''
    coin_ranges = {}
    if season in SEASON_START_COINS:
        # Initialise with full season timespan
        for server in SEASON_START_COINS[season]:
            coin_ranges.update({server: {}})
            for coin in SEASON_START_COINS[season][server]:
                coin_ranges[server].update({
                    coin: {
                        "start": SEASONS_INFO[season]["start_time"],
                        "end": SEASONS_INFO[season]["end_time"]
                    }
                })

        # Refine timespan for partial season coins
        repo_data = get_scoring_epochs_repo_data()
        if season in repo_data:
            repo_data = repo_data[season]
            for server in SEASON_START_COINS[season]:
                if server in repo_data["Servers"]:
                    for coin in repo_data["Servers"][server]:
                        if coin not in coin_ranges[server]:
                            coin_ranges[server].update({
                                coin: {
                                    "start": SEASONS_INFO[season]["start_time"],
                                    "end": SEASONS_INFO[season]["end_time"]
                                }
                            })
                        if "start_time" in repo_data["Servers"][server][coin]:
                            coin_ranges[server][coin].update({"start": repo_data["Servers"][server][coin]["start_time"]})
                        if "end_time" in repo_data["Servers"][server][coin]:
                            coin_ranges[server][coin].update({"end": repo_data["Servers"][server][coin]["end_time"]})

    return coin_ranges                        


def get_epoch_time_breaks(repo_data, season, server):
    time_breaks = [SEASONS_INFO[season]["start_time"], SEASONS_INFO[season]["end_time"]]
    for coin in repo_data["Servers"][server]:
        if "start_time" in repo_data["Servers"][server][coin]:
            time_breaks.append(repo_data["Servers"][server][coin]["start_time"])
        if "end_time" in repo_data["Servers"][server][coin]:
            time_breaks.append(repo_data["Servers"][server][coin]["end_time"])
    time_breaks = list(set(time_breaks))
    time_breaks.sort()
    return time_breaks


def get_season_epochs(season):
    epoch = 0
    epoch_dict = {}
    repo_data = get_scoring_epochs_repo_data()
    if season in repo_data:
        repo_data = repo_data[season]
        coin_ranges = get_coin_time_ranges(season)

        for server in repo_data["Servers"]:
            epoch_dict.update({server: {}})
            time_breaks = get_epoch_time_breaks(repo_data, season, server)

            for i in range(len(time_breaks)-1):
                epoch = f"Epoch_{i}"
                epoch_dict[server].update({
                    epoch: {
                        'start_time': time_breaks[i],
                        'end_time': time_breaks[i+1]-1,
                        'start_event': get_epoch_events(repo_data, time_breaks[i]),
                        'end_event': get_epoch_events(repo_data, time_breaks[i+1])
                    }
                })
                epoch_coins = get_epoch_coins(season, server, epoch_dict[server][epoch])
                epoch_dict[server][epoch].update({
                    "coins": epoch_coins,
                    'num_epoch_coins': len(epoch_coins),
                    'score_per_ntx': get_epoch_score(server, len(epoch_coins))
                })
        for server in ["KMD", "LTC"]:
            epoch_dict.update({
                server: {
                    server: {
                        'start_time': SEASONS_INFO[season]["start_time"],
                        'end_time': SEASONS_INFO[season]["end_time"],
                        'start_event': "season start",
                        'end_event': "season end",
                        "coins": [server],
                        'num_epoch_coins': 1,
                        'score_per_ntx': get_epoch_score(server, 1)
                    }
                }
            })
    return epoch_dict


def get_epoch_events(repo_data, timestamp):
    events = []
    for server in repo_data["Servers"]:
        for coin in repo_data["Servers"][server]:
            if "start_time" in repo_data["Servers"][server][coin]:
                if timestamp == repo_data["Servers"][server][coin]["start_time"]:
                    events.append(f"{coin} start")
            if "end_time" in repo_data["Servers"][server][coin]:
                if timestamp == repo_data["Servers"][server][coin]["end_time"]:
                    events.append(f"{coin} end")
            if timestamp == repo_data["season_start"]:
                events.append(f"season start")
            if timestamp == repo_data["season_end"]:
                events.append(f"season end")

    events = list(set(events))
    return ', '.join(events)


def get_epoch_coins(season, server, epoch):
    epoch_coins = []
    coin_ranges = get_coin_time_ranges(season)
    if server in coin_ranges:
        coin_ranges = coin_ranges[server]
        for coin in coin_ranges:
            coin_start = coin_ranges[coin]["start"]
            coin_end = coin_ranges[coin]["end"]
            start_time = epoch["start_time"]
            end_time = epoch["end_time"]
            if coin_start <= start_time:
                if coin_end >= end_time:
                    epoch_coins.append(coin)
    return epoch_coins


def get_season_notaries(season):
    notaries = []
    if season in SEASONS_INFO and season in NOTARY_PUBKEYS:
        notaries = list(NOTARY_PUBKEYS[season]["Main"].keys())
        notaries.sort()
    return notaries


def get_season_coins(season):
    coins = []
    if season in SEASON_START_COINS:
        for server in SEASON_START_COINS[season]:
            coins += SEASON_START_COINS[season][server]
    if season in SCORING_EPOCHS_REPO_DATA:
        for server in SCORING_EPOCHS_REPO_DATA[season]["Servers"]:
            for coin in SCORING_EPOCHS_REPO_DATA[season]["Servers"][server]:
                if coin not in coins:
                    coins.append(coin)
    coins = list(set(coins))
    coins.sort()
    return coins


def get_season_server_coins(season, server):
    coins = []
    if season in SEASON_START_COINS:
        if server in SEASON_START_COINS[season]:
            coins += SEASON_START_COINS[season][server]
    if season in SCORING_EPOCHS_REPO_DATA:
        if server in SCORING_EPOCHS_REPO_DATA[season]["Servers"]:
            for coin in SCORING_EPOCHS_REPO_DATA[season]["Servers"][server]:
                if coin not in coins:
                    coins.append(coin)
    coins = list(set(coins))
    coins.sort()
    return coins


# Rescan full season
NOW = time.time()
RESCAN_SEASON = False
RESCAN_CHUNK_SIZE = 10000


# Notarisation Addresses
NTX_ADDR = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'
BTC_NTX_ADDR = '1P3rU1Nk1pmc2BiWC8dEy9bZa1ZbMp5jfg'
LTC_NTX_ADDR = 'LhGojDga6V1fGzQfNGcYFAfKnDvsWeuAsP'


# SPECIAL CASE BTC TXIDS
S4_INIT_BTC_FUNDING_TX = "13fee57ec60ef4ca42dbed5eb77d576bf7545e7042b334b27afdc33051635611"


# OP_RETURN data sometimes has extra info. Not used yet, but here for future reference
noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'GLEEC-OLD', 'AYA', 'MCL', 'VRSC']
VALID_SERVERS = ["Main", "Third_Party", "KMD", "BTC", "LTC"]
SCORING_EPOCHS_REPO_DATA = get_scoring_epochs_repo_data()


# Things that can be ignored
RETIRED_DPOW_COINS = ["HUSH3", "GLEEC-OLD", "AXO", "BTCH", "COQUICASH", "OOT"]
EXCLUDE_DECODE_OPRET_COINS = ['D']
EXCLUDED_SERVERS = ["Unofficial"]
EXCLUDED_SEASONS = ["Season_1", "Season_2", "Season_3", "Unofficial", "Season_4", "Season_5", "Season_5_Testnet", "VOTE2022_Testnet"]


OTHER_LAUNCH_PARAMS = {
    "BTC": "~/bitcoin/src/bitcoind",
    "LTC": "~/litecoin/src/litecoind",
    "KMD": "~/komodo/src/komodod", 
    "AYA": "~/AYAv2/src/aryacoind",
    "CHIPS": "~/chips/src/chipsd",
    "MIL": "~/mil-1/src/mild",
    "EMC2": "~/einsteinium/src/einsteiniumd",
    "TOKEL": "~/tokelkomodo/src/komodod -ac_name=TOKEL -ac_supply=100000000 -ac_eras=2 -ac_cbmaturity=1 -ac_reward=100000000,4250000000 -ac_end=80640,0 -ac_decay=0,77700000 -ac_halving=0,525600 -ac_cc=555 -ac_ccenable=236,245,246,247 -ac_adaptivepow=6 -addnode=135.125.204.169 -addnode=192.99.71.125 -addnode=144.76.140.197 -addnode=135.181.92.123 ",
    "VRSC": "~/VerusCoin/src/verusd",
    "GLEEC": "~/komodo/src/komodod -ac_name=GLEEC -ac_supply=210000000 -ac_public=1 -ac_staked=100 -addnode=95.217.161.126",
    "KIP0001": "~/komodo/src/komodod -ac_public=1 -ac_name=KIP0001 -ac_supply=139419284 -ac_staked=10 -addnode=178.159.2.6",
    "MCL": "~/marmara/src/komodod -ac_name=MCL -ac_supply=2000000 -ac_cc=2 -addnode=5.189.149.242 -addnode=161.97.146.150 -addnode=149.202.158.145 -addressindex=1 -spentindex=1 -ac_marmara=1 -ac_staked=75 -ac_reward=3000000000 -daemon"
}

OTHER_CONF_FILE = {
    "BTC": "~/.bitcoin/bitcoin.conf",
    "LTC": "~/.litecoin/litecoin.conf",
    "KMD": "~/.komodo/komodo.conf",
    "MCL": "~/.komodo/MCL/MCL.conf", 
    "MIL": "~/.mil/mil.conf", 
    "TOKEL": "~/.komodo/TOKEL/TOKEL.conf", 
    "KIP0001": "~/.komodo/KIP0001/KIP0001.conf",
    "AYA": "~/.aryacoin/aryacoin.conf",
    "CHIPS": "~/.chips/chips.conf",
    "EMC2": "~/.einsteinium/einsteinium.conf",
    "VRSC": "~/.komodo/VRSC/VRSC.conf",   
    "GLEEC": "~/.komodo/GLEEC/GLEEC.conf" 
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
    "LTC": "~/litecoin/src/litecoin-cli",
    "KMD": "~/komodo/src/komodo-cli",
    "MIL": "~/mil-1/src/mil-cli",
    "MCL": "~/komodo/src/komodo-cli -ac_name=MCL",
    "TOKEL": "~/komodo/src/komodo-cli -ac_name=TOKEL", 
    "GLEEC": "~/komodo/src/komodo-cli -ac_name=GLEEC",
    "KIP0001": "~/komodo/src/komodo-cli -ac_name=KIP0001",
    "AYA": "~/AYAv2/src/aryacoin-cli",
    "CHIPS": "~/chips/src/chips-cli",
    "EMC2": "~/einsteinium/src/einsteinium-cli",
    "VRSC": "~/VerusCoin/src/verus"  
}

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
        "MESH",
        "ZILLA",
        "GLEEC-OLD"
    ],
    "Season_7": [
        "BLUR",
        "LABS",
        "BTC",
        "MESH",
        "ZILLA",
        "GLEEC-OLD"
    ],
    "VOTE2022_Testnet": [
        "BLUR",
        "LABS",
    ]
}

SEASON_START_COINS = {
    "Season_6": {
        "LTC": ["LTC"],
        "KMD": ["KMD"],
        "Main": [
            "BET",
            "BOTS",
            "CLC",
            "CCL",
            "CRYPTO",
            "DEX",
            "GLEEC",
            "HODL",
            "ILN",
            "JUMBLR",
            "KOIN",
            "MGW",
            "MARTY",
            "MSHARK",
            "NINJA",
            "PANGEA",
            "PIRATE",
            "REVS",
            "DOC",
            "SUPERNET",
            "THC"
        ],
        "Third_Party": [
            "AYA",
            "EMC2",
            "MCL",
            "SFUSD",
            "TOKEL"
        ]
    },
    "Season_7": {
        "LTC": ["LTC"],
        "KMD": ["KMD"],
        "Main": [
            "CLC",
            "CCL",
            "DOC",
            "GLEEC",
            "ILN",
            "KOIN",
            "MARTY",
            "NINJA",
            "PIRATE",
            "SUPERNET",
            "THC"
        ],
        "Third_Party": [
            "AYA",
            "CHIPS",
            "EMC2",
            "MCL",
            "MIL",
            "TOKEL",
            "VRSC"
        ]
    },
    "VOTE2023_Testnet": {
        "Main": [
            "DOC",
            "MARTY"
        ]
    }
}

SEASONS_INFO = {
    "Season_1": {
        "start_block": 1,
        "end_block": 813999,
        "start_time": 1473793441,
        "end_time": 1530921600,
        "servers": {}
    },
    "Season_2": {
        "start_block": 814000,
        "end_block": 1443999,
        "start_time": 1530921600,
        "end_time": 1563148799,
        "servers": {}
    },
    "Season_3": {
        "start_block": 1444000,
        "end_block": 1921999,
        "start_time": 1563148800,
        "end_time": 1592146799,
        "servers": {}
    },
    "Season_4": {
        "start_block": 1922000,
        "end_block": 2436999,
        "start_time": 1592146800,
        "end_time": 1617364800,
        "servers": {}
    },
    "Season_5": {
        "start_block": 2437000,
        "end_block": 2893460,
        "post_season_end_block": 2963329,
        "start_time": 1623682800,
        "end_time": 1651622400,
        "post_season_end_time": 1656077852,
        "servers": {}
    },
    "Season_6": {
        "start_block": 2963330,
        "end_block": 3368762,
        "start_time": 1656077853,
        "end_time": 1680911999,
        "post_season_end_time": 1688169599,
        "servers": {}
    },
    "Season_7": {
        "start_block": 3484958,
        "end_block": 4484958,
        "start_time": 1688132253,
        "end_time": 1717199999,
        "post_season_end_time": 1725148799,
        "servers": {}
    },
    "VOTE2022_Testnet": {
        "start_block": 2903777,
        "end_block": 2923160,
        "start_time": 1651622400,
        "end_time": 1653436800,
        "coins": ["DOC", "MARTY"],
        "servers": {
            "Main": {
                "coins": ["DOC", "MARTY"],
                "addresses": {
                    "DOC": {},
                    "MARTY": {}
                },
                "epochs": {
                    "Epoch_0": {
                        "start_event": "testnet start",
                        "end_event": "testnet end",
                        "start_block": 2903777,
                        "end_block": 2923160,
                        "start_time": 1651622400,
                        "end_time": 1653436800,
                        "coins": ["DOC", "MARTY"]
                    }
                }
            }
        }    
    },
    "VOTE2023_Testnet": {
        "start_block": 2903777,
        "end_block": 2923160,
        "start_time": 1651622400,
        "end_time": 1653436800,
        "coins": ["DOC", "MARTY"],
        "servers": {
            "Main": {
                "coins": ["DOC", "MARTY"],
                "addresses": {
                    "DOC": {},
                    "MARTY": {}
                },
                "epochs": {
                    "Epoch_0": {
                        "start_event": "testnet start",
                        "end_event": "testnet end",
                        "start_block": 2903777,
                        "end_block": 2923160,
                        "start_time": 1651622400,
                        "end_time": 1653436800,
                        "coins": ["DOC", "MARTY"],
                        'score_per_ntx': 1
                    }
                }
            }
        }    
    }
}

# Exclude future seasons until about to happen.
for _season in SEASONS_INFO:
    if SEASONS_INFO[_season]["start_time"] > NOW - 96 * 60 * 60:
        EXCLUDED_SEASONS.append(_season)


EPOCHS = populate_epochs()

# Add season coins & notaries
for _season in SEASONS_INFO:
    SEASONS_INFO[_season].update({"notaries": get_season_notaries(_season)})

for _season in SEASONS_INFO:
    SEASONS_INFO[_season].update({"coins": get_season_coins(_season)})
    _ranges = get_coin_time_ranges(_season)
    for _server in _ranges:
        if _server in EPOCHS[_season]:
            SEASONS_INFO[_season]["servers"].update({
                _server: {
                    "addresses": {},
                    "coins": get_season_server_coins(_season, _server),
                    "epochs": EPOCHS[_season][_server],
                    "teunre": _ranges[_server]
                }
            })


CURRENT_SEASON, DPOW_COINS_ACTIVE, CURRENT_DPOW_COINS = get_dpow_active_info(SEASONS_INFO.keys())

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

        if _season in NOTARY_PUBKEYS:

            for _server in SEASONS_INFO[_season]["servers"]:
                _coins = SEASONS_INFO[_season]["servers"][_server]["coins"][:]

                if _server in ["Main", "Third_Party"]:
                    _coins.append("KMD")
                    _coins.append("LTC")
                    _coins.append("BTC")

                for _coin in _coins:
                    for _notary in SEASONS_INFO[_season]["notaries"]:

                        if _server in ["BTC", "LTC", "KMD"]:
                            pubkey = NOTARY_PUBKEYS[_season]["Main"][_notary]
                        else:
                            pubkey = NOTARY_PUBKEYS[_season][_server][_notary]

                        if _server == "Main":
                            address = get_addr_from_pubkey("KMD", pubkey)
                        else:
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

                        if _coin not in SEASONS_INFO[_season]["servers"][_server]["addresses"]:
                            SEASONS_INFO[_season]["servers"][_server]["addresses"].update({
                                _coin: {}
                            })

                        SEASONS_INFO[_season]["servers"][_server]["addresses"][_coin].update({
                            address: _notary
                        })


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

NEXT_SEASON_COINS = []


if __name__ == '__main__':
    pass