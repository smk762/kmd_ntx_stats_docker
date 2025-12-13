#!/usr/bin/env python3.12
import requests
from random import choice
from django.db.models import Sum, Max
from kmd_ntx_api.cron import days_ago, get_time_since
from kmd_ntx_api.helper import get_or_none, get_notary_list
from kmd_ntx_api.query import get_mined_data, get_mined_count_season_data
from kmd_ntx_api.notary_seasons import get_season, get_page_season
from kmd_ntx_api.serializers import minedSerializer
from kmd_ntx_api.cache_data import cached
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


def get_nn_mining_summary(notary, season=None):
    """Return mining summary without HTTP self-calls to avoid deadlocks/timeouts."""
    if season is None:
        season = get_season()

    cache_key = cached.namespaced_key("mining", f"mining_summary_{season}_{notary}")
    cached_summary = cached.get_data(cache_key)
    if cached_summary:
        return cached_summary

    mining_summary = {
        "blocks_mined": 0,
        "sum_value_mined": 0,
        "max_value_mined": 0,
        "last_mined_block": "N/A",
        "last_mined_blocktime": 0,
        "time_since_mined": "N/A",
        "mined_last_24hrs": 0,
    }

    try:
        qs = get_mined_count_season_data(season).filter(name=notary).values().order_by("-last_mined_blocktime")
        if qs:
            row = qs[0]
            mining_summary.update({
                "blocks_mined": row.get("blocks_mined", 0),
                "sum_value_mined": row.get("sum_value_mined", 0),
                "max_value_mined": row.get("max_value_mined", 0),
                "last_mined_block": row.get("last_mined_block", "N/A"),
                "last_mined_blocktime": row.get("last_mined_blocktime", 0),
            })
            ts, ts_text = get_time_since(mining_summary["last_mined_blocktime"])
            mining_summary.update({
                "time_since_mined_ts": ts,
                "time_since_mined": ts_text,
            })
    except Exception as e:
        logger.warning(f"get_nn_mining_summary fallback for {notary}: {e}")

    try:
        mined_last_24hrs = float(get_notary_mined_last_24hrs(notary))
        mining_summary.update({"mined_last_24hrs": mined_last_24hrs})
    except Exception as e:
        logger.warning(f"get_nn_mining_summary 24h fallback for {notary}: {e}")

    try:
        cached.refresh(key=cache_key, data=mining_summary, force=True, expire=300)
    except Exception:
        pass

    return mining_summary


def warm_mining_cache(season=None):
    """
    Warm per-notary mining summaries with minimal queries:
    - One query for season aggregates (blocks/sum/max/last).
    - One grouped query for last-24h sums.
    """
    if season is None:
        season = get_season()

    cache_expire = 300
    summaries = {}

    # Base aggregates per notary for the season.
    # Pick the row with the most recent mined block per notary (max last_mined_blocktime).
    season_rows = (
        get_mined_count_season_data(season)
        .order_by("-last_mined_blocktime")
        .values("name", "blocks_mined", "sum_value_mined", "max_value_mined", "last_mined_block", "last_mined_blocktime")
    )
    for row in season_rows:
        name = row["name"]
        if name in summaries:
            continue  # already set the most recent row for this notary
        summaries[name] = {
            "blocks_mined": row.get("blocks_mined", 0),
            "sum_value_mined": row.get("sum_value_mined", 0),
            "max_value_mined": row.get("max_value_mined", 0),
            "last_mined_block": row.get("last_mined_block", "N/A"),
            "last_mined_blocktime": row.get("last_mined_blocktime", 0),
        }

    # 24h mined sums per notary (grouped)
    last_24h_rows = (
        get_mined_data_24hr()
        .values("name")
        .annotate(mined_last_24hrs=Sum("value"), last_blocktime=Max("block_time"))
    )
    last_24h_map = {row["name"]: float(row["mined_last_24hrs"] or 0) for row in last_24h_rows}

    # Compose final summaries and cache
    for name, summary in summaries.items():
        last_ts = summary.get("last_mined_blocktime", 0)
        ts, ts_text = get_time_since(last_ts)
        summary.update({
            "time_since_mined_ts": ts,
            "time_since_mined": ts_text,
            "mined_last_24hrs": last_24h_map.get(name, 0.0),
        })
        cache_key = cached.namespaced_key("mining", f"mining_summary_{season}_{name}")
        try:
            cached.refresh(key=cache_key, data=summary, force=True, expire=cache_expire)
        except Exception:
            pass

    return len(summaries)

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
        cache_key = cached.namespaced_key("mining", "mined_count_season")
        data = cached.get_data(cache_key, expire=300)
        if data is None:
            data = mined_data.aggregate(Sum('value'))['value__sum']
            cached.refresh(data={"val": str(data)}, force=True, key=cache_key, expire=300)
            return data
        else:
            return data["val"]
    except Exception as e:
        logger.error(e)
        return 0
    
    
def get_mined_count_24hr(mined_data):
    try:
        cache_key = cached.namespaced_key("mining", "mined_count_24hr")
        data = cached.get_data(cache_key, expire=300)
        if data is None:
            data = mined_data.filter(block_time__gt=str(days_ago(1))).aggregate(Sum('value'))['value__sum']
            cached.refresh(data={"val": str(data)}, force=True, key=cache_key, expire=300)
            return data
        else:
            return data["val"]
    except Exception as e:
        logger.error(e)
        return 0
    
    
def get_biggest_block_season(mined_data):
    try:
        cache_key = cached.namespaced_key("mining", "biggest_block_season")
        data = cached.get_data(cache_key, expire=300)
        if data is None:
            data = mined_data.order_by('-value').first()
            cached.refresh(data={"val": str(data)}, force=True, key=cache_key, expire=300)
            return data
        else:
            return data["val"]
    except Exception as e:
        logger.error(e)
        return 0    
    