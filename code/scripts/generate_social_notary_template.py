#!/usr/bin/env python3
import os
import json
import requests
from lib_const import *
from lib_urls import get_dpow_server_coins_url
from lib_validate import *
from lib_helper import get_nn_region_split

s5_socials = requests.get("https://raw.githubusercontent.com/KomodoPlatform/NotaryNodes/master/season5/elected_nn_social.json").json()
season = "Season_6"

template = {}
for notary in NOTARY_PUBKEYS["Season_6"]["Main"]:
    nn, region = get_nn_region_split(notary)
    if nn not in template:
        template.update({
            nn: {
            "discord": "",
            "email": "",
            "github": "",
            "icon": "",
            "keybase": "",
            "regions": {},
            "telegram": "",
            "twitter": "",
            "website": "",
            "youtube": ""
            }
        })
    template[nn]["regions"].update({
        region: {
            "Main": {
                "KMD_address": "",
                "LTC_address": "",
                "pubkey": NOTARY_PUBKEYS["Season_6"]["Main"][notary]
            },
            "Third_Party": {
                "KMD_address": "",
                "pubkey": NOTARY_PUBKEYS["Season_6"]["Third_Party"][notary]
            }
        }
    })
    if nn in s5_socials:
        for k,v in s5_socials[nn].items():
            if v != "" and k != "regions":
                template[nn][k] = v

with open(os.path.dirname(os.path.abspath(__file__))+'/social_notaries_season_6.json', 'w+') as j:
    json.dump(template, j, indent = 4, sort_keys=True)
