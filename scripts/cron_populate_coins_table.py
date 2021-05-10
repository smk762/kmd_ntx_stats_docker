#!/usr/bin/env python3
import json
import time
import requests
from lib_const import *
from lib_table_select import get_notarised_chains
from models import coins_row


'''
This script scans the komodo, coins and dpow repositories and updates contexual info about the chains in the "coins" table.
It should be run as a cronjob every 12-24 hours
'''


# Gets coins info from coins repo
def parse_coins_repo():
    r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/coins")
    coins_repo = r.json()

    coins_data = {}
    for item in coins_repo:
        coin = item['coin']

        if coin in TRANSLATE_COINS:
            logger.warning(f"[parse_coins_repo] Translating {coin} to {TRANSLATE_COINS[coin]}")
            coin = TRANSLATE_COINS[coin]

        coins_data.update({coin:{"coins_info":item}})
        if 'asset' in item:
            coins_data[coin]["coins_info"].update({
                "pubtype": 60,
                "p2shtype": 85,
                "wiftype": 188,
                "txfee": 1000
                })

    for coin in coins_data:
        logger.info(f"[parse_coins_repo] Getting info for {coin}")
        coins_data[coin].update({
            "electrums":[],
            "electrums_ssl":[],
            "dpow":{},
            "dpow_active":0
        })

        if "mm2" not in coins_data[coin]["coins_info"]:
            coins_data[coin]["coins_info"].update({
                "mm2": 0
            })
            coins_data[coin].update({
                "mm2_compatible": 0
            })

        elif coins_data[coin]["coins_info"]["mm2"] == 1:
            coins_data[coin].update({
                "mm2_compatible": 1
            })


    return coins_data


# Gets dpow info from dpow repo
def parse_dpow_coins(coins_data):
    r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/dPoW/dev/README.md")
    dpow_readme = r.text
    lines = dpow_readme.splitlines()

    for line in lines:
        raw_info = line.split("|")
        info = [i.strip() for i in raw_info]

        if len(info) > 4 and info[0].lower() not in ['coin', '--------', 'game']:
            coin = info[0]

            try:
                src = info[1].split("(")[1].replace(")","")
            except:
                src = info[1]

            version = info[2]
            server = info[4].lower()
            if server == "dpow-3p":
                server = "Third_Party"
            elif server == "dpow-mainnet":
                server = "Main"

            if coin == "GleecBTC" and server == "Third_Party":
                logger.warning(f"[parse_dpow_coins] Translating GleecBTC to GLEEC-OLD")
                coin = "GLEEC-OLD"
            elif coin in TRANSLATE_COINS:
                logger.warning(f"[parse_dpow_coins] Translating {coin} to {TRANSLATE_COINS[coin]}")
                coin = TRANSLATE_COINS[coin]

            logger.info(f"[parse_dpow_coins] Adding {coin} to dpow")

            if coin not in coins_data:
                coins_data.update({coin:{}})

            coins_data[coin].update({
                "dpow":{
                    "src":src,
                    "version":version,
                    "server":server            
                },
                "dpow_active":1
            })
    return coins_data


# Gets launch params from komodo repo
def parse_assetchains(coins_data):
    r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/komodo/dev/src/assetchains.json")
    ac_json = r.json()
    for item in ac_json:
        coin = item['ac_name']

        if coin in TRANSLATE_COINS:
            logger.warning(f"[parse_assetchains] Translating {coin} to {TRANSLATE_COINS[coin]}")
            coin = TRANSLATE_COINS[coin]

        params = "~/komodo/src/komodod"
        for k,v in item.items():
            if k == 'addnode':
                for ip in v:
                    params += " -"+k+"="+ip
            else:
                params += " -"+k+"="+str(v)

        if coin not in coins_data:
            coins_data.update({coin:{}})
        if "coins_info" not in coins_data[coin]:
            coins_data[coin].update({"coins_info":{}})

        coins_data[coin]["coins_info"].update({"cli":'~/komodo/src/komodo-cli -ac_name='+coin})
        coins_data[coin]["coins_info"].update({"conf_path":'~/.komodo/'+coin+'/'+coin+'.conf'})
        coins_data[coin]["coins_info"].update({"launch_params":params})

    for coin in OTHER_CLI:
        if coin not in coins_data:
            coins_data.update({coin:{}})
        if "coins_info" not in coins_data[coin]:
            coins_data[coin].update({"coins_info":{}})
        coins_data[coin]["coins_info"].update({"cli":OTHER_CLI[coin]})

    for coin in OTHER_CONF_FILE:
        if coin not in coins_data:
            coins_data.update({coin:{}})
        if "coins_info" not in coins_data[coin]:
            coins_data[coin].update({"coins_info":{}})
        coins_data[coin]["coins_info"].update({"conf_path":OTHER_CONF_FILE[coin]})

    for coin in OTHER_LAUNCH_PARAMS:
        if coin not in coins_data:
            coins_data.update({coin:{}})
        if "coins_info" not in coins_data[coin]:
            coins_data[coin].update({"coins_info":{}})
        coins_data[coin]["coins_info"].update({"launch_params":OTHER_LAUNCH_PARAMS[coin]})

    return coins_data


