#!/usr/bin/env python3.12
import os
import json
import time
import requests
from lib_const import *
from const_seasons import SEASONS
from decorators import *
from models import coin_social_row
import lib_helper as helper
import lib_urls as urls
from pathlib import Path
from typing import Dict, Any


@print_runtime
def generate_social_coins_template(season):

    all_coins = SEASONS.INFO[season]["coins"]
    try:
        url = urls.get_notary_nodes_repo_coin_social_url(season)
        repo_info = requests.get(url).json()
    except Exception as e:
        logger.error(f"Error getting info from {url} {e}")
        repo_info = {}
    template = {}
    for coin in all_coins:
        template.update({
            coin: {
                    "discord": "",
                    "email": "",
                    "explorers":[],
                    "github": "",
                    "linkedin": "",
                    "mining_pools":[],
                    "reddit": "",
                    "telegram": "",
                    "twitter": "",
                    "website": "",
                    "youtube": ""
            }
        })
    for coin in all_coins:
        if coin in repo_info:
            for item in repo_info[coin]:
                template[coin].update({item:repo_info[coin][item]})

        elif coin in TRANSLATE_COINS:
            
            for item in repo_info[coin]:
                template[helper.handle_translate_coins(coin)].update({item:repo_info[coin][item]})
                

    with open(f"{os.path.dirname(os.path.abspath(__file__))}/social_coins_{season.lower()}.json", 'w+') as j:
        json.dump(template, j, indent = 4, sort_keys=True)


def _season_number(season: str) -> int:
    try:
        return int(season.split("_")[1])
    except Exception:
        return 0


def fetch_prior_social_coins(current_season: str) -> Dict[str, Any]:
    """
    Look for local social_coins files from previous seasons (descending).
    Returns the first found as dict.
    """
    cur_num = _season_number(current_season)
    base = Path(__file__).resolve().parent
    for n in range(cur_num - 1, 0, -1):
        cand = base / f"social_coins_season_{n}.json"
        if cand.exists():
            try:
                data = json.loads(cand.read_text())
                if isinstance(data, dict):
                    logger.info(f"[backfill] Using prior social coins from {cand.name}")
                    return data
            except Exception as e:
                logger.debug(f"[backfill] Failed to read {cand}: {e}")
    logger.info("[backfill] No prior season social coins data found")
    return {}


def backfill_coin_social_fields(template: Dict[str, Any], prior: Dict[str, Any]) -> Dict[str, Any]:
    """Fill empty social fields from prior season data without overwriting existing values."""
    social_fields = ["discord", "email", "explorers", "github", "linkedin",
                     "mining_pools", "reddit", "telegram", "twitter", "website", "youtube"]
    for coin, data in prior.items():
        if coin not in template or not isinstance(data, dict):
            continue
        for field in social_fields:
            if field not in template[coin] or not template[coin][field]:
                if field in data and data[field]:
                    template[coin][field] = data[field]
    return template


@print_runtime
def populate_coins_social(season):
    try:
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/social_coins_{season.lower()}.json", 'r') as j:
            coin_social = json.load(j)

        all_coins = SEASONS.INFO[season]["coins"]
        coin_info = COINS_INFO

        for coin in all_coins:

            row = coin_social_row()
            row.coin = coin
            row.season = season
            row.icon = ""
            row.explorers = []

            if coin in coin_info:

                if "coins_info" in coin_info[coin]:
                    if "icon" in coin_info[coin]["coins_info"]:
                        row.icon = coin_info[coin]["coins_info"]["icon"]
                        
                if "explorers" in coin_info[coin]:
                    row.explorers = coin_info[coin]["explorers"]
                    
            else:
                logger.info(f"{coin} not in coin_info")

            if coin in coin_social:
                row.discord = coin_social[coin]["discord"]
                row.email = coin_social[coin]["email"]
                row.github = coin_social[coin]["github"]
                row.linkedin = coin_social[coin]["linkedin"]
                row.mining_pools = coin_social[coin]["mining_pools"]
                row.reddit = coin_social[coin]["reddit"]
                row.telegram = coin_social[coin]["telegram"]
                row.twitter = coin_social[coin]["twitter"]
                row.website = coin_social[coin]["website"]
                row.youtube = coin_social[coin]["youtube"]

            row.update()

        # Backfill empty social fields from prior seasons if available
        prior = fetch_prior_social_coins(season)
        if prior:
            coin_social = backfill_coin_social_fields(coin_social, prior)

        # Persist the enriched file for transparency/pushing
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/social_coins_{season.lower()}.json", 'w+') as j:
            json.dump(coin_social, j, indent=4, sort_keys=True)
    except Exception as e:
        logger.info(f"Error in [populate_coins_social]: {e}")


if __name__ == "__main__":

    logger.info(f"Preparing to populate [social_coins] table...")
    seasons = helper.get_active_seasons()
    for season in seasons:
        generate_social_coins_template(season)
        populate_coins_social(season)
    
    CURSOR.close()
    CONN.close()
