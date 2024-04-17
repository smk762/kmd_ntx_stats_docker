#!/usr/bin/env python3
from lib_const import *
import lib_api
import lib_electrum
import lib_query
from lib_helper import is_postseason, handle_translate_coins
from lib_urls import get_notarised_tenure_table_url

def check_excluded_coins(season, server, coin):
    if season in DPOW_EXCLUDED_COINS: 
        if coin in DPOW_EXCLUDED_COINS[season]:
            return "Unofficial", "Unofficial"
    return season, server


def validate_epoch_coins(epoch_coins, season):
    if len(epoch_coins) == 0:
        return False
    for coin in epoch_coins:
        if season in DPOW_EXCLUDED_COINS:
            if coin in DPOW_EXCLUDED_COINS[season]:
                logger.warning(f"{coin} in DPOW_EXCLUDED_COINS[{season}]")
                return False
    return True


def get_season_from_block(block):
    if not isinstance(block, int):
        block = int(block)
    for season in SEASONS_INFO:
        if season.find("Testnet") == -1:
            start_block = SEASONS_INFO[season]['start_block']
            if 'post_season_end_block' in SEASONS_INFO[season]:
                end_block = SEASONS_INFO[season]['post_season_end_block']
            else:
                end_block = SEASONS_INFO[season]['end_block']
            if block >= start_block and block <= end_block:
                return season
    return None


def get_coin_epoch_at(season, server, coin, timestamp, testnet):
    if testnet:
        return "Epoch_0"

    if season in DPOW_EXCLUDED_COINS: 
        if coin not in DPOW_EXCLUDED_COINS[season]:
            if coin in ["KMD", "BTC", "LTC"]:
                if int(timestamp) >= SEASONS_INFO[season]["start_time"]:
                    if int(timestamp) <= SEASONS_INFO[season]["end_time"]:
                        return f"{coin}"
                else:
                    return "Unofficial"


            epochs = SEASONS_INFO[season]["servers"][server]["epochs"]
            for epoch in epochs:
                if coin in epochs[epoch]["coins"]:
                    if int(timestamp) >= epochs[epoch]["start_time"]:
                        if int(timestamp) <= epochs[epoch]['end_time']:
                            return epoch

    return "Unofficial"


def validate_season_server_epoch(season, notary_addresses, block_time, coin, testnet=False):
    if season in DPOW_EXCLUDED_COINS:
        if coin in DPOW_EXCLUDED_COINS[season]:
            season = "Unofficial"
            server = "Unofficial"
            epoch = "Unofficial"
    season, server, testnet = get_season_server_from_kmd_addresses(notary_addresses, coin, testnet)
    epoch = get_coin_epoch_at(season, server, coin, block_time, testnet)
    return season, server, epoch, testnet


def get_server_from_kmd_address(season, address):
    if server in SEASONS_INFO:
        for server in ["Main", "Third_Party"]:
            if server in SEASONS_INFO[season]:
                if address in SEASONS_INFO[season]["servers"][server]["addresses"]["KMD"]:
                    return server
    return "Unofficial"


def handle_dual_server_coins(server, coin):
    coin = handle_translate_coins(coin)

    if coin in ["GLEEC-OLD"]:
        server = "Third_Party"
        
    if coin in ["GLEEC"]:
        if server == "Third_Party":
            coin ="GLEEC-OLD"

    return server, coin


def get_scored(score_value):
    if score_value > 0:
        return True
    else:
        return False


def get_coin_epoch_score_at(season, server, coin, timestamp, testnet=False):
    if season in DPOW_EXCLUDED_COINS:
        if coin in DPOW_EXCLUDED_COINS[season]:
            return 0

    if season in SEASONS_INFO:
        season_start = SEASONS_INFO[season]["start_time"]
        season_end = SEASONS_INFO[season]["end_time"]

        if testnet and int(timestamp) >= season_start and int(timestamp) <= season_end:
            return 1

        if coin in ["BTC", "LTC"]:
            return 0

        if coin in ["KMD"]:
            if int(timestamp) >= season_start and int(timestamp) <= season_end:
                return 0.0325
            return 0

        if server in SEASONS_INFO[season]["servers"]:
            epoch = get_epoch_at_timestamp(season, server, coin, timestamp)
            return get_epoch_score(season, server, epoch)

    return 0


def calc_epoch_score(server, num_coins):
    logger.info(f"[calc_epoch_score] {server} {num_coins}")
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


def get_epoch_coins(season, server, epoch):
    try:
        return SEASONS_INFO[season]["servers"][server]["epochs"][epoch]['coins']
    except:
        return []


def get_epoch_score(season, server, epoch):
    try:
        return SEASONS_INFO[season]["servers"][server]["epochs"][epoch]['score_per_ntx']
    except:
        return 0

def get_epoch_at_timestamp(season, server, coin, timestamp):
    epochs = SEASONS_INFO[season]["servers"][server]["epochs"]

    for epoch in epochs:
        if coin in epochs[epoch]["coins"]:
            start = epochs[epoch]['start_time']
            end = epochs[epoch]['end_time']
            if timestamp >= start and timestamp <= end:
                return epoch

    return "Unofficial"



