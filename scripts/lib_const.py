import os
import time
import requests
import logging
import logging.handlers
from dotenv import load_dotenv

from lib_db import CONN, CURSOR
from base_58 import COIN_PARAMS, get_addr_from_pubkey
from lib_rpc import def_credentials
from notary_pubkeys import NOTARY_PUBKEYS
from s5_candidates import VOTE2021_ADDRESSES_DICT

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ENV VARS
load_dotenv()

SKIP_PAST_SEASONS = (os.getenv("SKIP_PAST_SEASONS") == 'True') # set this to False in .env when originally populating the table, or rescanning
SKIP_UNTIL_YESTERDAY = (os.getenv("SKIP_UNTIL_YESTERDAY") == 'True') # set this to True in .env to quickly update tables with most recent data
OTHER_SERVER = os.getenv("OTHER_SERVER") # set to IP or domain to allow for external imports of data to avoid API limits
THIS_SERVER = os.getenv("THIS_SERVER") # IP / domain of the local server
API_PAGE_BREAK = int(os.getenv("API_PAGE_BREAK")) # How many pages back to go with verbose API responses

SEASON = "Season_4"

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
TRANSLATE_COINS = { 'COQUI':'COQUICASH','OURC':'OUR','WLC':'WLC21','GleecBTC':'GLEEC-OLD', "SFUSD":"PBC"  }

# Coins categorised
OTHER_COINS = []
ANTARA_COINS = []
THIRD_PARTY_COINS = []
RETIRED_SMARTCHAINS = ["HUSH3"]

COINS_INFO = requests.get(f'{THIS_SERVER}/api/info/coins/').json()['results']
ELECTRUMS = requests.get(f'{THIS_SERVER}/api/info/electrums/').json()['results']

SEASON = 'Season_4'

ANTARA_COINS = requests.get(f'{THIS_SERVER}/api/info/dpow_server_coins/?season={SEASON}&server=Main').json()["results"]
THIRD_PARTY_COINS = requests.get(f'{THIS_SERVER}/api/info/dpow_server_coins/?season={SEASON}&server=Third_Party').json()["results"]

ALL_COINS = ANTARA_COINS + THIRD_PARTY_COINS + ['BTC', 'KMD', 'LTC']
ALL_ANTARA_COINS = ANTARA_COINS + RETIRED_SMARTCHAINS # add retired smartchains here


# Defines BASE_58 coin parameters
for coin in ALL_ANTARA_COINS:
    COIN_PARAMS.update({coin:COIN_PARAMS["KMD"]})

for coin in THIRD_PARTY_COINS:
    COIN_PARAMS.update({coin:COIN_PARAMS[coin]})


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
        },
    "Season_5_Testnet": {
            "start_block":2299140,
            "end_block":2436999,
            "start_time":1615367302,
            "end_time":1618660800, # April 17th 2021 12pm,
            "notaries":[]
        }
}
# set at post season to use "post_season_end_time" for aggreagates (e.g. mining)
POSTSEASON = True

# BTC specific addresses. TODO: This could be reduced / merged.
NOTARIES = {}
ALL_SEASON_NOTARIES = []


for season in SEASONS_INFO:
    NOTARIES.update({season:[]})
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
    NN_BTC_ADDRESSES_DICT.update({season:{}})
    try:
        addresses = requests.get(f"{THIS_SERVER}/api/table/addresses/?chain=BTC&season={season}").json()
        for item in addresses['results']:
            ALL_SEASON_NOTARY_BTC_ADDRESSES.append(item["address"])
            ALL_SEASON_NN_BTC_ADDRESSES_DICT.update({item["address"]:item["notary"]})
            NN_BTC_ADDRESSES_DICT[season].update({item["address"]:item["notary"]})
    except Exception as e:
        logger.error(e)
        logger.info("Addresses API might be down!")
    NOTARY_BTC_ADDRESSES.update({season:list(NN_BTC_ADDRESSES_DICT[season].keys())})

ALL_SEASON_NOTARY_BTC_ADDRESSES = list(set(ALL_SEASON_NOTARY_BTC_ADDRESSES))

NN_LTC_ADDRESSES_DICT = {}
NOTARY_LTC_ADDRESSES = {}
ALL_SEASON_NN_LTC_ADDRESSES_DICT = {}
ALL_SEASON_NOTARY_LTC_ADDRESSES = []

for season in SEASONS_INFO:
    NN_LTC_ADDRESSES_DICT.update({season:{}})
    try:
        addresses = requests.get(f"{THIS_SERVER}/api/table/addresses/?chain=LTC&season={season}").json()
        for item in addresses['results']:
            ALL_SEASON_NOTARY_LTC_ADDRESSES.append(item["address"])
            ALL_SEASON_NN_LTC_ADDRESSES_DICT.update({item["address"]:item["notary"]})
            NN_LTC_ADDRESSES_DICT[season].update({item["address"]:item["notary"]})
    except Exception as e:
        logger.error(e)
        logger.info("Addresses API might be down!")
    NOTARY_LTC_ADDRESSES.update({season:list(NN_LTC_ADDRESSES_DICT[season].keys())})

