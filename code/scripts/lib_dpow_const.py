import requests 
OTHER_LAUNCH_PARAMS = {
    "BTC":"~/bitcoin/src/bitcoind",
    "SFUSD":"~/sfusd-core/src/smartusdd",
    "LTC":"~/litecoin/src/litecoind",
    "KMD":"~/komodo/src/komodod", 
    "AYA":"~/AYAv2/src/aryacoind",
    "CHIPS":"~/chips3/src/chipsd",
    "EMC2":"~/einsteinium/src/einsteiniumd",
    "VRSC":"~/VerusCoin/src/verusd",
    "GLEEC":"~/komodo/src/komodod -ac_name=GLEEC -ac_supply=210000000 -ac_public=1 -ac_staked=100 -addnode=95.217.161.126",
    "VOTE2021":"~/komodo/src/komodod  -ac_name=VOTE2021 -ac_public=1 -ac_supply=129848152 -addnode=77.74.197.115",
    "GLEEC-OLD":"~/GleecBTC-FullNode-Win-Mac-Linux/src/gleecbtcd",
    "MCL":"~/Marmara-v.1.0/src/komodod -ac_name=MCL -pubkey=$pubkey -ac_supply=2000000 -ac_cc=2 -addnode=37.148.210.158 -addnode=37.148.212.36 -addressindex=1 -spentindex=1 -ac_marmara=1 -ac_staked=75 -ac_reward=3000000000 -daemon"
}
OTHER_CONF_FILE = {
    "BTC":"~/.bitcoin/bitcoin.conf",
    "SFUSD":"~/.smartusd/smartusd.conf",
    "LTC":"~/.litecoin/litecoin.conf",
    "KMD":"~/.komodo/komodo.conf",   
    "MCL":"~/.komodo/MCL/MCL.conf", 
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
    "MCL":"~/komodo/src/komodo-cli -ac_name=MCL",
    "GLEEC":"~/komodo/src/komodo-cli -ac_name=GLEEC",
    "VOTE2021":"~/komodo/src/komodo-cli -ac_name=VOTE2021",
    "AYA":"~/AYAv2/src/aryacoin-cli",
    "CHIPS":"~/chips3/src/chips-cli",
    "EMC2":"~/einsteinium/src/einsteinium-cli",
    "VRSC":"~/VerusCoin/src/verus",   
    "GLEEC-OLD":"~/GleecBTC-FullNode-Win-Mac-Linux/src/gleecbtc-cli",   
}

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
            "end_block":3437000,
            "start_time":1623682800,
            "end_time":1773682800,
            "notaries":[]
        }
}

PARTIAL_SEASON_DPOW_CHAINS = {}
SCORING_EPOCHS_REPO = requests.get("https://raw.githubusercontent.com/KomodoPlatform/dPoW/master/doc/scoring_epochs.json").json()
SCORING_EPOCHS_REPO["Season_4"]["Servers"]["dPoW-3P"].update({
    "GLEEC-OLD": SCORING_EPOCHS_REPO["Season_4"]["Servers"]["dPoW-3P"]["GLEEC"]
})
del SCORING_EPOCHS_REPO["Season_4"]["Servers"]["dPoW-3P"]["GLEEC"]

for season in SCORING_EPOCHS_REPO:
    PARTIAL_SEASON_DPOW_CHAINS.update({
        season:{
            "Servers":{
                "Main":{},
                "Third_Party":{}
            }
        }
    })

    for server in SCORING_EPOCHS_REPO[season]["Servers"]:
        if server == "dPoW-3P":
            epoch_server = "Third_Party"
        elif server == "dPoW-Mainnet":
            epoch_server = "Main"
        for item in SCORING_EPOCHS_REPO[season]["Servers"][server]:
            PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][epoch_server].update({
                    item:SCORING_EPOCHS_REPO[season]["Servers"][server][item]
                })

PARTIAL_SEASON_DPOW_CHAINS.update({
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
        ]
}

EXCLUDE_DECODE_OPRET_COINS = ['D']

EXCLUDED_SERVERS = ["Unofficial"]
EXCLUDED_SEASONS = ["Season_1", "Season_2", "Season_3", "Unofficial", "Season_4", "Season_5_Testnet"]

SCORING_EPOCHS = {

}

for season in SEASONS_INFO:
    season_start = SEASONS_INFO[season]["start_time"]
    season_end = SEASONS_INFO[season]["end_time"]

    SCORING_EPOCHS.update({season:{
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

    if season not in PARTIAL_SEASON_DPOW_CHAINS:
        SCORING_EPOCHS[season]["Main"].update({
            f"Epoch_0": {
                "start":season_start,
                "end":season_end-1,
                "start_event":"Season start",
                "end_event": "Season end"
            }
        })
        SCORING_EPOCHS[season]["Third_Party"].update({
            f"Epoch_0": {
                "start":season_start,
                "end":season_end-1,
                "start_event":"Season start",
                "end_event": "Season end"
            }
        })

    else:
        for server in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"]:
            epoch_event_times = [season_start, season_end]

            for chain in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server]:

                if "start_time" in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][chain]:
                    epoch_event_times.append(PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][chain]["start_time"])
                if "end_time" in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][chain]:
                    epoch_event_times.append(PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][chain]["end_time"])

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

                for chain in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server]:
                    if "start_time" in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][chain]:

                        if epoch_start_time == PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][chain]["start_time"]:
                            epoch_start_events.append(f"{chain} start")

                        elif epoch_end_time == PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][chain]["start_time"]:
                            epoch_end_events.append(f"{chain} start")

                    if "end_time" in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][chain]:

                        if epoch_start_time == PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][chain]["end_time"]:
                            epoch_start_events.append(f"{chain} end")

                        elif epoch_end_time == PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][chain]["end_time"]:
                            epoch_end_events.append(f"{chain} end")

                if server == "dPoW-Mainnet":
                    score_server = "Main"
                elif server == "dPoW-3P":
                    score_server = "Third_Party"
                else:
                    score_server = server
                SCORING_EPOCHS[season][score_server].update({
                    f"Epoch_{epoch}": {
                        "start":epoch_start_time,
                        "end":epoch_end_time-1,
                        "start_event":epoch_start_events,
                        "end_event":epoch_end_events
                    }
                })

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
        "VRSC"
    ]
}