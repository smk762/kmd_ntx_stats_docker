#!/usr/bin/env python3
import json
import requests
import logging
import logging.handlers
from lib_const import *
from models import coins_row

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

'''
This script scans the coins and dpow repositories and updates contexual info about the chains in the "coins" table.
It should be run as a cronjob every 12-24 hours
'''

def parse_dpow_coins():
    dpow = {}
    dpow_main = []
    dpow_3p = []
    r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/dPoW/dev/README.md")
    dpow_readme = r.text
    lines = dpow_readme.splitlines()

    for line in lines:
        raw_info = line.split("|")
        info = [i.strip() for i in raw_info]

        if len(info) > 4 and info[0].lower() not in ['coin', '--------', 'game']:
            coin = info[0]

            if coin in TRANSLATE_COINS:
                coin = TRANSLATE_COINS[coin]

            logger.info("Adding "+coin+" to dpow")
            try:
                src = info[1].split("(")[1].replace(")","")
            except:
                src = info[1]

            version = info[2]
            server = info[4].lower()

            if server == "dpow-mainnet":
                dpow_main.append(coin)
            elif server == "dpow-3p":
                dpow_3p.append(coin)

            dpow.update({
                coin:{
                    "src":src,
                    "version":version,
                    "server":server            
                }
            })
    return dpow, dpow_main, dpow_3p

def remove_from_dpow(dpow):
    before_coins = ANTARA_COINS + THIRD_PARTY_COINS + OTHER_COINS + ['BTC', 'KMD']
    now_coins = list(dpow.keys())
    for coin in before_coins:

        if coin in TRANSLATE_COINS:
            coin = TRANSLATE_COINS[coin]

        if coin not in now_coins:
            logger.warning("Removing "+coin+" from dpow")
            coin_data = coins_row()
            coin_data.coin = coin
            coin_data.delete()


def parse_assetchains(dpow):
    r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/komodo/dev/src/assetchains.json")
    ac_json = r.json()
    for item in ac_json:
        coin = item['ac_name']

        if coin in TRANSLATE_COINS:
            coin = TRANSLATE_COINS[coin]

        params = "~/komodo/src/komodod"
        for k,v in item.items():
            if k == 'addnode':
                for ip in v:
                    params += " -"+k+"="+ip
            else:
                params += " -"+k+"="+str(v)
        if coin in dpow:
            dpow[coin].update({"launch_params":params})
            dpow[coin].update({"cli":'~/komodo/src/komodo-cli -ac_name='+coin})
            dpow[coin].update({"conf_path":'~/.komodo/'+coin+'/'+coin+'.conf'})
        else:
            logger.info(coin+" not in dpow list")

    for coin in OTHER_LAUNCH_PARAMS:
        if coin in dpow:
            dpow[coin].update({"launch_params":OTHER_LAUNCH_PARAMS[coin]})

    for coin in OTHER_CONF_FILE:
        if coin in dpow:
            dpow[coin].update({"conf_path":OTHER_CONF_FILE[coin]})

    for coin in OTHER_CLI:
        if coin in dpow:
            dpow[coin].update({"cli":OTHER_CLI[coin]})

    return dpow


def parse_coins_repo(dpow):
    r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/coins")
    coins_repo = r.json()

    coins_info = {}
    for item in coins_repo:
        coin = item['coin']

        if coin in TRANSLATE_COINS:
            coin = TRANSLATE_COINS[coin]

        coins_info.update({coin:{"coins_info":item}})

    for coin in dpow:
        if coin not in coins_info:
            coins_info.update({coin:{"coins_info":{}}})

    for server in PARTIAL_SEASON_DPOW_CHAINS["Season_4"]:
        for coin in PARTIAL_SEASON_DPOW_CHAINS["Season_4"][server]:
            if coin not in coins_info:
                coins_info.update({coin:{"coins_info":{}}})

    for coin in coins_info:
        logger.info(f"Getting info for {coin} from coins repo")
        coins_info[coin].update({
            "electrums":[],
            "electrums_ssl":[],
            "dpow":{},
            "dpow_active":0
        })

        if "mm2" not in coins_info[coin]["coins_info"]:
            coins_info[coin]["coins_info"].update({
                "mm2": 0
            })
            coins_info[coin].update({
                "mm2_compatible": 0
            })

        elif coins_info[coin]["coins_info"]["mm2"] == 1:
            coins_info[coin].update({
                "mm2_compatible": 1
            })

        if coin in dpow:
            coins_info[coin].update({
                "dpow":dpow[coin],
                "dpow_active":1,
            })

    return coins_info


