#!/usr/bin/env python3
from lib_const import *
import lib_api
import lib_electrum
import lib_table_select
from lib_helper import is_postseason



def check_excluded_chains(season, server, chain):
    if season in DPOW_EXCLUDED_CHAINS: 
        if chain in DPOW_EXCLUDED_CHAINS[season]:
            return "Unofficial", "Unofficial"
    return season, server


def validate_epoch_chains(epoch_chains, season):
    if len(epoch_chains) == 0:
        return False
    for chain in epoch_chains:
        if season in DPOW_EXCLUDED_CHAINS:
            if chain in DPOW_EXCLUDED_CHAINS[season]:
                logger.warning(f"{chain} in DPOW_EXCLUDED_CHAINS[{season}]")
                return False
    return True

def get_season_from_block(block):
    if not isinstance(block, int):
        block = int(block)
    for season in SEASONS_INFO:
        if season.find("Testnet") == -1:
            start_block = SEASONS_INFO[season]['start_block']
            end_block = SEASONS_INFO[season]['end_block']
            if block >= start_block and block <= end_block:
                return season
    return None


    
def get_chain_epoch_at(season, server, chain, timestamp):
    if season in DPOW_EXCLUDED_CHAINS: 
        if chain not in DPOW_EXCLUDED_CHAINS[season]:
            if int(timestamp) >= SEASONS_INFO[season]["start_time"]:
                if int(timestamp) <= SEASONS_INFO[season]["end_time"]:
                    if chain in ["KMD", "BTC", "LTC"]:
                            if int(timestamp) <= SEASONS_INFO[season]["end_time"]:
                                return f"{chain}"

            epochs = lib_table_select.get_epochs(season, server)
            for epoch in epochs:
                if chain in epoch["epoch_chains"]:
                    if int(timestamp) >= epoch["epoch_start"]:
                        if int(timestamp) <= epoch["epoch_end"]:
                            return epoch["epoch"]

    return "Unofficial"


def validate_season_server_epoch(season, server, notary_addresses, block_time, chain):
    if season in DPOW_EXCLUDED_CHAINS:
        if chain in DPOW_EXCLUDED_CHAINS[season]:
            season = "Unofficial"
            server = "Unofficial"
            epoch = "Unofficial"
    season, server = get_season_server_from_addresses(notary_addresses, chain)
    epoch = get_chain_epoch_at(season, server, chain, block_time)
    return season, server, epoch


def handle_dual_server_chains(server, chain, addr=None):
    chain = handle_translate_chains(chain)
    if chain == "GLEEC":
        if addr:
            if addr.startswith("R"):
                server = "Main"
            else:
                server = "Third_Party"
        if server == "Third_Party":
            chain = "GLEEC-OLD"

    return server, chain


def handle_translate_chains(chain):
    if chain in TRANSLATE_COINS:
        return TRANSLATE_COINS[chain]
    return chain


def get_scored(score_value):
    if score_value > 0:
        return True
    else:
        return False


def get_chain_epoch_score_at(season, server, chain, timestamp):
    if season in DPOW_EXCLUDED_CHAINS: 
        if chain not in DPOW_EXCLUDED_CHAINS[season]:
            if chain in ["BTC", "LTC"]:
                return 0
            if chain in ["KMD"]:
                season_start = SEASONS_INFO[season]["start_time"]
                season_end = SEASONS_INFO[season]["end_time"]
                if int(timestamp) >= season_start and int(timestamp) <= season_end:
                    return 0.0325
                return 0

            active_chains, num_coins = get_server_active_scoring_dpow_chains_at_time(
                                            season, server, timestamp
                                        )

            if chain in active_chains:
                if server == "Main":
                    return round(0.8698/num_coins, 8)
                elif server == "Third_Party":
                    return round(0.0977/num_coins, 8)
                elif server == "Testnet":
                    return round(0.0977/num_coins, 8)
    return 0



