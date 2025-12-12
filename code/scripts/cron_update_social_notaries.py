#!/usr/bin/env python3.12
import time
import os
import json
import requests
from logger import logger
from lib_const import *
from const_seasons import SEASONS
from decorators import *
import lib_helper as helper
from lib_urls import get_notary_nodes_repo_elected_nn_social_url, get_notary_addresses_url
from models import nn_social_row
from logger import logger
from typing import Dict, Any
from pathlib import Path
import hashlib
from base58 import b58encode_check
def calc_addr_from_pubkey_local(coin: str, pubkey: str) -> str | None:
    try:
        prefixes = {"KMD": 60, "LTC": 48}
        prefix = prefixes.get(coin)
        if prefix is None:
            return None
        pk_bytes = bytes.fromhex(pubkey)
        h160 = hashlib.new('ripemd160', hashlib.sha256(pk_bytes).digest()).digest()
        return b58encode_check(bytes([prefix]) + h160).decode()
    except Exception as e:
        logger.debug(f"[backfill] addr derivation failed for {coin} {pubkey}: {e}")
        return None

PLACEHOLDER_NOTARIES = {"USER", "PLACEHOLDER"}


def _season_number(season: str) -> int:
    try:
        return int(season.split("_")[1])
    except Exception:
        return 0


def fetch_prior_social_data(current_season: str) -> Dict[str, Any]:
    """
    Try to fetch elected_nn_social.json from previous seasons (descending) and
    return the first one found. This allows backfilling social links when the
    current season file is empty.
    """
    cur_num = _season_number(current_season)
    for n in range(cur_num - 1, 0, -1):
        season_slug = f"season{n}"
        url = f"https://raw.githubusercontent.com/KomodoPlatform/NotaryNodes/master/{season_slug}/elected_nn_social.json"
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict) and data:
                    logger.info(f"[backfill] Using prior social data from {url}")
                    return data
        except Exception as e:
            logger.debug(f"[backfill] Failed to fetch {url}: {e}")
    logger.info("[backfill] No prior season social data found")
    return {}


def backfill_social_fields(template: Dict[str, Any], prior: Dict[str, Any]) -> Dict[str, Any]:
    """Fill empty social fields from prior season data without overwriting existing values."""
    social_fields = ["discord", "email", "github", "icon", "keybase", "telegram", "twitter", "website", "youtube"]

    for notary_name, data in prior.items():
        if notary_name in PLACEHOLDER_NOTARIES:
            continue
        if not isinstance(data, dict):
            continue
        if notary_name not in template:
            continue

        # Shallow social fields
        for field in social_fields:
            if not template[notary_name].get(field) and data.get(field):
                template[notary_name][field] = data[field]

    return template


def backfill_regions_from_pubkeys(template: Dict[str, Any], season: str) -> Dict[str, Any]:
    """
    Use notary_pubkeys.json for the given season to ensure regions/tier data exist,
    and derive KMD/LTC addresses from pubkeys when missing.
    """
    try:
        cache_dir = Path(__file__).resolve().parent.parent / "cache"
        pubkeys_path = cache_dir / "notary_pubkeys.json"
        if not pubkeys_path.exists():
            logger.warning(f"[backfill] notary_pubkeys.json missing at {pubkeys_path}")
            return template
        pub_data = json.loads(pubkeys_path.read_text())
        season_data = pub_data.get(season, {})
        if not season_data:
            logger.warning(f"[backfill] No pubkey data for {season}")
            return template

        for tier_name in ("Main", "Third_Party"):
            tier_map = season_data.get(tier_name, {})
            for notary_region, pubkey in tier_map.items():
                if not isinstance(pubkey, str):
                    continue
                # split notary and region by last underscore
                if "_" not in notary_region:
                    continue
                notary_name = "_".join(notary_region.split("_")[:-1])
                region = notary_region.split("_")[-1]
                if notary_name in PLACEHOLDER_NOTARIES:
                    continue
                if notary_name not in template:
                    continue
                template[notary_name].setdefault("regions", {})
                template[notary_name]["regions"].setdefault(region, {})
                template[notary_name]["regions"][region].setdefault(tier_name, {})
                tier = template[notary_name]["regions"][region][tier_name]
                tier["pubkey"] = pubkey
                kmd_addr = calc_addr_from_pubkey_local("KMD", pubkey)
                ltc_addr = calc_addr_from_pubkey_local("LTC", pubkey)
                if isinstance(kmd_addr, str):
                    tier["KMD_address"] = kmd_addr
                if isinstance(ltc_addr, str):
                    tier["LTC_address"] = ltc_addr
        return template
    except Exception as e:
        logger.warning(f"[backfill] Failed to backfill regions from pubkeys: {e}")
        return template


@print_runtime
def generate_social_notaries_template(season):
    notaries = helper.get_season_notaries(season)
    try:
        repo_info = requests.get(get_notary_nodes_repo_elected_nn_social_url(season)).json()
    except Exception as e:
        logger.warning(e)
        repo_info = {}
    template = {}
    for notary in notaries:
        notary_name, region = helper.get_nn_region_split(notary)
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
        if notary_name not in template or notary_name in PLACEHOLDER_NOTARIES:
            logger.warning(f"[generate_social_notaries_template] Skipping unexpected notary key from repo: {notary_name}")
            continue
        for item in repo_info[notary_name]:
            if item != "regions":
                template[notary_name].update({item:repo_info[notary_name][item]})

    for notary in notaries:
        notary_name, notary_region = helper.get_nn_region_split(notary)
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

    # Backfill social fields from prior seasons if current season data is sparse/empty
    prior_data = fetch_prior_social_data(season)
    if prior_data:
        template = backfill_social_fields(template, prior_data)

    # Backfill regions/addresses from pubkeys for this season
    template = backfill_regions_from_pubkeys(template, f"Season_{season.split('_')[-1]}")

    with open(f"{os.path.dirname(os.path.abspath(__file__))}/social_notaries_{season.lower()}.json", 'w+') as j:
        json.dump(template, j, indent = 4, sort_keys=True)


@print_runtime
def populate_social_notaries(season):
    try:
        url = get_notary_nodes_repo_elected_nn_social_url(season)
        r = requests.get(url)
        elected_nn_social = r.json()

        for notary in SEASONS.INFO[season]["notaries"]:
            nn_social = nn_social_row()
            notary_name, region = helper.get_nn_region_split(notary)
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
                # Only warn if repo data is non-empty and the missing entry is unexpected (skip placeholders like USER)
                if elected_nn_social:
                    logger.warning(f"{notary_name} not in repo keys: {list(elected_nn_social.keys())}")
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
        for notary_name in SEASONS.INFO[season]["notaries"]:
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
            if item[0] not in SEASONS.INFO[season]["notaries"]:
                sql = f"DELETE FROM nn_social WHERE notary = '{item[0]}' AND season = '{season}';"
                logger.warning(f"Deleting [nn_social] row: {season} {item[0]}")
                CURSOR.execute(sql)
                CONN.commit()
    except Exception as e:
        logger.error(f"Error in [populate_social_notaries]: {e}")


if __name__ == "__main__":
    logger.info(SEASONS.EXCLUDED)
    season = "Season_8"
    logger.info(f"Preparing to populate {season} [social_notaries] table...")
    populate_social_notaries(season)
    remove_invalid_notaries(season)
    generate_social_notaries_template(season)
    
    CURSOR.close()
    CONN.close()
