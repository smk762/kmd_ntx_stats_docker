#!/usr/bin/env python3
import os
import json
import time
import requests
from lib_const import *
from lib_helper import *
from lib_notary import get_season
from models import coin_social_row


def generate_social_coins_template(season):
    url = f"{THIS_SERVER}/api/info/dpow_server_coins"
    dpow_main_chains = requests.get(f"{url}/?season={season}&server=Main").json()['results']
    dpow_3p_chains = requests.get(f"{url}/?season={season}&server=Third_Party").json()['results']
    all_chains = dpow_3p_chains+dpow_main_chains+["KMD", "LTC", "BTC"]

    translated_chains_main = []
    for chain in dpow_main_chains:
        translated_chain = handle_translate_chains(chain)
        translated_chains_main.append(translated_chain)

    translated_chains_3p = []
    for chain in dpow_3p_chains:
        translated_chain = handle_translate_chains(chain)
        translated_chains_3p.append(translated_chain)

    all_chains = list(set(translated_chains_main + translated_chains_3p + ["KMD", "LTC", "BTC"]))

    try:
        url = f"https://raw.githubusercontent.com/KomodoPlatform/NotaryNodes/master/{season.lower().replace('_', '')}/coin_social.json"
        logger.info(url)
        repo_info = requests.get(url).json()
    except Exception as e:
        logger.error(f"Error getting info from {url} {e}")
        repo_info = {}
    template = {}
    for chain in all_chains:
        template.update({
            chain: {
                    "discord": "",
                    "email":"",
                    "explorers":[],
                    "github": "",
                    "linkedin":"",
                    "mining_pools":[],
                    "reddit":"",
                    "telegram": "",
                    "twitter": "",
                    "website": "",
                    "youtube": ""
            }
        })
    for chain in all_chains:
        if chain in repo_info:
            print(f"{chain} repo_info[chain]: {repo_info[chain]}")
            for item in repo_info[chain]:
                print(f"{chain} {item}: {repo_info[chain][item]}")
                template[chain].update({item:repo_info[chain][item]})

        elif chain in TRANSLATE_COINS:
            print(f"{chain} repo_info[chain]: {repo_info[chain]}")
            
            for item in repo_info[chain]:
                print(f"{chain} {item}: {repo_info[chain][item]}")
                template[handle_translate_chains(chain)].update({item:repo_info[chain][item]})
                

    with open(f"{os.path.dirname(os.path.abspath(__file__))}/social_coins_{season.lower()}.json", 'w+') as j:
        json.dump(template, j, indent = 4, sort_keys=True)


def populate_coins_social(season):
    try:
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/social_coins_{season.lower()}.json", 'r') as j:
            chain_social = json.load(j)

        url = f"{THIS_SERVER}/api/info/dpow_server_coins"
        dpow_main_chains = requests.get(f"{url}/?season={season}&server=Main").json()['results']
        dpow_3p_chains = requests.get(f"{url}/?season={season}&server=Third_Party").json()['results']
        all_chains = dpow_3p_chains+dpow_main_chains+["KMD", "LTC", "BTC"]

        coin_info = requests.get(f"{THIS_SERVER}/api/info/coins/").json()['results']

        for chain in all_chains:

            coin_social = coin_social_row()
            coin_social.chain = chain
            coin_social.season = season
            coin_social.icon = ""
            coin_social.explorers = []

            if chain in coin_info:

                if "coins_info" in coin_info[chain]:
                    if "icon" in coin_info[chain]["coins_info"]:
                        coin_social.icon = coin_info[chain]["coins_info"]["icon"]
                        
                if "explorers" in coin_info[chain]:
                    coin_social.explorers = coin_info[chain]["explorers"]
                    
            else:
                logger.info(f"{chain} not in coin_info")

            if chain in chain_social:
                print(f"chain_social[chain]: {chain_social[chain]}")
                coin_social.discord = chain_social[chain]["discord"]
                coin_social.email = chain_social[chain]["email"]
                coin_social.github = chain_social[chain]["github"]
                coin_social.linkedin = chain_social[chain]["linkedin"]
                coin_social.mining_pools = chain_social[chain]["mining_pools"]
                coin_social.reddit = chain_social[chain]["reddit"]
                coin_social.telegram = chain_social[chain]["telegram"]
                coin_social.twitter = chain_social[chain]["twitter"]
                coin_social.website = chain_social[chain]["website"]
                coin_social.youtube = chain_social[chain]["youtube"]

            coin_social.update()
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
