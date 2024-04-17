#!/usr/bin/env python3
import requests
from random import choice
from django.db.models import Sum
from kmd_ntx_api.cron import days_ago, get_time_since
from kmd_ntx_api.helper import get_or_none, get_notary_list
from kmd_ntx_api.query import get_mined_data, get_mined_count_season_data
from kmd_ntx_api.notary_seasons import get_season, get_page_season
from kmd_ntx_api.serializers import minedSerializer
from kmd_ntx_api.cache_data import get_from_memcache, refresh_cache
from kmd_ntx_api.logger import logger


def get_mined_data_24hr():
    data = get_mined_data().filter(block_time__gt=str(days_ago(1)))
    return data


def get_notary_mined_last_24hrs(notary):
    data = get_mined_data_24hr().filter(name=notary)
    sum_mined = data.aggregate(Sum('value'))['value__sum']
    if not sum_mined:
        sum_mined = 0
    return sum_mined


def get_nn_mining_summary(notary, season=get_season()):

    url = f"http://127.0.0.1:8762/api/table/mined_count_season/?season={season}&name={notary}"
    mining_summary = requests.get(url).json()['results']
    if len(mining_summary) > 0:
        mining_summary = mining_summary[0]
        time_since_mined_ts, time_since_mined = get_time_since(mining_summary["last_mined_blocktime"])
        mining_summary.update({
            "time_since_mined_ts": time_since_mined_ts,
            "time_since_mined": time_since_mined
        })
    else:
        mining_summary = {
          "blocks_mined": 0,
          "sum_value_mined": 0,
          "max_value_mined": 0,
          "last_mined_block": "N/A",
          "last_mined_blocktime": "N/A",
          "time_since_mined": "N/A"
        }

    mined_last_24hrs = float(get_notary_mined_last_24hrs(notary))
    mining_summary.update({
        "mined_last_24hrs": mined_last_24hrs
    })
    
    return mining_summary

## API Functions

def get_mined_count_season_by_name(request):
    season = get_page_season(request)
    resp = {}

    data = get_mined_count_season_data(season).filter(blocks_mined__gte=10).values()
    for i in data:
        if i["name"] not in resp:
            resp.update({i["name"]: {}})
            for k, v in i.items():
                if k not in ["name", "season", "id"]:
                    resp[i["name"]].update({k:v})
        elif i["last_mined_blocktime"] > resp[i["name"]]["last_mined_blocktime"]:
            for k, v in i.items():
                if k not in ["name", "season", "id"]:
                    resp[i["name"]].update({k:v})            
    return resp

def get_notary_mining(request):
    notary = get_or_none(request, "notary")
    season = get_page_season(request)

    if not notary:
        notary = choice(get_notary_list(season))

    data = get_mined_data(season, notary).values().order_by('block_height')
    serializer = minedSerializer(data, many=True)
    return serializer.data


def get_mined_count_daily_by_name(request):
    season = get_page_season(request)
    resp = {}

    data = get_mined_count_season_data(season).filter(blocks_mined__gte=10).values()
    for i in data:
        if i["name"] not in resp:
            resp.update({i["name"]: {}})
        for k, v in i.items():
            if k not in ["name", "season", "id"]:
                resp[i["name"]].update({k:v})            
    return resp

def get_mined_count_season(mined_data):
    try:
        cache_key = "mined_count_season"
        data = get_from_memcache(cache_key, expire=300)
        if data is None:
            data = mined_data.aggregate(Sum('value'))['value__sum']
            refresh_cache(data={"val": str(data)}, force=True, key=cache_key, expire=300)
            return data
        else:
            return data["val"]
    except Exception as e:
        logger.error(e)
        return 0
    
    
def get_mined_count_24hr(mined_data):
    try:
        cache_key = "mined_count_24hr"
        data = get_from_memcache(cache_key, expire=300)
        if data is None:
            data = mined_data.filter(block_time__gt=str(days_ago(1))).aggregate(Sum('value'))['value__sum']
            refresh_cache(data={"val": str(data)}, force=True, key=cache_key, expire=300)
            return data
        else:
            return data["val"]
    except Exception as e:
        logger.error(e)
        return 0
    
    
def get_biggest_block_season(mined_data):
    try:
        cache_key = "biggest_block_season"
        data = get_from_memcache(cache_key, expire=300)
        if data is None:
            data = mined_data.order_by('-value').first()
            refresh_cache(data={"val": str(data)}, force=True, key=cache_key, expire=300)
            return data
        else:
            return data["val"]
    except Exception as e:
        logger.error(e)
        return 0    
    