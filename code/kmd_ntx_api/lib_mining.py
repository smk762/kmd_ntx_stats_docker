#!/usr/bin/env python3
import time
from django.db.models import Sum
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_query as query

def get_mined_count_season_by_name(request):
    season = helper.get_or_none(request, "season", SEASON)
    resp = {}

    data = query.get_mined_count_season_data(season).filter(blocks_mined__gte=10).values()
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


def get_mined_count_daily_by_name(request):
    season = helper.get_or_none(request, "season", SEASON)
    resp = {}

    data = query.get_mined_count_season_data(season).filter(blocks_mined__gte=10).values()
    for i in data:
        if i["name"] not in resp:
            resp.update({i["name"]: {}})
        for k, v in i.items():
            if k not in ["name", "season", "id"]:
                resp[i["name"]].update({k:v})            
    return resp


def get_nn_mining_summary(notary, season=None):
    if not season:
        season = SEASON

    url = f"{THIS_SERVER}/api/table/mined_count_season/?season={season}&name={notary}"
    mining_summary = requests.get(url).json()['results']
    if len(mining_summary) > 0:
        mining_summary = mining_summary[0]
        mining_summary.update({
            "time_since_mined": helper.get_time_since(mining_summary["last_mined_blocktime"])[1]
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


def get_mined_data_24hr():
    day_ago = int(time.time()) - SINCE_INTERVALS['day']
    data = query.get_mined_data().filter(block_time__gt=str(day_ago))
    return data


def get_notary_mined_last_24hrs(notary):
    data = get_mined_data_24hr().filter(name=notary)
    sum_mined = data.aggregate(Sum('value'))['value__sum']
    if not sum_mined:
        sum_mined = 0
    return sum_mined

