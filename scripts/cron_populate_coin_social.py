#!/usr/bin/env python3
import os
import json
import time
import requests
from lib_const import *
from models import coin_social_row


#r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/NotaryNodes/master/season4/coin_social.json")
#coin_social = r.json()
try:
    with open(os.path.dirname(os.path.abspath(__file__))+'/coins_social.json', 'r') as j:
        chain_social = json.load(j)
except:
    print(f"coins_social.json does not exist! Run generate_coins_social_template.py to create it, then fill in known social data.")

season = "Season_4"
for chain in chain_social:
    coin_social = coin_social_row()
    coin_social.coin = chain
    coin_social.season = season
    coin_social.discord = chain_social[chain]["discord"]
    coin_social.keybase = chain_social[chain]["explorer"]
    coin_social.github = chain_social[chain]["github"]
    coin_social.icon = chain_social[chain]["icon"]
    coin_social.telegram = chain_social[chain]["telegram"]
    coin_social.twitter = chain_social[chain]["twitter"]
    coin_social.website = chain_social[chain]["website"]
    coin_social.youtube = chain_social[chain]["youtube"]
    coin_social.update()
    
CURSOR.close()
CONN.close()
