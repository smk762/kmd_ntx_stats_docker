#!/usr/bin/env python3
import os
import json
import time
import requests
from lib_const import *
from lib_notary import get_season
from models import coin_social_row


season = get_season(time.time())

#r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/NotaryNodes/master/season4/coin_social.json")
#coin_social = r.json()
try:
    with open(os.path.dirname(os.path.abspath(__file__))+'/coins_social.json', 'r') as j:
        chain_social = json.load(j)
except:
    print(f"coins_social.json does not exist! Run generate_coins_social_template.py to create it, then fill in known social data.")

url = f"{THIS_SERVER}/api/info/dpow_server_coins"
dpow_main_chains = requests.get(f"{url}/?season={season}&server=Main").json()['results']
dpow_3p_chains = requests.get(f"{url}/?season={season}&server=Third_Party").json()['results']

chains = list(set(dpow_3p_chains+dpow_main_chains+list(chain_social.keys())))

for chain in chains:

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
    
CURSOR.close()
CONN.close()
