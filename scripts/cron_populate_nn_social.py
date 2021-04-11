#!/usr/bin/env python3
import time
import requests
import logging
import logging.handlers
from lib_const import *
from models import nn_social_row


r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/NotaryNodes/master/season4/elected_nn_social.json")
elected_nn_social = r.json()

season = "Season_4"
for notary in NOTARY_PUBKEYS['Season_4']:
    nn_social = nn_social_row()
    notary_name = notary.split("_")[0]
    for region in elected_nn_social[notary_name]['regions']:
        nn_social.notary = f"{notary_name}_{region}"
        nn_social.season = season
        nn_social.twitter = elected_nn_social[notary_name]["twitter"]
        nn_social.youtube = elected_nn_social[notary_name]["youtube"]
        nn_social.discord = elected_nn_social[notary_name]["discord"]
        nn_social.telegram = elected_nn_social[notary_name]["telegram"]
        nn_social.github = elected_nn_social[notary_name]["github"]
        nn_social.keybase = elected_nn_social[notary_name]["keybase"]
        nn_social.website = elected_nn_social[notary_name]["website"]
        nn_social.icon = elected_nn_social[notary_name]["icon"]
        nn_social.update()
    

r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/NotaryNodes/master/season4/elected_nn_social.json")
elected_nn_social = r.json()

season = "Season_5_Testnet"
for notary in NOTARY_PUBKEYS[season]:
    nn_social = nn_social_row()
    nn_social.notary = f"{notary}"
    nn_social.season = season
    nn_social.update()

# e.g. jorian changed name, used same pubkey in testnet
sql = "SELECT notary FROM nn_social WHERE \
       season = '"+str(season)+"' ORDER BY notary ASC;"
CURSOR.execute(sql)
try:
    results = CURSOR.fetchall()
    for item in results:
        if item[0] not in NOTARY_PUBKEYS[season]:
            sql = f"DELETE FROM nn_social WHERE notary = '{item[0]}' AND season = '{season}';"
            logger.warning(f"Deleting [nn_social] row: {season} {item[0]}")
            CURSOR.execute(sql)
            CONN.commit()
except:
    pass

    

CURSOR.close()
CONN.close()
