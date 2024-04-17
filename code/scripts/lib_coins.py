#!/usr/bin/env python3
import json
import time
import requests
from lib_api import *
from lib_const import *
from lib_helper import *
from lib_validate import *
from lib_query import *
from lib_update import *
from lib_urls import *
from models import coins_row
from lib_crypto import SMARTCHAIN_BASE_58
from lib_helper import get_season_coins
from decorators import print_runtime

'''
This script scans the komodo, coins and dpow repositories and updates contexual info about the coins in the "coins" table.
It should be run as a cronjob every 12-24 hours
'''


def get_alt_name(coin):
    coin = handle_translate_coins(coin)
    coin = coin.replace("-segwit", "")
    return coin


def get_assetchain_conf_path(ac_name):
    return f"~/.komodo/{ac_name}/{ac_name}.conf"


def get_assetchain_cli(ac_name):
    return f"~/komodo/src/komodo-cli -ac_name={ac_name}"


@print_runtime
def parse_coins_repo():
    '''
    Gets data from coins repository and prepopulates the coins_data dict.
    Some coins are named differently in dPoW Repo (e.g. ARRR/TKL) so
    in thiese cases both are initialised.
    '''
    coins_data = {}
    r = requests.get(get_coins_repo_coins_url())
    coins_repo = r.json()

    for item in coins_repo:
        coin = item['coin']
        _coin = get_alt_name(item['coin'])
        if coin != _coin:
            coins_data = get_coins_repo_info(coins_data, _coin, item)
        coins_data = get_coins_repo_info(coins_data, coin, item)
    return coins_data


def get_coins_repo_info(coins_data, coin, item):
    ''' Add coins repository data for a coin to the coins_data dict'''
    logger.info(f"[get_coins_repo_info] Getting info for {coin}")
    coins_data = pre_populate_coins_data(coins_data, coin)

    if "derivation_path" in item:
        item["derivation_path"] = item["derivation_path"].replace("'", "-")

    coins_data[coin].update({"coins_info":item})

    if 'asset' in item:
        coins_data[coin]["coins_info"].update(SMARTCHAIN_BASE_58)

    if "mm2" not in coins_data[coin]["coins_info"]:
        coins_data[coin]["coins_info"].update({"mm2": 0})

    coins_data[coin].update({
                "mm2_compatible": coins_data[coin]["coins_info"]["mm2"]
            })
    return coins_data


@print_runtime
def parse_dpow_coins(coins_data):
    '''
    Gets data from dPoW repo to use for stats.
    No coin renaming or name duplication for this data.
    '''
    r = requests.get(get_dpow_readme_url())
    dpow_readme = r.text
    lines = dpow_readme.splitlines()
    dpow_coins = []
    for line in lines:
        info = [i.strip() for i in line.split("|")]

        if len(info) > 4 and info[0].lower() not in ['coin', '--------']:
            dpow_coins.append(coin)
            coins_data[coin].update({
                "dpow":{
                    "src": get_dpow_coin_src(info[1]),
                    "version": info[2],
                    "server": get_dpow_coin_server(info[4])
                },
                "dpow_active":1
            })

    return coins_data, dpow_coins


def get_coins_repo_lightwallets(lightwallets, coins_data):
    '''
    Gets lightwallet data from coins repo to use for activation commands.
    No coin renaming or name duplication
    '''
    for coin in lightwallets:
        data = requests.get(lightwallets[coin]).json()
        logger.info(f"[get_coins_repo_lightwallets] {coin}")
        coins_data[coin]['lightwallets'] = data
    return coins_data


def get_coins_repo_electrums(electrums, coins_data):
    '''
    Gets electrum data from coins repo to use for activation commands.
    No coin renaming or name duplication
    '''
    for coin in electrums:
        coins_data = pre_populate_coins_data(coins_data, coin)
        data = requests.get(electrums[coin]).json()
        logger.info(f"[get_coins_repo_electrums] {coin}")
        for item in data:
            print(item)
            if "protocol" in item:
                if item['protocol'] == "SSL":
                    coins_data[coin]['electrums_ssl'].append(item['url'])
                    if 'ws_url' in item:
                        coins_data[coin]['electrums_wss'].append(item['ws_url'])
                elif item['protocol'] == "WSS":
                    print(item)
                    if 'ws_url' in item:
                        coins_data[coin]['electrums_wss'].append(item['ws_url'])
                    elif 'url' in item:
                        coins_data[coin]['electrums_wss'].append(item['url'])
                else:
                    coins_data[coin]['electrums'].append(item['url'])
            else:
                coins_data[coin]['electrums'].append(item['url'])
    return coins_data


