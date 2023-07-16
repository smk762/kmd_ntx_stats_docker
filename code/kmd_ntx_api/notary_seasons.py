#!/usr/bin/env python3
import time
import struct
from logger import logger
import cache_data
import kmd_ntx_api.const as const
from kmd_ntx_api.cache_data import notary_pubkeys


def get_seasons_info() -> dict:
    seasons = cache_data.seasons()
    for season in seasons:
        pubkeys = cache_data.notary_pubkeys()
        if season in pubkeys:
            seasons[season].update({
                "regions": struct.default_regions_info()
            })
            notaries = list(pubkeys[season]["Main"].keys())
            notaries.sort()
            seasons[season].update({
                "notaries": notaries
            })
            for notary in notaries:
                region = notary.split("_")[-1]
                if region not in seasons[season]["regions"].keys():
                    region = "DEV"
                seasons[season]["regions"][region]['nodes'].append(notary)


def get_season(timestamp: int=int(time.time())) -> str:
    seasons = cache_data.seasons()
    for season in seasons:
        if seasons:
            if 'post_season_end_time' in seasons[season]:
                end_time = seasons[season]['post_season_end_time']
            else:
                end_time = seasons[season]['end_time']
        else:
            end_time = seasons[season]['end_time']
        if timestamp >= seasons[season]['start_time'] and timestamp <= end_time:
            return season
    return "Unofficial"


def get_timespan_season(start, end):
    season = get_season()
    if not start:
        start = time.time() - const.SINCE_INTERVALS['day']
    if not end:
        end = time.time()
    else:
        season = get_season((end+start)/2)
    return int(float(start)), int(float(end)), season


def get_page_season(request):
    if "season" in request.GET:
        if request.GET["season"].isnumeric():
            return f"Season_{request.GET['season']}"
        seasons_info = get_seasons_info()
        if request.GET["season"].title() in seasons_info:
            return request.GET["season"].title()
    return get_season()


def get_notary_seasons():
    ntx_seasons = {}
    pubkeys = notary_pubkeys()
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

    return ntx_seasons

