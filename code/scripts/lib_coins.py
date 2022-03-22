#!/usr/bin/env python3
import json
import time
import requests
from lib_const import *
from lib_helper import *
from lib_validate import *
from lib_urls import *
from models import coins_row
from lib_crypto import SMARTCHAIN_BASE_58
from lib_table_select import get_notarised_chains

'''
This script scans the komodo, coins and dpow repositories and updates contexual info about the chains in the "coins" table.
It should be run as a cronjob every 12-24 hours
'''

# Gets coins info from coins repo (Uses "ARRR, TKL")
def parse_coins_repo():

    coins_data = {}
    r = requests.get(get_coins_repo_coins_url())
    coins_repo = r.json()

    for item in coins_repo:
        coin = handle_translate_chains(item['coin'])
        coins_data = pre_populate_coins_data(coins_data, coin)
        item['coin'] = coin

        logger.info(f"[parse_coins_repo] Getting info for {coin}")
        coins_data.update({coin:{"coins_info":item}})

        if 'asset' in item:
            coins_data[coin]["coins_info"].update(SMARTCHAIN_BASE_58)

        if "mm2" not in coins_data[coin]["coins_info"]:
            coins_data[coin]["coins_info"].update({"mm2": 0})

        coins_data[coin].update({
                    "mm2_compatible": coins_data[coin]["coins_info"]["mm2"]
                })

    return coins_data


# Gets dpow info from dpow repo (Uses "PIRATE, TOKEL")
def parse_dpow_coins(coins_data):
    r = requests.get(get_dpow_readme_url())
    dpow_readme = r.text
    lines = dpow_readme.splitlines()

    for line in lines:
        info = [i.strip() for i in line.split("|")]

        if len(info) > 4 and info[0].lower() not in ['coin', '--------']:

            coin = handle_translate_chains(info[0])
            logger.info(f"[parse_dpow_coins] Adding {coin} to dpow")
            coins_data = pre_populate_coins_data(coins_data, coin)

            coins_data[coin].update({
                "dpow":{
                    "src": get_dpow_coin_src(info[1]),
                    "version": info[2],
                    "server": get_dpow_coin_server(info[4])            
                },
                "dpow_active":1
            })

    return coins_data


# Gets launch params from komodo repo (Uses "PIRATE")
def parse_assetchains(coins_data):
    r = requests.get(get_dpow_assetchains_url())
    for item in r.json():

        ac_name = item['ac_name']
        coin = handle_translate_chains(ac_name)
        coins_data = pre_populate_coins_data(coins_data, coin)

        coins_data[coin]["coins_info"].update({
            "cli": get_assetchain_cli(ac_name),
            "conf_path": get_assetchain_conf_path(ac_name),
            "launch_params": get_assetchain_launch_params(item)
        })

    for coin in OTHER_CLI:
        coins_data = pre_populate_coins_data(coins_data, coin)
        coins_data[coin]["coins_info"].update({"cli":OTHER_CLI[coin]})

    for coin in OTHER_CONF_FILE:
        coins_data = pre_populate_coins_data(coins_data, coin)
        coins_data[coin]["coins_info"].update({"conf_path":OTHER_CONF_FILE[coin]})

    for coin in OTHER_LAUNCH_PARAMS:
        coins_data = pre_populate_coins_data(coins_data, coin)
        coins_data[coin]["coins_info"].update({"launch_params":OTHER_LAUNCH_PARAMS[coin]})

    return coins_data


# Gets Electrum / Explorer info from coins repo (Uses TKL)
def parse_electrum_explorer(coins_data):
    coins = list(coins_data.keys())
    coins.sort()

    for coin in coins:

        coin = handle_translate_chains(coin)
        coins_data = pre_populate_coins_data(coins_data, coin)

        logger.info(f"[parse_electrum_explorer] Adding Electrum info for {coin}")
        coins_data = get_coins_repo_electrums(coins_data, coin)

        logger.info(f"[parse_electrum_explorer] Adding Explorer info for {coin}")
        coins_data = get_coins_repo_explorers(coins_data, coin)

        logger.info(f"[parse_electrum_explorer] Adding Icon info for {coin}")
        coins_data = get_coins_repo_icons(coins_data, coin)

    return coins_data


# TODO: dPoW Tenure not populating? Bad entries. Need some validation to avoid.
def get_dpow_tenure(coins_data):

    now = int(time.time())
    notarised_chains = get_notarised_chains()

    for coin in notarised_chains:
        coin = handle_translate_chains(coin)
        coins_data = pre_populate_coins_data(coins_data, coin)
        url = get_notarised_tenure_table_url(None, None, coin)
        notarised_tenure = requests.get(url).json()["results"]

        if len(notarised_tenure) > 0:
            notarised_tenure = notarised_tenure[0]
            if "season" in notarised_tenure:
                season = notarised_tenure["season"]
                server = notarised_tenure["server"]
                logger.info(f"[get_dpow_tenure] adding dpow_tenure data to {coin} {season} {server}")

                if season in SEASONS_INFO:

                    season_start_time = SEASONS_INFO[season]["start_time"]
                    season_end_time = SEASONS_INFO[season]["end_time"]

                    if season not in coins_data[coin]["dpow_tenure"]:
                        coins_data[coin]["dpow_tenure"].update({season:{}})

                    if server not in coins_data[coin]["dpow_tenure"][season]:
                        coins_data[coin]["dpow_tenure"][season].update({server:{}})

                    coins_data[coin]["dpow_tenure"][season][server].update({"start_time":season_start_time})
                    coins_data[coin]["dpow_tenure"][season][server].update({"end_time":season_end_time})

                    if season in PARTIAL_SEASON_DPOW_CHAINS:
                        if server in PARTIAL_SEASON_DPOW_CHAINS[season]:
                            if coin in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server]:

                                # TODO: Calc first / last block based on timestamp
                                if "start_time" in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][coin]:
                                    start_time = PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][coin]["start_time"]
                                    coins_data[coin]["dpow_tenure"][season][server].update({"start_time":start_time})

                                if "end_time" in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][coin]:
                                    end_time = PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][coin]["end_time"]
                                    coins_data[coin]["dpow_tenure"][season][server].update({"end_time":end_time})

    return coins_data


def remove_old_coins(coins_data):
    current_coins = requests.get(get_coins_info_url()).json()["results"]
    for coin in current_coins:
        if coin not in coins_data:
            logger.info(f"[remove_old_coins] Removing {coin}")
            coin_data = coins_row()
            coin_data.chain = coin
            coin_data.delete()


def update_coins(coins_data):
    for coin in coins_data:
        coin = handle_translate_chains(coin)
        logger.info(f"[update_coins] Updating {coin}")
        coin_data = coins_row()
        coin_data.chain = coin
        coin_data.coins_info = json.dumps(coins_data[coin]['coins_info'])
        coin_data.electrums = json.dumps(coins_data[coin]['electrums'])
        coin_data.electrums_ssl = json.dumps(coins_data[coin]['electrums_ssl'])
        coin_data.explorers = json.dumps(coins_data[coin]['explorers'])
        coin_data.dpow = json.dumps(coins_data[coin]['dpow'])
        coin_data.dpow_tenure = json.dumps(coins_data[coin]['dpow_tenure'])
        coin_data.dpow_active = coins_data[coin]['dpow_active']
        coin_data.mm2_compatible = coins_data[coin]['mm2_compatible']
        coin_data.update()