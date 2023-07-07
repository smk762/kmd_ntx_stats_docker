#!/usr/bin/env python3
import os
import json
import time
import requests
from lib_const import *
from decorators import *
from models import coin_social_row
import lib_helper as helper
import lib_urls as urls


@print_runtime
def generate_social_coins_template(season):

    all_coins = SEASONS_INFO[season]["coins"]
    try:
        url = urls.get_notary_nodes_repo_coin_social_url(season)
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
            for item in repo_info[coin]:
                template[coin].update({item:repo_info[coin][item]})

        elif coin in TRANSLATE_COINS:
            
            for item in repo_info[coin]:
                template[helper.handle_translate_coins(coin)].update({item:repo_info[coin][item]})
                

    with open(f"{os.path.dirname(os.path.abspath(__file__))}/social_coins_{season.lower()}.json", 'w+') as j:
        json.dump(template, j, indent = 4, sort_keys=True)


@print_runtime
def populate_coins_social(season):
    try:
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/social_coins_{season.lower()}.json", 'r') as j:
            coin_social = json.load(j)

        all_coins = SEASONS_INFO[season]["coins"]
        coin_info = requests.get(urls.get_coins_info_url()).json()['results']

        for coin in all_coins:

            row = coin_social_row()
            row.coin = coin
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


if __name__ == "__main__":

    logger.info(f"Preparing to populate [social_coins] table...")
    for season in ["Season_7"]:
        generate_social_coins_template(season)
        populate_coins_social(season)
    
    CURSOR.close()
    CONN.close()
