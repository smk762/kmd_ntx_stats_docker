#!/usr/bin/env python3
import time
import json
import requests
import logging
import logging.handlers
from lib_const import *
from decorators import *
from lib_helper import get_season_notaries, get_nn_region_split
from lib_urls import get_notary_nodes_repo_elected_nn_social_url, get_notary_addresses_url
from models import nn_social_row


@print_runtime
def generate_social_notaries_template(season):
    notaries = get_season_notaries(season)
    try:
        repo_info = requests.get(get_notary_nodes_repo_elected_nn_social_url(season)).json()
    except Exception as e:
        logger.warning(e)
        repo_info = {}
    template = {}
    for notary in notaries:
        notary_name, region = get_nn_region_split(notary)
        template.update({
            notary_name: {
                "discord": "",
                "icon": "",
                "github": "",
                "email": "",
                "keybase": "",
                "telegram": "",
                "twitter": "",
                "website": "",
                "youtube": "",
                "regions": {}
            }
        })
    for notary_name in repo_info:
        for item in repo_info[notary_name]:
            if item != "regions":
                template[notary_name].update({item:repo_info[notary_name][item]})

    for notary in notaries:
        notary_name, notary_region = get_nn_region_split(notary)
        if notary_region not in template[notary_name]["regions"]:
            notary_addresses = requests.get(get_notary_addresses_url(season, notary)).json()
            template[notary_name]["regions"].update({
                notary_region:{}
            })
            if "Main" in notary_addresses[season]:
                template[notary_name]["regions"][notary_region].update({
                    "Main": {
                        "pubkey": notary_addresses[season]["Main"][notary]["pubkey"],
                        "KMD_address": notary_addresses[season]["Main"][notary]["addresses"]["KMD"],
                        "LTC_address": notary_addresses[season]["Main"][notary]["addresses"]["LTC"]
                    },                    
                })
            if "Third_Party" in notary_addresses[season]:
                template[notary_name]["regions"][notary_region].update({
                    "Third_Party": {
                        "pubkey": notary_addresses[season]["Third_Party"][notary]["pubkey"],
                        "KMD_address": notary_addresses[season]["Third_Party"][notary]["addresses"]["KMD"]
                    },                    
                })

    with open(f"{os.path.dirname(os.path.abspath(__file__))}/social_notaries_{season.lower()}.json", 'w+') as j:
        json.dump(template, j, indent = 4, sort_keys=True)


@print_runtime
def populate_social_notaries(season):
    try:
        url = get_notary_nodes_repo_elected_nn_social_url(season)
        r = requests.get(url)
        elected_nn_social = r.json()

        for notary in SEASONS_INFO[season]["notaries"]:
            nn_social = nn_social_row()
            notary_name, region = get_nn_region_split(notary)
            if notary_name in list(elected_nn_social.keys()):

                for region in elected_nn_social[notary_name]['regions']:
                    nn_social.notary = f"{notary_name}_{region}"
                    nn_social.season = season
                    if "twitter" in elected_nn_social[notary_name]:
                        nn_social.twitter = elected_nn_social[notary_name]["twitter"]
                    else:
                        nn_social.twitter = ""

                    if "youtube" in elected_nn_social[notary_name]:
                        nn_social.youtube = elected_nn_social[notary_name]["youtube"]
                    else:
                        nn_social.youtube = ""

                    if "email" in elected_nn_social[notary_name]:
                        nn_social.email = elected_nn_social[notary_name]["email"]
                    else:
                        nn_social.email = ""

                    if "discord" in elected_nn_social[notary_name].keys():
                        nn_social.discord = elected_nn_social[notary_name]["discord"]
                    else:
                        nn_social.discord = ""

                    if "telegram" in elected_nn_social[notary_name]:
                        nn_social.telegram = elected_nn_social[notary_name]["telegram"]
                    else:
                        nn_social.telegram = ""

                    if "github" in list(elected_nn_social[notary_name].keys()):
                        nn_social.github = elected_nn_social[notary_name]["github"]
                    else:
                        nn_social.github = ""

                    if "keybase" in elected_nn_social[notary_name]:
                        nn_social.keybase = elected_nn_social[notary_name]["keybase"]
                    else:
                        nn_social.keybase = ""

                    if "website" in elected_nn_social[notary_name]:
                        nn_social.website = elected_nn_social[notary_name]["website"]
                    else:
                        nn_social.website = ""

                    if "icon" in elected_nn_social[notary_name]:
                        nn_social.icon = elected_nn_social[notary_name]["icon"]
                    else:
                        nn_social.icon = ""

                    nn_social.update()
            else:
                logger.warning(f"{notary_name} not in {list(elected_nn_social.keys())}")
                nn_social = nn_social_row()
                nn_social.notary = notary
                nn_social.season = season
                nn_social.twitter = ""
                nn_social.youtube = ""
                nn_social.discord = ""
                nn_social.email = ""
                nn_social.telegram = ""
                nn_social.github = ""
                nn_social.keybase = ""
                nn_social.website = ""
                nn_social.icon = ""
                nn_social.update()

    except Exception as e:
        logger.warning(f"{url} returns 404? {e}")
        for notary_name in SEASONS_INFO[season]["notaries"]:
            nn_social = nn_social_row()
            nn_social.notary = f"{notary_name}"
            nn_social.season = season
            nn_social.twitter = ""
            nn_social.youtube = ""
            nn_social.discord = ""
            nn_social.email = ""
            nn_social.telegram = ""
            nn_social.github = ""
            nn_social.keybase = ""
            nn_social.website = ""
            nn_social.icon = ""
            nn_social.update()


@print_runtime
def remove_invalid_notaries(season):
    # e.g. jorian changed name in Testnet, used same pubkey
    sql = "SELECT notary FROM nn_social WHERE \
           season = '"+str(season)+"' ORDER BY notary ASC;"
    CURSOR.execute(sql)
    try:
        results = CURSOR.fetchall()
        for item in results:
            if item[0] not in SEASONS_INFO[season]["notaries"]:
                sql = f"DELETE FROM nn_social WHERE notary = '{item[0]}' AND season = '{season}';"
                logger.warning(f"Deleting [nn_social] row: {season} {item[0]}")
                CURSOR.execute(sql)
                CONN.commit()
    except Exception as e:
        logger.error(f"Error in [populate_social_notaries]: {e}")


if __name__ == "__main__":
    print(EXCLUDED_SEASONS)
    season = "Season_7"
    logger.info(f"Preparing to populate {season} [social_notaries] table...")
    populate_social_notaries(season)
    remove_invalid_notaries(season)
    generate_social_notaries_template(season)
    
    CURSOR.close()
    CONN.close()
