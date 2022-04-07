#!/usr/bin/env python3
import os
import json
import time
import requests
from lib_const import *
from lib_helper import *
from decorators import *
from lib_urls import get_dpow_server_coins_url, get_notary_nodes_repo_coin_social_url
from models import coin_social_row
from lib_validate import *


season = get_season()

dpow_main_coins = SEASONS_INFO[season]["servers"]["Main"]["coins"]
dpow_3p_coins = SEASONS_INFO[season]["servers"]["Third_Party"]["coins"]
all_coins = dpow_3p_coins + dpow_main_coins + ["KMD", "LTC", "BTC"]


@print_runtime
def generate_social_coins_template(season):

    translated_coins_main = []
    for coin in dpow_main_coins:
        translated_coin = handle_translate_coins(coin)
        translated_coins_main.append(translated_coin)

    translated_coins_3p = []
    for coin in dpow_3p_coins:
        translated_coin = handle_translate_coins(coin)
        translated_coins_3p.append(translated_coin)

    all_coins = list(set(translated_coins_main + translated_coins_3p + ["KMD", "LTC", "BTC"]))

    try:
        url = get_notary_nodes_repo_coin_social_url(season)
        repo_info = requests.get(url).json()
    except Exception as e:
        logger.error(f"Error getting info from {url} {e}")
        repo_info = {}
    template = {}
    for coin in all_coins:
        template.update({
            coin: {
                    "discord": "",
                    "email": "",
                    "explorers":[],
                    "github": "",
                    "linkedin": "",
                    "mining_pools":[],
                    "reddit": "",
                    "telegram": "",
                    "twitter": "",
                    "website": "",
                    "youtube": ""
            }
        })
    for coin in all_coins:
        if coin in repo_info:
            print(f"{coin} repo_info[coin]: {repo_info[coin]}")
            for item in repo_info[coin]:
                print(f"{coin} {item}: {repo_info[coin][item]}")
                template[coin].update({item:repo_info[coin][item]})

        elif coin in TRANSLATE_COINS:
            print(f"{coin} repo_info[coin]: {repo_info[coin]}")
            
            for item in repo_info[coin]:
                print(f"{coin} {item}: {repo_info[coin][item]}")
                template[handle_translate_coins(coin)].update({item:repo_info[coin][item]})
                

    with open(f"{os.path.dirname(os.path.abspath(__file__))}/social_coins_{season.lower()}.json", 'w+') as j:
        json.dump(template, j, indent = 4, sort_keys=True)


@print_runtime
def populate_coins_social(season):
    try:
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/social_coins_{season.lower()}.json", 'r') as j:
            coin_social = json.load(j)


        coin_info = requests.get(get_coins_info_url()).json()['results']

        for coin in all_coins:

            row = coin_social_row()
            row.chain = coin
            row.season = season
            row.icon = ""
            row.explorers = []

            if coin in coin_info:

                if "coins_info" in coin_info[coin]:
                    if "icon" in coin_info[coin]["coins_info"]:
                        row.icon = coin_info[coin]["coins_info"]["icon"]
                        
                if "explorers" in coin_info[coin]:
                    row.explorers = coin_info[coin]["explorers"]
                    
            else:
                logger.info(f"{coin} not in coin_info")

            if coin in coin_social:
                print(f"coin_social[coin]: {coin_social[coin]}")
                row.discord = coin_social[coin]["discord"]
                row.email = coin_social[coin]["email"]
                row.github = coin_social[coin]["github"]
                row.linkedin = coin_social[coin]["linkedin"]
                row.mining_pools = coin_social[coin]["mining_pools"]
                row.reddit = coin_social[coin]["reddit"]
                row.telegram = coin_social[coin]["telegram"]
                row.twitter = coin_social[coin]["twitter"]
                row.website = coin_social[coin]["website"]
                row.youtube = coin_social[coin]["youtube"]

            row.update()
    except Exception as e:
        logger.info(f"Error in [populate_coins_social]: {e}")
        print(f"social_coins_{season}.json does not exist!")


if __name__ == "__main__":

    logger.info(f"Preparing to populate [social_coins] table...")
    for season in SEASONS_INFO:
        if season not in EXCLUDED_SEASONS:
            generate_social_coins_template(season)
            populate_coins_social(season)
    
    CURSOR.close()
    CONN.close()
