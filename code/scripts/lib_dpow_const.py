#!/usr/bin/env python3.12
from const_seasons import SEASONS_INFO, get_dpow_active_info
from lib_crypto import get_addr_from_pubkey
from notary_pubkeys import NOTARY_PUBKEYS

RESCAN_SEASON = False
RESCAN_CHUNK_SIZE = 10000
CURRENT_SEASON, DPOW_COINS_ACTIVE, CURRENT_DPOW_COINS = get_dpow_active_info(SEASONS_INFO.keys())



# Notarisation Addresses
NTX_ADDR = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'
BTC_NTX_ADDR = '1P3rU1Nk1pmc2BiWC8dEy9bZa1ZbMp5jfg'
LTC_NTX_ADDR = 'LhGojDga6V1fGzQfNGcYFAfKnDvsWeuAsP'


# SPECIAL CASE BTC TXIDS
S4_INIT_BTC_FUNDING_TX = "13fee57ec60ef4ca42dbed5eb77d576bf7545e7042b334b27afdc33051635611"


# OP_RETURN data sometimes has extra info. Not used yet, but here for future reference
noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'GLEEC-OLD', 'AYA', 'MCL', 'VRSC']
VALID_SERVERS = ["Main", "Third_Party", "KMD", "BTC", "LTC"]


# Things that can be ignored
RETIRED_DPOW_COINS = ["HUSH3", "AXO", "BTCH", "COQUICASH", "OOT"]
EXCLUDE_DECODE_OPRET_COINS = ['D']
EXCLUDED_SERVERS = ["Unofficial"]


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
    "MCL": "~/marmara/src/marmarad -ac_name=MCL-addnode=5.189.149.242 -addnode=161.97.146.150 -addnode=149.202.158.145 -addressindex=1 -spentindex=1 -daemon"
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
    "MCL": "~/komodo/src/marmara-cli",
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
    "Season_8": [],
    "VOTE2022_Testnet": [
        "BLUR",
        "LABS",
    ]
}





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



if __name__ == '__main__':
    pass