def get_coins_repo_explorers(explorers, coins_data):
    '''
    Gets explorer data from coins repo to use for activation commands.
    No coin renaming or name duplication
    '''
    for coin in explorers:
        pre_populate_coins_data(coins_data, coin)
        data = requests.get(explorers[coin]).json()
        logger.info(f"[get_coins_repo_explorers] {coin}")
        for explorer in data:
            coins_data[coin]['explorers'].append(explorer.replace("/tx/", "/").replace("/tx.dws?", "/"))
    return coins_data


def drop_suffix(coin):
    if coin.endswith("-AVX20") or coin.endswith("-BEP20") or coin.endswith("-ERC20")\
                                 or coin.endswith("-HRC20") or coin.endswith("-KRC20")\
                                 or coin.endswith("-PLG20") or coin.endswith("-FTM20")\
                                 or coin.endswith("-HCO20") or coin.endswith("-OLD")\
                                 or coin.endswith("-MVR20") or coin.endswith("-segwit"):
        return coin.split("-")[0]
    else:
        return coin


def get_coins_repo_icons(icons, coins_data):
    '''
    Gets coin icon path from coins repo.
    No coin renaming or name duplication
    '''
    for coin in coins_data:
        _coin = drop_suffix(coin)
        alt_name = get_alt_name(coin)

        if f"{_coin.lower()}.png" in icons:
            coins_data[coin]["coins_info"].update({"icon": icons[f"{_coin.lower()}.png"]})
        if f"{alt_name.lower()}.png" in icons:
            coins_data[coin]["coins_info"].update({"icon": icons[f"{alt_name.lower()}.png"]})

    return coins_data


@print_runtime
def get_dpow_tenure(coins_data):
    '''
    Gets dPoW tenure data from database.
    No coin renaming or name duplication.
    '''
    now = int(time.time())
    notarised_coins = get_season_coins()

    for coin in notarised_coins:

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

                    if season in SCORING_EPOCHS_REPO_DATA:
                        if server in SCORING_EPOCHS_REPO_DATA[season]["Servers"]:
                            if coin in SCORING_EPOCHS_REPO_DATA[season]["Servers"][server]:

                                if "start_time" in SCORING_EPOCHS_REPO_DATA[season]["Servers"][server][coin]:
                                    start_time = SCORING_EPOCHS_REPO_DATA[season]["Servers"][server][coin]["start_time"]
                                    coins_data[coin]["dpow_tenure"][season][server].update({"start_time":start_time})

                                if "end_time" in SCORING_EPOCHS_REPO_DATA[season]["Servers"][server][coin]:
                                    end_time = SCORING_EPOCHS_REPO_DATA[season]["Servers"][server][coin]["end_time"]
                                    coins_data[coin]["dpow_tenure"][season][server].update({"end_time":end_time})

    return coins_data


@print_runtime
def parse_assetchains(coins_data):
    '''
    Gets launch/conf data for dPoW coins.
    No coin renaming or name duplication
    '''
    r = requests.get(get_dpow_assetchains_url())
    for item in r.json():

        coin = item['ac_name']

        coins_data[coin]["coins_info"].update({
            "cli": get_assetchain_cli(coin),
            "conf_path": get_assetchain_conf_path(coin),
            "launch_params": get_assetchain_launch_params(item)
        })

    for coin in OTHER_CLI:
        if coin in coins_data:
            coins_data[coin]["coins_info"].update({"cli":OTHER_CLI[coin]})

    for coin in OTHER_CONF_FILE:
        if coin in coins_data:
            coins_data[coin]["coins_info"].update({"conf_path":OTHER_CONF_FILE[coin]})

    for coin in OTHER_LAUNCH_PARAMS:
        if coin in coins_data:
            coins_data[coin]["coins_info"].update({"launch_params":OTHER_LAUNCH_PARAMS[coin]})

    return coins_data


