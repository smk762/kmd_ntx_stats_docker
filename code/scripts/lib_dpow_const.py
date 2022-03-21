#!/usr/bin/env python3
import requests 
import time
from lib_urls import get_scoring_epochs_url

def get_scoring_epochs_repo():
    scoring_epochs = requests.get(get_scoring_epochs_url()).json()
    for season in scoring_epochs:
        if "GLEEC" in scoring_epochs[season]["Servers"]["dPoW-3P"]:
            scoring_epochs[season]["Servers"]["dPoW-3P"].update({
                "GLEEC-OLD": scoring_epochs[season]["Servers"]["dPoW-3P"]["GLEEC"]
            })
            del scoring_epochs[season]["Servers"]["dPoW-3P"]["GLEEC"]
    return scoring_epochs


def get_partial_season_dpow_chains(scoring_epochs):
    partial_season_dpow_chains = {}
    for season in scoring_epochs:
        partial_season_dpow_chains.update({
            season:{
                "Servers":{
                    "Main":{},
                    "Third_Party":{}
                }
            }
        })

        for server in scoring_epochs[season]["Servers"]:
            if server.lower() == "dpow-3p":
                epoch_server = "Third_Party"
            elif server.lower() == "dpow-mainnet":
                epoch_server = "Main"
            for item in scoring_epochs[season]["Servers"][server]:
                partial_season_dpow_chains[season]["Servers"][epoch_server].update({
                        item:scoring_epochs[season]["Servers"][server][item]
                    })

    partial_season_dpow_chains.update({
        "Season_5_Testnet": {
            "Servers": {
                "Main": {
                    "LTC": {
                        "start_time":1616508400,
                        "start_time_comment": "LTC Block 2022000"
                    },
                    "RICK": {
                        "start_time":1616442129,
                        "start_time_comment": "KMD Block 2316959"
                    },
                    "MORTY": {
                        "start_time":1616442129,
                        "start_time_comment": "KMD Block 2316959"
                    }
                }
            }
        }
    })

    return partial_season_dpow_chains


def get_scoring_epochs_source(partial_season_dpow_chains):
    scoring_epochs = {}
    for season in SEASONS_INFO:
        season_start = SEASONS_INFO[season]["start_time"]
        season_end = SEASONS_INFO[season]["end_time"]

        scoring_epochs.update({season:{
            "Main":{},
            "Third_Party":{},
            "KMD": {
                f"KMD": {
                    "start":season_start,
                    "end":season_end-1,
                    "start_event":"Season start",
                    "end_event": "Season end"
                }
            },
            "BTC": {
                f"BTC": {
                    "start":season_start,
                    "end":season_end-1,
                    "start_event":"Season start",
                    "end_event": "Season end"
                }
            },
            "LTC": {
                f"LTC": {
                    "start":season_start,
                    "end":season_end-1,
                    "start_event":"Season start",
                    "end_event": "Season end"
                }
            }
        }})

        if season not in partial_season_dpow_chains:
            scoring_epochs[season]["Main"].update({
                f"Epoch_0": {
                    "start":season_start,
                    "end":season_end-1,
                    "start_event":"Season start",
                    "end_event": "Season end"
                }
            })
            scoring_epochs[season]["Third_Party"].update({
                f"Epoch_0": {
                    "start":season_start,
                    "end":season_end-1,
                    "start_event":"Season start",
                    "end_event": "Season end"
                }
            })

        else:
            for server in partial_season_dpow_chains[season]["Servers"]:
                epoch_event_times = [season_start, season_end]

                for chain in partial_season_dpow_chains[season]["Servers"][server]:

                    if "start_time" in partial_season_dpow_chains[season]["Servers"][server][chain]:
                        epoch_event_times.append(partial_season_dpow_chains[season]["Servers"][server][chain]["start_time"])
                    if "end_time" in partial_season_dpow_chains[season]["Servers"][server][chain]:
                        epoch_event_times.append(partial_season_dpow_chains[season]["Servers"][server][chain]["end_time"])

                epoch_event_times = list(set(epoch_event_times))
                epoch_event_times.sort()
                num_epochs = len(epoch_event_times)

                for epoch in range(0,num_epochs-1):

                    epoch_start_time = epoch_event_times[epoch]
                    epoch_end_time = epoch_event_times[epoch+1]

                    epoch_start_events = []
                    epoch_end_events = []

                    if epoch_start_time == season_start:
                        epoch_start_events.append("Season start")
                    if epoch_end_time == season_end:
                        epoch_end_events.append("Season end")

                    for chain in partial_season_dpow_chains[season]["Servers"][server]:
                        if "start_time" in partial_season_dpow_chains[season]["Servers"][server][chain]:

                            if epoch_start_time == partial_season_dpow_chains[season]["Servers"][server][chain]["start_time"]:
                                epoch_start_events.append(f"{chain} start")

                            elif epoch_end_time == partial_season_dpow_chains[season]["Servers"][server][chain]["start_time"]:
                                epoch_end_events.append(f"{chain} start")

                        if "end_time" in partial_season_dpow_chains[season]["Servers"][server][chain]:

                            if epoch_start_time == partial_season_dpow_chains[season]["Servers"][server][chain]["end_time"]:
                                epoch_start_events.append(f"{chain} end")

                            elif epoch_end_time == partial_season_dpow_chains[season]["Servers"][server][chain]["end_time"]:
                                epoch_end_events.append(f"{chain} end")

                    if server == "dPoW-Mainnet":
                        score_server = "Main"
                    elif server == "dPoW-3P":
                        score_server = "Third_Party"
                    else:
                        score_server = server
                    scoring_epochs[season][score_server].update({
                        f"Epoch_{epoch}": {
                            "start":epoch_start_time,
                            "end":epoch_end_time-1,
                            "start_event":epoch_start_events,
                            "end_event":epoch_end_events
                        }
                    })

    return scoring_epochs


