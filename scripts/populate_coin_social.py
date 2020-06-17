#!/usr/bin/env python3
import os
import json
import time
import requests
import logging
import logging.handlers
import notary_lib

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

#r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/NotaryNodes/master/season4/coin_social.json")
#coin_social = r.json()

with open(os.path.dirname(os.path.abspath(__file__))+'/coins_social.json', 'r') as j:
    coin_social = json.load(j)


conn = connect_db()
cursor = conn.cursor()

season = "Season_4"
for chain in coin_social:
    row_list = [chain]
    for social in ['twitter', 'youtube', 'discord', 'telegram', 'github', 'explorer', 'website', 'icon']:
        if social in coin_social[chain]:
            row_list.append(coin_social[chain][social])
        else:
            row_list.append("")
    row_list.append(season)
    row_data = tuple(row_list)

    update_coin_social_tbl(conn, cursor, row_data)
   

cursor.close()

conn.close()