# Gets Electrum / Explorer info from coins repo
def parse_electrum_explorer(coins_data):
    coins = list(coins_data.keys())
    coins.sort()
    for coin in coins:
        logger.info(f"[parse_electrum_explorer] Adding electrum info for {coin}")

        try:
            if coin == "COQUICASH":
                r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/COQUI")
            elif coin == "WLC21":
                r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/WLC")
            else:
                r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/"+coin)
            electrums = r.json()

            if coin in TRANSLATE_COINS:
                logger.warning(f"[parse_electrum_explorer] Translating {coin} to {TRANSLATE_COINS[coin]}")
                coin = TRANSLATE_COINS[coin]

            if "electrums" not in coins_data[coin]:
                coins_data[coin].update({"electrums":[]})
            if "electrums_ssl" not in coins_data[coin]:

                coins_data[coin].update({"electrums_ssl":[]})

            for electrum in electrums:

                if "protocol" in electrum:

                    if electrum['protocol'] == "SSL":
                        coins_data[coin]['electrums_ssl'].append(electrum['url'])

                    else:
                        coins_data[coin]['electrums'].append(electrum['url'])
                else:
                    coins_data[coin]['electrums'].append(electrum['url'])

        except Exception as e:
            if r.text != "404: Not Found":
                logger.error(f"Exception in [parse_electrum_explorer]: {e} {r.text}")


    for coin in coins:
        logger.info(f"[parse_electrum_explorer] Adding Explorer info for {coin}")
        try:
            if coin == "COQUICASH":
                r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/explorers/COQUI")
            elif coin == "WLC21":
                r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/explorers/WLC")
            else:
                r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/explorers/"+coin)
            explorers = r.json()

            if coin in TRANSLATE_COINS:
                logger.warning(f"[parse_electrum_explorer] Translating {coin} to {TRANSLATE_COINS[coin]}")
                coin = TRANSLATE_COINS[coin]

            if "explorers" not in coins_data[coin]:
                coins_data[coin].update({"explorers":[]})

            for explorer in explorers:
                coins_data[coin]['explorers'].append(explorer.replace("/tx/", "/").replace("/tx.dws?", "/"))

        except Exception as e:
            if r.text != "404: Not Found":
                logger.error(f"Exception in [parse_electrum_explorer]: {e} {r.text}")

    for coin in coins:
        logger.info(f"[parse_electrum_explorer] Adding Icon info for {coin}")
        try:
            if coin == "COQUICASH":
                r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/icons/coqui.png")
            elif coin == "WLC21":
                r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/icons/wlc.png")
            else:
                r = requests.get(f"https://raw.githubusercontent.com/KomodoPlatform/coins/master/icons/{coin.lower()}.png")
            url = f"https://raw.githubusercontent.com/KomodoPlatform/coins/master/icons/{coin.lower()}.png"
            r = requests.get(url)
            if r.text != "404: Not Found":

                if coin in TRANSLATE_COINS:
                    logger.warning(f"[parse_electrum_explorer] Translating {coin} to {TRANSLATE_COINS[coin]}")
                    coin = TRANSLATE_COINS[coin]

                coins_data[coin]["coins_info"].update({"icon":url})
        except Exception as e:
            if r.text != "404: Not Found":
                logger.error(f"Exception in [parse_electrum_explorer]: {e} {r.text}")


    return coins_data


