#!/usr/bin/env python3
import os
import json
import requests

from kmd_ntx_api.notary_seasons import get_season, get_seasons_info

season = get_season()
seasons_info = get_seasons_info()
dpow_main_coins = seasons_info[season]["servers"]["Main"]["coins"]
dpow_3p_coins = seasons_info[season]["servers"]["Third_Party"]["coins"]
all_coins = dpow_main_coins + dpow_3p_coins

template = {}
for coin in all_coins:
    coin_info = requests.get(f"/api/info/coins/?coin={coin}").json()
    template.update({
        coin: {
                "discord": "",
                "icon": coin_info["coins_info"]["icon"],
                "github": "",
                "explorer": coin_info["explorers"],
                "telegram": "",
                "keybase": "",
                "twitter": "",
                "website": "",
                "youtube": ""
        }
    })
    try:
        repo_info = requests.get(f"https://raw.githubusercontent.com/smk762/coins/social/social/{coin}").json()[0]
    except:
        repo_info = {}
    for item in repo_info:
        template[coin].update({item:repo_info[item]})

with open(os.path.dirname(os.path.abspath(__file__))+'/social_coins.json', 'w+') as j:
    json.dump(template, j, indent = 4, sort_keys=True)