def get_scoring_epochs_all(scoring_epochs):
    all_scoring_epochs = []
    for season in scoring_epochs:
        for server in scoring_epochs[season]:
            for epoch in scoring_epochs[season][server]:
                all_scoring_epochs.append(epoch)

    return list(set(all_scoring_epochs))


OTHER_LAUNCH_PARAMS = {
    "BTC":"~/bitcoin/src/bitcoind",
    "SFUSD":"~/sfusd-core/src/smartusdd",
    "LTC":"~/litecoin/src/litecoind",
    "KMD":"~/komodo/src/komodod", 
    "AYA":"~/AYAv2/src/aryacoind",
    "CHIPS":"~/chips/src/chipsd",
    "MIL":"~/mil-1/src/mild",
    "EMC2":"~/einsteinium/src/einsteiniumd",
    "TOKEL": "~/tokelkomodo/src/komodod -ac_name=TOKEL -ac_supply=100000000 -ac_eras=2 -ac_cbmaturity=1 -ac_reward=100000000,4250000000 -ac_end=80640,0 -ac_decay=0,77700000 -ac_halving=0,525600 -ac_cc=555 -ac_ccenable=236,245,246,247 -ac_adaptivepow=6 -addnode=135.125.204.169 -addnode=192.99.71.125 -addnode=144.76.140.197 -addnode=135.181.92.123 ",
    "VRSC":"~/VerusCoin/src/verusd",
    "GLEEC":"~/komodo/src/komodod -ac_name=GLEEC -ac_supply=210000000 -ac_public=1 -ac_staked=100 -addnode=95.217.161.126",
    "VOTE2021":"~/komodo/src/komodod  -ac_name=VOTE2021 -ac_public=1 -ac_supply=129848152 -addnode=77.74.197.115",
    "GLEEC-OLD":"~/GleecBTC-FullNode-Win-Mac-Linux/src/gleecbtcd",
    "MCL":"~/marmara/src/komodod -ac_name=MCL -ac_supply=2000000 -ac_cc=2 -addnode=5.189.149.242 -addnode=161.97.146.150 -addnode=149.202.158.145 -addressindex=1 -spentindex=1 -ac_marmara=1 -ac_staked=75 -ac_reward=3000000000 -daemon"
}

OTHER_CONF_FILE = {
    "BTC":"~/.bitcoin/bitcoin.conf",
    "SFUSD":"~/.smartusd/smartusd.conf",
    "LTC":"~/.litecoin/litecoin.conf",
    "KMD":"~/.komodo/komodo.conf",
    "MCL":"~/.komodo/MCL/MCL.conf", 
    "MIL":"~/.mil/mil.conf", 
    "TOKEL":"~/.komodo/TOKEL/TOKEL.conf", 
    "VOTE2021":"~/.komodo/VOTE2021/VOTE2021.conf",
    "AYA":"~/.aryacoin/aryacoin.conf",
    "CHIPS":"~/.chips/chips.conf",
    "EMC2":"~/.einsteinium/einsteinium.conf",
    "VRSC":"~/.komodo/VRSC/VRSC.conf",   
    "GLEEC":"~/.komodo/GLEEC/GLEEC.conf",
    "GLEEC-OLD":"~/.gleecbtc/gleecbtc.conf",   
}

