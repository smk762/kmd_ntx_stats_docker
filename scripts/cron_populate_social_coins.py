#!/usr/bin/env python3
import os
import json
import time
import requests
from lib_const import *
from lib_notary import get_season
from models import coin_social_row


def generate_social_coins_template(season):
    url = f"{THIS_SERVER}/api/info/dpow_server_coins"
    dpow_main_chains = requests.get(f"{url}/?season={season}&server=Main").json()['results']
    dpow_3p_chains = requests.get(f"{url}/?season={season}&server=Third_Party").json()['results']
    all_chains = dpow_3p_chains+dpow_main_chains+["KMD", "LTC", "BTC"]

    template = {}
    for chain in all_chains:
        template.update({
            chain: {
                    "discord": "",
                    "github": "",
                    "telegram": "",
                    "keybase": "",
                    "twitter": "",
                    "website": "",
                    "youtube": ""
            }
        })
        try:
            repo_info = request.get(f"https://raw.githubusercontent.com/smk762/coins/social/social/{chain}").json()[0]
        except:
            repo_info = {}
        for item in repo_info:
            template[chain].update({item:repo_info[item]})

    with open(f"{os.path.dirname(os.path.abspath(__file__))}/social_coins_{season.lower()}.json", 'w+') as j:
        json.dump(template, j, indent = 4, sort_keys=True)


def update_coins_social(season):
    try:
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/social_coins_{season.lower()}.json", 'r') as j:
            chain_social = json.load(j)

        url = f"{THIS_SERVER}/api/info/dpow_server_coins"
        dpow_main_chains = requests.get(f"{url}/?season={season}&server=Main").json()['results']
        dpow_3p_chains = requests.get(f"{url}/?season={season}&server=Third_Party").json()['results']
        all_chains = dpow_3p_chains+dpow_main_chains+["KMD", "LTC", "BTC"]

        for chain in all_chains:

            coin_social = coin_social_row()

            coin_social.coin = chain
            coin_social.season = season

            coin_info = requests.get(f"{THIS_SERVER}/api/info/coins/?chain={chain}").json()['results']

            if chain in coin_info:
                if "coins_info" in coin_info[chain]:
                    if "icon" in coin_info[chain]["coins_info"]:
                        coin_social.icon = coin_info[chain]["coins_info"]["icon"]   

            if chain in chain_social:
                coin_social.github = chain_social[chain]["github"]
                coin_social.discord = chain_social[chain]["discord"]
                coin_social.keybase = chain_social[chain]["keybase"]
                coin_social.twitter = chain_social[chain]["twitter"]
                coin_social.website = chain_social[chain]["website"]
                coin_social.youtube = chain_social[chain]["youtube"]
                coin_social.telegram = chain_social[chain]["telegram"]

            coin_social.update()
    except Exception as e:
        print(e)
        print(f"social_coins_{season}.json does not exist!")


if __name__ == "__main__":

    logger.info(f"Preparing to populate [social_coins] table...")
    for season in SEASONS_INFO:
        generate_social_coins_template(season)
        update_coins_social(season)
    
    CURSOR.close()
    CONN.close()
