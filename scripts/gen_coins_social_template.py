#!/usr/bin/env python3
import os
import json
import requests

r = requests.get("http://notary.earth:8762/api/info/coins/?dpow_active=1")
coins_data = r.json()

coins_list = list(coins_data['results'][0].keys())

template = {}
for chain in coins_list:
    template.update({
        chain: {
                "discord": "",
                "icon": "",
                "github": "",
                "explorer": "",
                "telegram": "",
                "twitter": "",
                "website": "",
                "youtube": ""
        }
    })

with open(os.path.dirname(os.path.abspath(__file__))+'/coins_social.json', 'w+') as j:
    json.dump(template, j, indent = 4, sort_keys=True)
