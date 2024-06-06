#!/usr/bin/env python3
import time
from kmd_ntx_api.const import SINCE_INTERVALS
from kmd_ntx_api.struct import default_regions_info
from kmd_ntx_api.logger import logger
from kmd_ntx_api.memcached import MEMCACHE
from kmd_ntx_api.cache_data import get_from_memcache
from kmd_ntx_api.cache_data import notary_seasons_cache, seasons_info_cache, refresh_cache, SEASONS_INFO_PATH, NOTARY_SEASONS_PATH

# TODO: reduce calls without `notary_seasons` param
def get_season(timestamp: int=int(time.time()), notary_seasons=None) -> str:
    logger.calc("get_season")
    if notary_seasons is None:
        notary_seasons = get_from_memcache("notary_seasons", expire=86400)
    for season in notary_seasons:
        if 'post_season_end_time' in notary_seasons[season]:
            end_time = notary_seasons[season]['post_season_end_time']
        else:
            end_time = notary_seasons[season]['end_time']
        if timestamp >= notary_seasons[season]['start_time'] and timestamp <= end_time:
            return season
    return "Unofficial"


# TODO: reduce calls without `seasons_info` param
def get_page_season(request, seasons_info=None):
    logger.calc("get_page_season")
    if "season" in request.GET:
        season = request.GET["season"]
        if season.isnumeric():
            return f"Season_{request.GET['season']}"
        if seasons_info is None:
            seasons_info = get_seasons_info()
        if season.title() in seasons_info:
            return season.title()
    return get_season()


# Cached
def get_notary_seasons():
    '''Only used in `notary_profile_view` (Notary Profile page)'''
    logger.calc("get_notary_seasons")
    ntx_seasons = get_from_memcache("notary_seasons", expire=86400)
    if len(ntx_seasons) == 0:
        ntx_seasons = {}
        pubkeys = get_from_memcache("notary_pubkeys", expire=86400)
        for season in pubkeys:
            for server in pubkeys[season]:
                for notary in pubkeys[season][server]:
                    if notary not in ntx_seasons:
                        ntx_seasons.update({notary:[]})
                    season = season.replace(".5", "")
                    ntx_seasons[notary].append(season)
        for notary in ntx_seasons:
            ntx_seasons[notary] = list(set(ntx_seasons[notary]))
            ntx_seasons[notary].sort()
        refresh_cache(
            data=ntx_seasons,
            key="notary_seasons",
            expire=86400
        )
    return ntx_seasons


def get_seasons_info() -> dict:
    logger.calc("get_seasons_info")
    seasons = seasons_info_cache()
    if seasons is None:
        pubkeys = get_from_memcache("notary_pubkeys", expire=86400)
        
        seasons = {i: {} for i in pubkeys.keys()}
        for season in pubkeys:
            notaries = list(pubkeys[season]["Main"].keys())
            notaries.sort()
            seasons[season].update({
                "notaries": notaries,
                "regions": default_regions_info()
            })
            for notary in notaries:
                region = notary.split("_")[-1]
                if region not in seasons[season]["regions"].keys():
                    region = "DEV"
                if notary not in seasons[season]["regions"][region]['nodes']:
                    seasons[season]["regions"][region]['nodes'].append(notary)
        refresh_cache(
            path=SEASONS_INFO_PATH,
            data=seasons,
            force=True,
            key="seasons_info_cache",
            expire=3600
        )
    return seasons


# Possibly unused

def get_timespan_season(start, end):
    logger.calc("get_timespan_season")
    season = get_season()
    if not start:
        start = time.time() - SINCE_INTERVALS['day']
    if not end:
        end = time.time()
    else:
        season = get_season((end+start)/2)
    return int(float(start)), int(float(end)), season