def get_season_server_from_addresses(address_list, chain):

    tx_chain = "KMD"
    if chain in ["BTC", "KMD", "LTC"]:
        tx_chain = chain

    if len(address_list) == 13:
        seasons = list(NOTARY_ADDRESSES_DICT.keys())[::-1]

        for season in seasons:
            notary_seasons = []
            season_notaries = list(NOTARY_ADDRESSES_DICT[season].keys())

            for notary in season_notaries:
                if season in NOTARY_ADDRESSES_DICT:
                    if notary in NOTARY_ADDRESSES_DICT[season]:
                        if tx_chain in NOTARY_ADDRESSES_DICT[season][notary]:
                            if NOTARY_ADDRESSES_DICT[season][notary][tx_chain] in address_list:
                                notary_seasons.append(season)

            if len(notary_seasons) == 13:
                break

        if len(notary_seasons) == 13 and len(set(notary_seasons)) == 1:
            ntx_season = notary_seasons[0].replace("_Third_Party", "").replace(".5", "")

            if chain in ["BTC", "KMD", "LTC"]:
                server = chain
            
            elif notary_seasons[0].find("_Third_Party") > -1:
                server = "Third_Party"
            else:
                server = "Main"

            return ntx_season, server

    return  "Unofficial", "Unofficial"


def get_balance(chain, pubkey, addr, server):
    balance = -1
    try:
        if chain in ELECTRUMS:
            try:
                if chain == "GLEEC" and server == "Third_Party":
                    electrum = ELECTRUMS["GLEEC-OLD"][0].split(":")
                else:
                    electrum = ELECTRUMS[chain][0].split(":")
                url = electrum[0]
                port = electrum[1]
                balance = lib_electrum.get_full_electrum_balance(pubkey, url, port)
            except Exception as e:
                logger.warning(">>>>> "+chain+" via ["+url+":"+str(port)+"] FAILED | addr: "+addr+" | "+str(e))
                try:
                    balance = lib_api.get_dexstats_balance(chain, addr)
                    logger.info(f"{chain} via [DEXSTATS] OK | addr: {addr} | balance: {balance}")
                except Exception as e:
                    logger.warning(">>>>> "+chain+" via [DEXSTATS] FAILED | addr: "+addr+" | "+str(e))

        elif chain in ANTARA_COINS:
            try:
                balance = lib_api.get_dexstats_balance(chain, addr)
            except Exception as e:
                logger.warning(">>>>> "+chain+" via [DEXSTATS] FAILED | addr: "+addr+" | "+str(e))

        elif chain == "AYA":
            url = 'https://explorer.aryacoin.io/ext/getaddress/'+addr
            r = requests.get(url)
            if 'balance' in r.json():
                balance = r.json()['balance']
            else:
                logger.warning(">>>>> "+chain+" via explorer.aryacoin.io FAILED | addr: "+addr+" | "+str(r.text))

    except Exception as e:
        logger.error(">>>>> "+chain+" FAILED ALL METHODS | addr: "+addr+" | "+str(e))
    return balance



def get_server_active_scoring_dpow_chains_at_time(season, server, timestamp):
    url = get_notarised_tenure_table_url(season, server)
    r = requests.get(url)
    tenure = r.json()["results"]
    server_active_scoring_dpow_chains = []
    count = 0
    for item in tenure:
        if timestamp >= item["official_start_block_time"]:
            if timestamp <= item["official_end_block_time"]:
                if item["chain"] not in ["BTC", "LTC", "KMD"] and item["chain"] not in DPOW_EXCLUDED_CHAINS[season]:
                    server_active_scoring_dpow_chains.append(item["chain"])
    server_active_scoring_dpow_chains = list(set(server_active_scoring_dpow_chains))
    return server_active_scoring_dpow_chains, len(server_active_scoring_dpow_chains)


def get_chain_server(chain, season):
    if chain in ["KMD", "LTC", "BTC"]:
        return chain
    else:
        main_coins = requests.get(
            get_dpow_server_coins_url(season, 'Main')
        ).json()["results"]
        third_party_coins = requests.get(
            get_dpow_server_coins_url(season, 'Third_Party')
        ).json()["results"]
    if chain in main_coins:
        return "Main"
    elif chain in third_party_coins:
        return "Third_Party"
    else:
        return "Unofficial"

 
def get_season(time_stamp=None):

    if not time_stamp:
        time_stamp = int(time.time())
    time_stamp = int(time_stamp)

    # detect & convert js timestamps
    if round((time_stamp/1000)/time.time()) == 1:
        time_stamp = time_stamp/1000

    for season in SEASONS_INFO:

        if season.find("Testnet") == -1:
            if is_postseason(time_stamp):
                end_time = SEASONS_INFO[season]['post_season_end_time']
            else:
                end_time = SEASONS_INFO[season]['end_time']

        if time_stamp >= SEASONS_INFO[season]['start_time'] and time_stamp <= end_time:
            return season

    return "Unofficial"


def get_name_from_address(address):
    if address in KNOWN_ADDRESSES:
        return KNOWN_ADDRESSES[address]
    return address
