#!/usr/bin/env python3.12
import time

from kmd_ntx_api.const import SINCE_INTERVALS
from kmd_ntx_api.pubkeys import NOTARY_PUBKEYS
from kmd_ntx_api.seasons import SEASONS_DATA
from kmd_ntx_api.struct import default_regions_info
from kmd_ntx_api.logger import logger
from kmd_ntx_api.cache_data import cached

# TODO: reduce calls without `notary_seasons` param
def get_season(timestamp: int=int(time.time()), notary_seasons=None) -> str:
    if notary_seasons is None:
        notary_seasons = cached.get_data("notary_seasons", expire=86400)
    for season in notary_seasons:
        if 'post_season_end_time' in notary_seasons[season]:
            end_time = notary_seasons[season]['post_season_end_time']
        else:
            end_time = notary_seasons[season]['end_time']
        if timestamp >= notary_seasons[season]['start_time'] and timestamp <= end_time:
            return season
    return "Unofficial"


# TODO: reduce calls without `seasons_info` param
def get_page_season(request, seasons_info=None, default="Season_8"):
    if "season" in request.GET:
        season = request.GET["season"]
        if season.isnumeric():
            return f"Season_{request.GET['season']}"
        if seasons_info is None:
            seasons_info = get_seasons_info()
        if season.title() in seasons_info:
            return season.title()
    if default is None:
        return get_season()
    return default


# Cached
def get_notary_seasons():
    '''Only used in `notary_profile_view` (Notary Profile page)'''
    ntx_seasons = cached.get_data("notary_seasons", expire=86400)
    if len(ntx_seasons) == 0:
        ntx_seasons = {}
        for season in NOTARY_PUBKEYS:
            for server in NOTARY_PUBKEYS[season]:
                for notary in NOTARY_PUBKEYS[season][server]:
                    if notary not in ntx_seasons:
                        ntx_seasons.update({notary:[]})
                    season = season.replace(".5", "")
                    ntx_seasons[notary].append(season)
        for notary in ntx_seasons:
            ntx_seasons[notary] = list(set(ntx_seasons[notary]))
            ntx_seasons[notary].sort()
        cached.refresh(
            data=ntx_seasons,
            key="notary_seasons",
            expire=86400
        )
    return ntx_seasons


def get_seasons_info() -> dict:
    seasons = cached.client.get('notary_seasons')
    if seasons is None:
        seasons = SEASONS_DATA
        for season in SEASONS_DATA:
            if season in NOTARY_PUBKEYS:
                notaries = get_season_notaries(season)
                seasons[season].update({
                    "servers": {},
                    "notaries": notaries,
                    "regions": default_regions_info()
                })
                for notary in notaries:
                    region = notary.split("_")[-1]
                    if region not in seasons[season]["regions"].keys():
                        region = "DEV"
                    if notary not in seasons[season]["regions"][region]['nodes']:
                        seasons[season]["regions"][region]['nodes'].append(notary)
                for server in NOTARY_PUBKEYS[season]:
                    seasons[season]["servers"].update({server: {}})
                # TODO: Add epochs
                # TODO: Add coins for season / server / epoch
            elif season.lower().find("testnet") == -1:
                logger.warning(f"{season} not in NOTARY_PUBKEYS!")
                    
        cached.refresh(
            data=seasons,
            force=True,
            key="notary_seasons",
            expire=86400
        )
    return seasons


def get_season_notaries(season):
    notaries = list(NOTARY_PUBKEYS[season]["Main"].keys())
    notaries.sort()
    return notaries

# Possibly unused

def get_timespan_season(start, end):
    season = get_season()
    if not start:
        start = time.time() - SINCE_INTERVALS['day']
    if not end:
        end = time.time()
    else:
        season = get_season((end+start)/2)
    return int(float(start)), int(float(end)), season