def remove_delisted_coins(dpow_coins):
    '''
    Removes old coins from database
    '''
    r = requests.get(get_coins_repo_coins_url())
    coins_repo = r.json()
    coins_repo_coins = []
    for item in coins_repo:
        coins_repo_coins.append(item["coin"])
    db_coins = get_all_coins()
    delisted_coins = list(set(db_coins) - set(coins_repo_coins))
    for coin in delisted_coins:
        if coin not in dpow_coins:
            print(f"delisting {coin}")
            delist_coin(coin)


@print_runtime
def parse_electrum_explorer(coins_data):
    '''
    Gets supplemental coins repo info.
    '''
    coins = list(coins_data.keys())
    coins.sort()

    explorers_data = get_github_folder_contents("KomodoPlatform", "coins", "explorers")
    explorers = {}
    for item in explorers_data:
        if 'message' in explorers_data:
            print(explorers_data)
        if item["name"] not in ["deprecated", "explorer_paths.json"]:
            explorers.update({item["name"]:item["download_url"]})

    electrums_data = get_github_folder_contents("KomodoPlatform", "coins", "electrums")
    electrums = {}
    for item in electrums_data:
        if item["name"] not in ["deprecated"]:
            electrums.update({item["name"]:item["download_url"]})

    lightwallets_data = get_github_folder_contents("KomodoPlatform", "coins", "light_wallet_d")
    lightwallets = {}
    for item in lightwallets_data:
        if item["name"] not in ["deprecated"]:
            lightwallets.update({item["name"]:item["download_url"]})

    icons_data = get_github_folder_contents("KomodoPlatform", "coins", "icons_original")
    icons = {}
    for item in icons_data:
        if item["name"] not in ["deprecated"]:
            icons.update({item["name"]:item["download_url"]})

    coins_data = get_coins_repo_lightwallets(lightwallets, coins_data)
    coins_data = get_coins_repo_electrums(electrums, coins_data)
    coins_data = get_coins_repo_explorers(explorers, coins_data)
    coins_data = get_coins_repo_icons(icons, coins_data)

    return coins_data


def pre_populate_coins_data(coins_data, coin):
    if coin not in coins_data:
        coins_data.update({coin: {}})
    if "coins_info" not in coins_data[coin]:
        coins_data[coin].update({"coins_info": {}})
    if "dpow" not in coins_data[coin]:
        coins_data[coin].update({"dpow": {}})
    if "dpow_tenure" not in coins_data[coin]:
        coins_data[coin].update({"dpow_tenure": {}})
    if "dpow_active" not in coins_data[coin]:
        coins_data[coin].update({"dpow_active": 0})
    if "electrums" not in coins_data[coin]:
        coins_data[coin].update({"electrums": []})
    if "electrums_ssl" not in coins_data[coin]:
        coins_data[coin].update({"electrums_ssl": []})
    if "electrums_wss" not in coins_data[coin]:
        coins_data[coin].update({"electrums_wss": []})
    if "explorers" not in coins_data[coin]:
        coins_data[coin].update({"explorers": []})
    if "lightwallets" not in coins_data[coin]:
        coins_data[coin].update({"lightwallets": []})
    if "mm2_compatible" not in coins_data[coin]:
        coins_data[coin].update({"mm2_compatible": 0})

    return coins_data


def remove_old_coins(coins_data):
    current_coins = requests.get(get_coins_info_url()).json()["results"]
    for coin in current_coins:
        if coin not in coins_data:
            logger.info(f"[remove_old_coins] Removing {coin}")
            coin_data = coins_row()
            coin_data.coin = coin
            coin_data.delete()


def update_coins(coins_data):
    for coin in coins_data:
        coin_data = coins_row()
        coin_data.coin = coin
        coin_data.coins_info = json.dumps(coins_data[coin]['coins_info'])
        coin_data.electrums = json.dumps(coins_data[coin]['electrums'])
        coin_data.electrums_ssl = json.dumps(coins_data[coin]['electrums_ssl'])
        coin_data.electrums_wss = json.dumps(coins_data[coin]['electrums_wss'])
        coin_data.explorers = json.dumps(coins_data[coin]['explorers'])
        coin_data.lightwallets = json.dumps(coins_data[coin]['lightwallets'])
        coin_data.dpow = json.dumps(coins_data[coin]['dpow'])
        coin_data.dpow_tenure = json.dumps(coins_data[coin]['dpow_tenure'])
        coin_data.dpow_active = coins_data[coin]['dpow_active']
        coin_data.mm2_compatible = coins_data[coin]['mm2_compatible']
        coin_data.update()