# This is to cover coins with explorer/electrum but not in "coins" file
def parse_electrum_explorer(dpow, coins_info):
    no_electrums = []
    no_explorers = []
    for coin in coins_info:
        logger.info(f"Adding electrum/explorer info for {coin}")
        if 'dpow' not in coins_info[coin]:
            coins_info[coin].update({
                "dpow":{}
            })

        if 'dpow_active' not in coins_info[coin]:
            coins_info[coin].update({
                "dpow_active":0
            })

        if 'electrums' not in coins_info[coin]:
            coins_info[coin].update({
                "electrums":[],
                "electrums_ssl":[]
            })

        if 'explorers' not in coins_info[coin]:
            coins_info[coin].update({
                "explorers":[]
            })

        try:
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/"+coin)
            electrums = r.json()

            for electrum in electrums:
                if "protocol" in electrum:
                    if electrum['protocol'] == "SSL":
                        coins_info[coin]['electrums_ssl'].append(electrum['url'])
                    else:
                        coins_info[coin]['electrums'].append(electrum['url'])
                else:
                    coins_info[coin]['electrums'].append(electrum['url'])

        except Exception as e:
            if r.text != "404: Not Found":
                logger.error("GET "+coin+" ELECTRUM ERROR: "+str(e)+" [RESPONSE]: "+r.text)

        try:
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/explorers/"+coin)
            explorers = r.json()
            for explorer in explorers:
                coins_info[coin]['explorers'].append(explorer)
        except Exception as e:
            if r.text != "404: Not Found":
                logger.error("GET "+coin+" EXPLORER ERROR: "+str(e)+" [RESPONSE]: "+r.text)


        if len(coins_info[coin]['electrums']) == 0:
            no_electrums.append(coin)
        if len(coins_info[coin]['explorers']) == 0:
            no_explorers.append(coin)
    logger.warning("no_electrums: "+str(no_electrums))
    logger.warning("no_explorers: "+str(no_explorers))
    return coins_info

def get_dpow_tenure():
    tenure = requests.get(f'{THIS_SERVER}/api/info/notarised_tenure/').json()["results"][0]

    tenured_coins = list(tenure.keys()) + list(PARTIAL_SEASON_DPOW_CHAINS["Season_4"].keys())

    for chain in tenured_coins:
        for season in tenure[chain]:
            if season == "Season_4" and chain in DPOW_EXCLUDED_CHAINS["Season_4"] \
            or season == "season_undefined":
                pass
            else:
                season_start_block = SEASONS_INFO[season]["start_block"]
                season_start_time = SEASONS_INFO[season]["start_time"]
                season_end_block = SEASONS_INFO[season]["end_block"]
                season_end_time = SEASONS_INFO[season]["end_time"]

                tenure[chain][season].update({"first_ntx_block":season_start_block})
                tenure[chain][season].update({"last_ntx_block":season_end_block})
                tenure[chain][season].update({"first_ntx_block_time":season_start_time})
                tenure[chain][season].update({"last_ntx_block_time":season_end_time})

                if season in PARTIAL_SEASON_DPOW_CHAINS:
                    if server in PARTIAL_SEASON_DPOW_CHAINS:

                        if chain in PARTIAL_SEASON_DPOW_CHAINS[season][server]:
                            # TODO: Calc first / last block based on timestamp
                            if "start_time" in PARTIAL_SEASON_DPOW_CHAINS[season][server][chain]:
                                season_start_time = PARTIAL_SEASON_DPOW_CHAINS[season][server][chain]["start_time"]
                                tenure[chain][season].update({"first_ntx_block_time":season_start_time})
                                tenure[chain][season].update({"first_ntx_block":0})

                            if "end_time" in PARTIAL_SEASON_DPOW_CHAINS[season][server][chain]:
                                season_end_time = PARTIAL_SEASON_DPOW_CHAINS[season][server][chain]["end_time"]
                                tenure[chain][season].update({"last_ntx_block_time":season_end_time})
                                tenure[chain][season].update({"last_ntx_block":0})

    for chain in TRANSLATE_COINS:
        try:
            if TRANSLATE_COINS[chain] not in tenure:
                tenure.update({TRANSLATE_COINS[chain]:tenure[chain]})

            for season in tenure[chain]:
                tenure[TRANSLATE_COINS[chain]].update({season:tenure[chain][season]})
        except:
            pass

    for chain in BACK_TRANSLATE_COINS:
        try:
            if BACK_TRANSLATE_COINS[chain] not in tenure:
                tenure.update({BACK_TRANSLATE_COINS[chain]:tenure[chain]})

            for season in tenure[chain]:
                tenure[BACK_TRANSLATE_COINS[chain]].update({season:tenure[chain][season]})
        except:
            pass
    return tenure

dpow_tenure = get_dpow_tenure()

 
dpow, dpow_main, dpow_3p = parse_dpow_coins()
remove_from_dpow(dpow)
dpow = parse_assetchains(dpow)
coins_info = parse_coins_repo(dpow)
coins_info = parse_electrum_explorer(dpow, coins_info)


for coin in coins_info:

    coin_data = coins_row()
    coin_data.chain = coin
    coin_data.coins_info = json.dumps(coins_info[coin]["coins_info"])
    coin_data.electrums = json.dumps(coins_info[coin]['electrums'])
    coin_data.electrums_ssl = json.dumps(coins_info[coin]['electrums_ssl'])
    coin_data.explorers = json.dumps(coins_info[coin]['explorers'])
    coin_data.dpow = json.dumps(coins_info[coin]['dpow'])
    if coin in dpow_tenure:
        print(dpow_tenure[coin])
        coin_data.dpow_tenure = json.dumps(dpow_tenure[coin])
    else:
        coin_data.dpow_tenure = json.dumps({})
    coin_data.dpow_active = coins_info[coin]['dpow_active']
    coin_data.mm2_compatible = coins_info[coin]['mm2_compatible']
    coin_data.update()

logger.info("dpow count: "+str(len(dpow)))
logger.info("dpow: "+str(dpow))
logger.info("dpow_main count: "+str(len(dpow_main)))
logger.info("dpow_main: "+str(dpow_main))
logger.info("dpow_3p count: "+str(len(dpow_3p)))
logger.info("dpow_3p: "+str(dpow_3p))
logging.info("Finished!")

for season in SEASONS_INFO:
    try:
        coin_data = coins_row()
        coin_data.coin = season
        coin_data.delete()
    except:
        pass