# TODO: dPoW Tenure not populating?
def get_dpow_tenure(coins_data):

    now = int(time.time())
    notarised_chains = get_notarised_chains()

    for coin in notarised_chains:
        url = f'{THIS_SERVER}/api/table/notarised_tenure/?chain={coin}'
        logger.info(url)
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

                    if coin == "GLEEC" and server == "Third_Party":

                        if "GLEEC-OLD" not in coins_data:
                            coins_data.update({"GLEEC-OLD":{}})

                        if "dpow_tenure" not in coins_data["GLEEC-OLD"]:
                            coins_data["GLEEC-OLD"].update({"dpow_tenure":{}})

                        if season not in coins_data["GLEEC-OLD"]["dpow_tenure"]:
                            coins_data["GLEEC-OLD"]["dpow_tenure"].update({season:{}})

                        if server not in coins_data["GLEEC-OLD"]["dpow_tenure"][season]:
                            coins_data["GLEEC-OLD"]["dpow_tenure"][season].update({server:{}})

                        coins_data["GLEEC-OLD"]["dpow_tenure"][season][server].update({"start_time":season_start_time})
                        coins_data["GLEEC-OLD"]["dpow_tenure"][season][server].update({"end_time":season_end_time})

                    else:
                        if coin not in coins_data:
                            coins_data.update({coin:{}})

                        if "dpow_tenure" not in coins_data[coin]:
                            coins_data[coin].update({"dpow_tenure":{}})

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

                                    if coin == "GLEEC" and server == "Third_Party":
                                        coins_data["GLEEC-OLD"]["dpow_tenure"][season][server].update({"start_time":start_time})
                                    else:
                                        coins_data[coin]["dpow_tenure"][season][server].update({"start_time":start_time})

                                if "end_time" in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][coin]:
                                    end_time = PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][server][coin]["end_time"]

                                    if coin == "GLEEC" and server == "Third_Party":
                                        coins_data["GLEEC-OLD"]["dpow_tenure"][season][server].update({"end_time":end_time})
                                    else:
                                        coins_data[coin]["dpow_tenure"][season][server].update({"end_time":end_time})
                            
    for coin in coins_data:
        logger.info(f"[get_dpow_tenure] setting dpow tenure: {coin}")

        if "dpow_tenure" not in coins_data[coin]:
            coins_data[coin].update({"dpow_tenure":{}})

    return coins_data


def remove_old_coins(coins_data):
    current_coins = requests.get(f"{THIS_SERVER}/api/info/coins/").json()["results"]
    for coin in current_coins:
        if coin not in coins_data:
            logger.info(f"[remove_old_coins] Removing {coin}")
            coin_data = coins_row()
            coin_data.chain = coin
            coin_data.delete()


def update_coins(coins_data):
    for coin in coins_data:
        logger.info(f"[update_coins] Updating {coin}")
        coin_data = coins_row()
        coin_data.chain = coin

        if "coins_info" in coins_data[coin]:
            coin_data.coins_info = json.dumps(coins_data[coin]['coins_info'])
        else:
            logger.warning(f"'coins_info' not set for {coin}, setting to default")
            coin_data.coins_info = json.dumps({})
            
        if "electrums" in coins_data[coin]:
            coin_data.electrums = json.dumps(coins_data[coin]['electrums'])
        else:
            logger.warning(f"'electrums' not set for {coin}, setting to default")
            coin_data.electrums = json.dumps([])
            
        if "electrums_ssl" in coins_data[coin]:
            coin_data.electrums_ssl = json.dumps(coins_data[coin]['electrums_ssl'])
        else:
            logger.warning(f"'electrums_ssl' not set for {coin}, setting to default")
            coin_data.electrums_ssl = json.dumps([])
            
        if "explorers" in coins_data[coin]:
            coin_data.explorers = json.dumps(coins_data[coin]['explorers'])
        else:
            logger.warning(f"'explorers' not set for {coin}, setting to default")
            coin_data.explorers = json.dumps([])

        if "dpow" in coins_data[coin]:
            coin_data.dpow = json.dumps(coins_data[coin]['dpow'])
        else:
            logger.warning(f"'dpow' not set for {coin}, setting to default")
            coin_data.dpow = json.dumps({})

        if "dpow_tenure" in coins_data[coin]:
            coin_data.dpow_tenure = json.dumps(coins_data[coin]['dpow_tenure'])
        else:
            logger.warning(f"'dpow_tenure' not set for {coin}, setting to default")
            coin_data.dpow_tenure = json.dumps({})

        if "dpow_active" in coins_data[coin]:
            coin_data.dpow_active = coins_data[coin]['dpow_active']
        else:
            logger.warning(f"'dpow_active' not set for {coin}, setting to default")
            coin_data.dpow_active = 0

        if "mm2_compatible" in coins_data[coin]:
            coin_data.mm2_compatible = coins_data[coin]['mm2_compatible']
        else:
            logger.warning(f"'mm2_compatible' not set for {coin}, setting to default")
            coin_data.mm2_compatible = 0

        coin_data.update()


if __name__ == "__main__":

    logger.info(f"Preparing to populate [coins] table...")

    # Gets data from coins repo, komodo repo and dpow repo...
    coins_data = parse_coins_repo()
    coins_data = parse_dpow_coins(coins_data)
    coins_data = parse_assetchains(coins_data)
    coins_data = parse_electrum_explorer(coins_data)
    coins_data = get_dpow_tenure(coins_data)

    remove_old_coins(coins_data)
    update_coins(coins_data)

    logging.info("[coins] table update complete!")
    CURSOR.close()
    CONN.close()
