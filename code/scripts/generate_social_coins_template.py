#!/usr/bin/env python3
import os
import json
import requests
from lib_const import *
from lib_urls import get_dpow_server_coins_url
from lib_validate import *


season = get_season()

dpow_main_coins = SEASONS_INFO[season]["servers"]["Main"]["coins"]
dpow_3p_coins = SEASONS_INFO[season]["servers"]["Third_Party"]["coins"]

template = {}
for chain in all_chains:
    coin_info = requests.get(f"{THIS_SERVER}/api/info/coins/?chain={chain}").json()
    template.update({
        chain: {
                "discord": "",
                "icon": coin_info["coins_info"]["icon"],
                "github": "",
                "explorer": coin_info[explorers],
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

with open(os.path.dirname(os.path.abspath(__file__))+'/social_coins.json', 'w+') as j:
    json.dump(template, j, indent = 4, sort_keys=True)