OTHER_CLI = {
    "BTC":"~/bitcoin/src/bitcoin-cli",
    "SFUSD":"~/sfusd-core/src/smartusd-cli",
    "LTC":"~/litecoin/src/litecoin-cli",
    "KMD":"~/komodo/src/komodo-cli",
    "MIL":"~/mil-1/src/mil-cli",
    "MCL":"~/komodo/src/komodo-cli -ac_name=MCL",
    "TOKEL":"~/komodo/src/komodo-cli -ac_name=TOKEL", 
    "GLEEC":"~/komodo/src/komodo-cli -ac_name=GLEEC",
    "VOTE2021":"~/komodo/src/komodo-cli -ac_name=VOTE2021",
    "AYA":"~/AYAv2/src/aryacoin-cli",
    "CHIPS":"~/chips/src/chips-cli",
    "EMC2":"~/einsteinium/src/einsteinium-cli",
    "VRSC":"~/VerusCoin/src/verus",   
    "GLEEC-OLD":"~/GleecBTC-FullNode-Win-Mac-Linux/src/gleecbtc-cli",   
}

# Some coins are named differently between dpow and coins repo...
TRANSLATE_COINS = {'COQUI': 'COQUICASH', 'OURC': 'OUR',
                   'WLC': 'WLC21', 'GleecBTC': 'GLEEC-OLD',
                   'ARRR': "PIRATE", 'TKL':'TOKEL'}

SEASONS_INFO = {
    "Season_1": {
            "start_block":1,
            "end_block":813999,
            "start_time":1473793441,
            "end_time":1530921600,
            "notaries":[]
        },
    "Season_2": {
            "start_block":814000,
            "end_block":1443999,
            "start_time":1530921600,
            "end_time":1563148799,
            "notaries":[]
        },
    "Season_3": {
            "start_block":1444000,
            "end_block":1921999,
            "start_time":1563148800,
            "end_time":1592146799,
            "notaries":[]
        },
    "Season_4": {
            "start_block":1922000, # https://github.com/KomodoPlatform/komodo/blob/master/src/komodo_globals.h#L47 (block_time 1592172139)
            "end_block":2436999,
            "start_time":1592146800, # https://github.com/KomodoPlatform/komodo/blob/master/src/komodo_globals.h#L48
            "end_time":1617364800, # April 2nd 2021 12pm
            "post_season_end_time":1623682799,
            "notaries":[]
        },
    "Season_5": {
            "start_block":2437000,
            "end_block":3436999,
            "start_time":1623682800,
            "end_time":1773682799,
            "notaries":[]
        },
    "Season_6": {
            "start_block":3437000,
            "end_block":4437000,
            "start_time":1773682800,
            "end_time":2773682800,
            "notaries":[]
        }
}

# set at post season to use "post_season_end_time" for aggreagates (e.g. mining)
POSTSEASON = True
RESCAN_SEASON = False

DPOW_EXCLUDED_CHAINS = {
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
        "BTC",
        "ARYA"
    ],
    "Season_5_Testnet": [
        "BLUR",
        "LABS",
        ],
    "Season_6": [
    ]
}

VALID_SERVERS = ["Main", "Third_Party", "KMD", "BTC", "LTC"]

NEXT_SEASON_CHAINS = {
    "LTC": ["LTC"],
    "KMD": ["KMD"],
    "Main": [
        "AXO",
        "BET",
        "BOTS",
        "BTCH",
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
        "OOT",
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
        "GLEEC-OLD",
        "MCL",
        "SFUSD",
        "VRSC",
        "TOKEL"
    ]
}

EXCLUDE_DECODE_OPRET_COINS = ['D']

EXCLUDED_SERVERS = ["Unofficial"]
EXCLUDED_SEASONS = ["Season_1", "Season_2", "Season_3", "Unofficial", "Season_4", "Season_5_Testnet"]
for season in SEASONS_INFO:
    if  SEASONS_INFO[season]["start_time"] > time.time():
        EXCLUDED_SEASONS.append(season)

RETIRED_SMARTCHAINS = ["HUSH3", "AXO", "BTCH", "COQUICASH", "OOT"]
RETIRED_DPOW_CHAINS = ["HUSH3", "GLEEC-OLD", "AXO", "BTCH", "COQUICASH", "OOT"]

SCORING_EPOCHS_REPO = get_scoring_epochs_repo()
PARTIAL_SEASON_DPOW_CHAINS = get_partial_season_dpow_chains(SCORING_EPOCHS_REPO)
SCORING_EPOCHS = get_scoring_epochs_source(PARTIAL_SEASON_DPOW_CHAINS)
ALL_SCORING_EPOCHS = get_scoring_epochs_all(SCORING_EPOCHS)