def get_epoch_scores_dict(season):
    epoch_scores_dict = {}
    if season in SEASONS_INFO:
        for server in SEASONS_INFO[season]["servers"]:
            if server != "Unofficial":
                epoch_scores_dict.update({server:{}})
                for epoch in SEASONS_INFO[season]["servers"][server]["epochs"]:
                    epoch_coins = SEASONS_INFO[season]["servers"][server]["epochs"][epoch]['coins']
                    score_per_ntx = calc_epoch_score(server, len(epoch_coins))
                    epoch_scores_dict[server].update({epoch:score_per_ntx})
                    
    return epoch_scores_dict


def get_season_server_from_kmd_addresses(address_list, coin, testnet=False):

    ntx_coin = "KMD"

    if coin in ["BTC"]:
        ntx_coin = "BTC"
        if not set(address_list).issubset(set(ALL_SEASON_NOTARY_BTC_ADDRESSES.keys())):
            return "Unofficial", "Unofficial", False


    if coin in ["LTC"]:
        ntx_coin = "LTC"
        if not set(address_list).issubset(set(ALL_SEASON_NOTARY_LTC_ADDRESSES.keys())):
            return "Unofficial", "Unofficial", False

    elif not set(address_list).issubset(set(KNOWN_ADDRESSES.keys())):
        return "Unofficial", "Unofficial", False

    for season in SEASONS_INFO:
        if season.find("Testnet") == -1:
            testnet = False
        else:
            testnet = True

        if len(address_list) == 13:
            for server in SEASONS_INFO[season]["servers"]:
                if server not in ["KMD", "LTC", "BTC"] and coin not in ["KMD", "LTC", "BTC"]:
                    if ntx_coin in SEASONS_INFO[season]["servers"][server]["addresses"]:
                        server_addresses = SEASONS_INFO[season]["servers"][server]["addresses"][ntx_coin]
                        if set(address_list).issubset(set(server_addresses.keys())):
                            return season, server, testnet

                elif coin == server:
                    if ntx_coin in SEASONS_INFO[season]["servers"][server]["addresses"]:
                        server_addresses = SEASONS_INFO[season]["servers"][server]["addresses"][ntx_coin]
                        if set(address_list).issubset(set(server_addresses.keys())):
                            return season, server, testnet
        else:
            if testnet:
                server_addresses = SEASONS_INFO[season]["servers"]["Main"]["addresses"]["KMD"]
                if set(address_list).issubset(set(server_addresses.keys())):
                    if coin in SEASONS_INFO[season]["servers"]["Main"]["coins"]:
                        return season, "Main", testnet

    return "Unofficial", "Unofficial", False


def get_balance(coin, pubkey, addr):
    balance = -1
    if coin in ELECTRUMS:
        balance = lib_electrum.get_full_electrum_balance(pubkey, coin)

    if balance == -1:
        balance = lib_api.get_dexstats_balance(coin, addr)
        
    if balance == -1:
        if coin == "AYA":
            url = 'https://explorer.aryacoin.io/ext/getaddress/'+addr
            r = requests.get(url)
            if 'balance' in r.json():
                balance = r.json()['balance']
            else:
                balance = -1
                logger.warning(">>>>> "+coin+" via explorer.aryacoin.io FAILED | addr: "+addr+" | "+str(r.text))

    return balance


def get_server_active_scoring_dpow_coins_at_time(season, server, timestamp):
    url = get_notarised_tenure_table_url(season, server)
    r = requests.get(url)
    tenure = r.json()["results"]
    server_active_scoring_dpow_coins = []
    count = 0
    for item in tenure:
        if timestamp >= item["official_start_block_time"]:
            if timestamp <= item["official_end_block_time"]:
                coin = item["coin"]
                if coin not in ["BTC", "LTC", "KMD"] and coin not in DPOW_EXCLUDED_COINS[season]:
                    server_active_scoring_dpow_coins.append(coin)
    server_active_scoring_dpow_coins = list(set(server_active_scoring_dpow_coins))
    return server_active_scoring_dpow_coins, len(server_active_scoring_dpow_coins)


def get_dpow_coin_server(season, coin):
    if season.find("Testnet") != -1:
        return "Main"

    if coin in ["KMD", "LTC", "BTC"]:
        return coin
    else:
        if "Main" in SEASONS_INFO[season]["servers"]:
            if coin in SEASONS_INFO[season]["servers"]["Main"]["coins"]:
                return "Main"

        if "Third_Party" in SEASONS_INFO[season]["servers"]:
            if coin in SEASONS_INFO[season]["servers"]["Third_Party"]["coins"]:
                return "Third_Party"

    return "Unofficial"

 
def get_season(timestamp=None):

    if not timestamp:
        timestamp = int(time.time())
    timestamp = int(timestamp)

    # detect & convert js timestamps
    if round((timestamp/1000)/time.time()) == 1:
        timestamp = timestamp/1000

    for season in SEASONS_INFO:

        if season.find("Testnet") == -1:
            if 'post_season_end_time' in SEASONS_INFO[season]:
                end_time = SEASONS_INFO[season]['post_season_end_time']
            else:
                end_time = SEASONS_INFO[season]['end_time']

        if timestamp >= SEASONS_INFO[season]['start_time'] and timestamp <= end_time:
            return season

    return "Unofficial"


def get_name_from_address(address):
    if address in KNOWN_ADDRESSES:
        return KNOWN_ADDRESSES[address]
    return address

def get_category_from_name(name):
    if "Mining Pool" in name:
        return "Mining Pool"
    for i in ["_AR", "_EU", "_NA", "_SH", "_DEV"]:
        if i in name:
            return "Notary"
    return "Solo"

def override_ticker(ticker):
    if ticker == "TKL": ticker = "TOKEL"