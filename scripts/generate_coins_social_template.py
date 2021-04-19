#!/usr/bin/env python3
import os
import json
import requests
from lib_const import *

url = f"{THIS_SERVER}/api/info/dpow_server_coins"
dpow_main_chains = requests.get(f"{url}/?season={season}&server=Main").json()['results']
dpow_3p_chains = requests.get(f"{url}/?season={season}&server=Third_Party").json()['results']


template = {}
for chain in dpow_main_chains:
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

with open(os.path.dirname(os.path.abspath(__file__))+'/coins_social.json', 'w+') as j:
    json.dump(template, j, indent = 4, sort_keys=True)