ALL_SEASON_NOTARY_LTC_ADDRESSES = list(set(ALL_SEASON_NOTARY_LTC_ADDRESSES))

# shows addresses for all coins for each notary node, by season.
NOTARY_ADDRESSES_DICT = {}

for season in NOTARY_PUBKEYS:
    NOTARY_ADDRESSES_DICT.update({season:{}})
    notaries = list(NOTARY_PUBKEYS[season].keys())
    notaries.sort()
    for notary in notaries:
        if notary not in NOTARY_ADDRESSES_DICT:
            NOTARY_ADDRESSES_DICT[season].update({notary:{}})

        for coin in COIN_PARAMS:
            NOTARY_ADDRESSES_DICT[season][notary].update({
                coin:get_addr_from_pubkey(coin, NOTARY_PUBKEYS[season][notary])
            })


# lists all season, name, address and id info for each notary
NOTARY_INFO = {}

# detailed address info categories by season. showing notary name, id and pubkey
ADDRESS_INFO = {}

for season in NOTARY_PUBKEYS:
    notary_id = 0    
    ADDRESS_INFO.update({season:{}})
    notaries = list(NOTARY_PUBKEYS[season].keys())
    notaries.sort()
    for notary in notaries:
        if notary not in NOTARY_INFO:
            NOTARY_INFO.update({
                notary:{
                    "Notary_ids":[],
                    "Seasons":[],
                    "Addresses":[],
                    "Pubkeys":[]
                }})
        addr = get_addr_from_pubkey("KMD", NOTARY_PUBKEYS[season][notary])
        ADDRESS_INFO[season].update({
            addr:{
                "Notary":notary,
                "Notary_id":notary_id,
                "Pubkey":NOTARY_PUBKEYS[season][notary]
            }})
        NOTARY_INFO[notary]['Notary_ids'].append(notary_id)
        NOTARY_INFO[notary]['Seasons'].append(season)
        NOTARY_INFO[notary]['Addresses'].append(addr)
        NOTARY_INFO[notary]['Pubkeys'].append(NOTARY_PUBKEYS[season][notary])
        notary_id += 1

for season in NOTARY_PUBKEYS:
    notaries = list(NOTARY_PUBKEYS[season].keys())
    notaries.sort()
    for notary in notaries:
        if season.find("Season_3") != -1:
            SEASONS_INFO["Season_3"]['notaries'].append(notary)
        elif season.find("Season_4") != -1:
            SEASONS_INFO["Season_4"]['notaries'].append(notary)
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
            KNOWN_ADDRESSES.update({address:notary})

NON_NOTARY_ADDRESSES = {
    "RRDRX84ETUUeAU2bFZr2TScYazYxziofYd":"Luxor (Mining Pool)",
    "RSXGTHQSqwcMw1vowKfEE7sQ8fAmv1tmso":"LuckPool (Mining Pool)",
    "RR7MvgQikm5Mt2wAaRMmWy1qfwAZTQ5eaV":"ZergPool (Mining Pool)",
    "RVtg94k4yjx5JznUt47fpHZkWC2wA5KqCQ":"ZPool (Mining Pool)",
    "RKA3nd9q1s9fqyBCDLMDkK3TAjTgdUxbEV":"Mining-Dutch (Mining Pool)",
    "RAE4r5zQg2jzBq6yHt3DpKppf6hFTpVW2m":"SoloPool (Mining Pool)",
    "RDPYwhSRoE5XRe15WwXQpxL4D9Y6dAhihy":"MiningFool (Mining Pool)",
    "RKLBUAQjAQSP4wybMiVWSFGvFP7nQHcEbN":"Mining-Dutch (Mining Pool)",
    "RHEx3ZVnK9u1AVroUfW3YBCEb7YLuzx775":"Tangery (Mining Pool)",
    "RH9Ti1vkrtE2RMcYCZG1f9UWeaoHPuN24K":"CoolMine (Mining Pool)",
    "RT2v445xYCHZYnQytczFqAwegP6ossURME":"k1pool"
}

KNOWN_ADDRESSES.update(NON_NOTARY_ADDRESSES)


OTHER_LAUNCH_PARAMS = {
    "BTC":"~/bitcoin/src/bitcoind",
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
    "Season_5": [],
    "Season_5_Testnet": [
        "BLUR",
        "LABS",
        ]
}

EXCLUDE_DECODE_OPRET_COINS = ['D']

EXCLUDED_SERVERS = ["Unofficial"]
EXCLUDED_SEASONS = ["Season_1", "Season_2", "Season_3", "Unofficial", "Season_5_Testnet"]

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