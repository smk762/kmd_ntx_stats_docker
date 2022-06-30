#!/usr/bin/env python3
import time
import json
import math
import random
import logging
import requests
import string
import itertools
import datetime
from datetime import datetime as dt
from datetime import timezone as tz
from calendar import monthrange
from django.http import JsonResponse
from kmd_ntx_api.lib_const import *
from kmd_ntx_api.navigation import NAV_DATA
import kmd_ntx_api.lib_struct as struct


def keys_to_list(_dict):
    _list = list(_dict.keys())
    _list.sort()
    return _list


def get_nn_region_split(notary):
    x = notary.split("_")
    region = x[-1]
    nn = notary.replace(f"_{region}", "")
    return nn, region


def has_error(_dict):
    if "error" in _dict:
        return True
    return False

def get_month_epoch_range(year=None, month=None):
    if not year or not month:
        dt_today = datetime.date.today()
        year = dt_today.year
        month = dt_today.month

    d = datetime.date(int(year), int(month), 1)
    ds_time = time.daylight * SINCE_INTERVALS['hour']
    start = time.mktime(d.timetuple()) - time.timezone + ds_time
    last_day = monthrange(int(year), int(month))[1]
    d = datetime.date(int(year), int(month), last_day)
    end = time.mktime(d.timetuple()) - time.timezone + ds_time + SINCE_INTERVALS['day'] - 1
    return start, end, last_day

def get_timespan_season(start, end):
    season = SEASON
    if not start:
        start = time.time() - SINCE_INTERVALS['day']
    if not end:
        end = time.time()
    else:
        season = get_season((end+start)/2)
    return int(float(start)), int(float(end)), season


def qset_values_to_list(qset_vals):
    table_data = []
    for item in qset_vals:
        table_data.append([v for k, v in item.items()])
    return table_data


def json_resp(resp, filters=None, params=None):

    data = {}
    if filters:
        data.update({"filters": filters})

    if params:
        data.update({"params": params})

    if has_error(resp):
        data.update({"error": resp["error"]})

    if "next" in resp:
        data.update({"next": resp["next"]})

    if "previous" in resp:
        data.update({"previous": resp["previous"]})

    if "count" in resp:
        data.update({"count": resp["count"]})
    else:
        data.update({"count": len(resp)})

    if "results" in resp:
        data.update({"results": resp["results"]})
    else:
        data.update({"results": resp})

    return JsonResponse(data)


def get_chart_json(data, axis_labels, chart_label, total):
    return {
        "chartdata": data,
        "labels": axis_labels,
        "chartLabel": chart_label,
        "total": total
    }

def append_unique(list_, item):
    if item not in list_:
        list_.append(item)
        return True
    return False


def update_unique(dict_, key, val):
    if key not in dict_:
        dict_.update({key:val})
        return True
    return False


def get_or_none(request, key, default=None):
    val = request.GET[key] if key in request.GET else None
    if default and not val:
        return default
    return val
    

def get_notary_clean(notary):
    return notary.title().replace("_", "")


def prepopulate_seednode_version_date(notaries):
    resp = {}
    for i in range(24):
        if i < 10: i = f"0{i}"
        resp.update({f"{i}": {}})

    for notary in notaries:
        for i in resp.keys():
            resp[i].update({
                notary: {
                    "versions": [],
                    "score": -1
                }
            })
    return resp


def prepopulate_seednode_version_month(notaries):
    resp = {}
    for i in range(31):
        if i + 1 < 10:
            x = f"0{i + 1}"
        else:
            x = str(i + 1)
        resp.update({x: {}})

    for notary in notaries:
        for i in resp.keys():
            resp[i].update({
                notary: {
                    "versions": [],
                    "score": 0
                }
            })
    return resp


def floor_to_utc_day(ts):
    return math.floor(int(ts) / (SINCE_INTERVALS['day'])) * (SINCE_INTERVALS['day'])


def date_hour(timestamp):
    if timestamp > time.time() * 10: timestamp /= 1000
    date, hour = dt.fromtimestamp(timestamp, tz=tz.utc).strftime("%x %H").split(" ")
    return f"{date} {hour}:00"


def get_notary_list(season):
    return SEASONS_INFO[season]["notaries"]


def get_sidebar_links(season):
    region_notaries = get_regions_info(season)
    coins_dict = get_dpow_server_coins_dict(season)
    coins_dict["Main"] += ["KMD", "LTC"]
    coins_dict["Main"].sort()
    sidebar_links = {
        "server": os.getenv("SERVER"),
        "coins_menu": coins_dict,
        "notaries_menu": region_notaries,
    }
    return sidebar_links


def get_base_context(request):
    print("getting context")
    season = get_page_season(request)
    server = get_or_none(request, "server")
    epoch = get_or_none(request, "epoch")
    coin = get_or_none(request, "coin")
    notary = get_or_none(request, "notary")
    context = {
        "season": season,
        "server": server,
        "epoch": epoch,
        "coin": coin,
        "notary": notary,
        "season_clean": season.replace("_"," "),
        "explorers": get_explorers(), 
        "coin_icons": get_coin_icons(),
        "dpow_coins": get_dpow_server_coins_list(season),
        "notary_icons": get_notary_icons(season),
        "notaries": get_notary_list(season),
        "scheme_host": get_current_host(request),
        "sidebar_links": get_sidebar_links(season),
        "nav_data": NAV_DATA,
        "eco_data_link": get_eco_data_link()
    }
    print("got context")
    return context


def get_coin_icons(season=None):
    url = f"{THIS_SERVER}/api/info/coin_icons"
    icons = requests.get(url).json()
    return icons["results"]


def get_notary_icons(season=None):
    if not season:
        season = SEASON
    url = f"{THIS_SERVER}/api/info/notary_icons/?season={season}"
    icons = requests.get(url).json()
    return icons["results"]


def get_explorers():
    url = f"{THIS_SERVER}/api/info/explorers"
    explorers = requests.get(url).json()
    return explorers["results"]

def apply_filters_api(request, serializer, queryset, table=None, filter_kwargs=None):
    if not filter_kwargs:
        filter_kwargs = {}

    for field in serializer.Meta.fields:
        # handle both standard 'WSGIRequest' object and DRF request object
        if hasattr(request, 'query_params'):
            val = request.query_params.get(field, None)
        else:
            val = request.GET.get(field, None)
        if val is not None:
            filter_kwargs.update({field:val}) 

    if 'from_block' in request.GET:
        filter_kwargs.update({'block_height__gte':request.GET['from_block']}) 

    if 'to_block' in request.GET:
        filter_kwargs.update({'block_height__lte':request.GET['to_block']})  

    if 'from_timestamp' in request.GET:
        filter_kwargs.update({'block_time__gte':request.GET['from_timestamp']}) 

    if 'to_timestamp' in request.GET:
        filter_kwargs.update({'block_time__lte':request.GET['to_timestamp']})

    if table in ['mined_count_daily']:

        if 'from_date' in request.GET:
            filter_kwargs.update({'mined_date__gte':request.GET['from_date']})  

        if 'to_date' in request.GET:
            filter_kwargs.update({'mined_date__lte':request.GET['to_date']})   

    if table in ['daily_notarised_coin', 'daily_notarised_count']:

        if 'from_date' in request.GET:
            filter_kwargs.update({'notarised_date__gte':request.GET['from_date']}) 

        if 'to_date' in request.GET:
            filter_kwargs.update({'notarised_date__lte':request.GET['to_date']})  

    if len(filter_kwargs) > 0:
        queryset = queryset.filter(**filter_kwargs)
    return queryset


def get_current_host(request):
    scheme = request.is_secure() and "https" or "http"
    if THIS_SERVER.find("stats.kmd.io") > -1:
        return f'https://{request.get_host()}/'
    else:
        return f'{scheme}://{request.get_host()}/'


def get_dexstats_explorers():
    explorers = requests.get(f"{THIS_SERVER}/api/info/explorers/").json()["results"]
    dexplorers = {}
    for coin in explorers:
        for item in explorers[coin]:
            if item.find("dexstats") > -1:
                dexplorers.update({coin:item})
    return dexplorers


def get_season(time_stamp=None):
    if not time_stamp:
        time_stamp = int(time.time())
    for season in SEASONS_INFO:
        if season.find("Testnet") == -1:
            if season in SEASONS_INFO:
                if POSTSEASON:
                    if 'post_season_end_time' in SEASONS_INFO[season]:
                        end_time = SEASONS_INFO[season]['post_season_end_time']
                    else:
                        end_time = SEASONS_INFO[season]['end_time']
                else:
                    end_time = SEASONS_INFO[season]['end_time']
                if time_stamp >= SEASONS_INFO[season]['start_time'] and time_stamp <= end_time:
                    return season
            else:
                logger.warning(f"[get_season] unrecognised season (not in SEASONS_INFO): {season}")
        else:
            logger.warning(f"[get_season] ignoring season: {season}")
    return "Unofficial"


def add_dict_nest(old_dict, new_key):
    for key in old_dict:
        old_dict[key].update({new_key:{}})
    return old_dict


def add_numeric_dict_nest(old_dict, new_key):
    for key in old_dict:
        old_dict[key].update({new_key:0})
    return old_dict


def add_string_dict_nest(old_dict, new_key):
    for key in old_dict:
        old_dict[key].update({new_key:""})
    return old_dict


def create_dict(key_list):
    new_dict = {}
    for key in key_list:
        new_dict.update({key:{}})
    return new_dict


# takes a row from queryset values, and returns a dict using a defined row value as top level key
def items_row_to_dict(items_row, top_key):
    key_list = list(items_row.keys())
    nested_json = {}
    nested_json.update({items_row[top_key]:{}})
    for key in key_list:
        if key != top_key:
            nested_json[items_row[top_key]].update({key:items_row[key]})
    return nested_json


def get_regions_info(season):
    return SEASONS_INFO[season]["regions"]


def get_page_season(request):
    if "season" in request.GET:
        if request.GET["season"] in SEASONS_INFO:
            return request.GET["season"]
    return SEASON


def day_hr_min_sec(seconds, granularity=2):
    result = []
    for name, count in INTERVALS:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])


def sort_dict(item: dict):
    return {k: sort_dict(v) if isinstance(v, dict) else v for k, v in sorted(item.items())}
    

def get_eco_data_link():
    if len(ECO_DATA) == 0:
        return ""
    item = random.choice(ECO_DATA)
    ad = random.choice(item['ads'])
    while ad['frequency'] == "never": 
        item = random.choice(ECO_DATA)
        ad = random.choice(item['ads'])
    link = ad['data']['string1']+" <a href="+ad['data']['link']+"> " \
          +ad['data']['anchorText']+"</a> "+ad['data']['string2']
    return link


def get_dpow_server_coins_dict(season=None):
    if not season:
        season = SEASON
    url = f"{THIS_SERVER}/api/info/dpow_server_coins"
    dpow_main_coins = requests.get(f"{url}/?season={season}&server=Main")
    dpow_3p_coins = requests.get(f"{url}/?season={season}&server=Third_Party")
    coins_dict = {
        "Main": dpow_main_coins.json()['results'],
        "Third_Party": dpow_3p_coins.json()['results']
    }
    
    return coins_dict

def get_dpow_server_coins_list(season=None):
    if not season:
        season = SEASON
    url = f"{THIS_SERVER}/api/info/dpow_server_coins"
    dpow_main_coins = requests.get(f"{url}/?season={season}&server=Main")
    dpow_3p_coins = requests.get(f"{url}/?season={season}&server=Third_Party")
    coins_list = dpow_main_coins.json()['results'] + dpow_3p_coins.json()['results']
    
    return coins_list


def get_coin_server(season, coin):
    if coin in ["KMD", "BTC", "LTC"]:
        return coin
    coins_dict = get_dpow_server_coins_dict(season)
    for server in coins_dict:
        if coin in coins_dict[server]:
            return server
    return "Unofficial"


def get_mainnet_coins(coins_dict):
    if "Main" in coins_dict:
        return coins_dict["Main"]
    return []


def get_third_party_coins(coins_dict):
    if "Third_Party" in coins_dict:
        return coins_dict["Third_Party"]
    return []


def get_notary_region(notary):
    return notary.split("_")[-1]


def get_time_since(timestamp):
    if timestamp == 0:
        return -1, "Never"
    now = int(time.time())
    sec_since = now - int(timestamp)
    dms_since = day_hr_min_sec(sec_since)
    return sec_since, dms_since


def region_sort(notary_list):
    new_list = []
    for region in ['AR','EU','NA','SH','DEV']:
        for notary in notary_list:
            if notary.endswith(region):
                new_list.append(notary)
    return new_list


def prepare_regional_graph_data(graph_data):
    bg_color = []
    border_color = []
    chartdata = []
    chartLabel = ""

    labels = list(graph_data.keys())
    labels.sort()
    labels = region_sort(labels)

    for label in labels:
        if label.endswith("_AR"):
            bg_color.append(COLORS["AR_REGION"])
        elif label.endswith("_EU"):
            bg_color.append(COLORS["EU_REGION"])
        elif label.endswith("_NA"):
            bg_color.append(COLORS["NA_REGION"])
        elif label.endswith("_SH"):
            bg_color.append(COLORS["SH_REGION"])
        else:
            bg_color.append(COLORS["DEV_REGION"])
        border_color.append(COLORS["BLACK"])

    chartdata = []
    for label in labels:
        chartdata.append(graph_data[label])
    
    data = { 
        "labels": labels, 
        "chartLabel": chartLabel, 
        "chartdata": chartdata, 
        "bg_color": bg_color, 
        "border_color": border_color, 
    } 
    return data


def prepare_coins_graph_data(graph_data, coins_dict):
    bg_color = []
    border_color = []
    chartdata = []
    chartLabel = ""

    labels = list(graph_data.keys())
    labels.sort()
        
    if not season:
        season = SEASON
    main_coins = get_mainnet_coins(coins_dict)
    third_coins = get_third_party_coins(coins_dict)

    for label in labels:
        if label in third_coins:
            bg_color.append(COLORS["THIRD_PARTY_COLOR"])
        elif label in main_coins:
            bg_color.append(COLORS["MAIN_COLOR"])
        else:
            bg_color.append(COLORS["OTHER_COIN_COLOR"])
        border_color.append(COLORS["BLACK"])

    chartdata = []
    for label in labels:
        chartdata.append(graph_data[label])
    
    data = { 
        "labels": labels, 
        "chartLabel": chartLabel, 
        "chartdata": chartdata, 
        "bg_color": bg_color, 
        "border_color": border_color, 
    } 
    return data


def is_hex(str_):
    hex_digits = set(string.hexdigits)
    return all(i in hex_digits for i in str_)


def safe_div(x,y):
    if y==0: return 0
    return float(x/y)


# DEPRECATE
def get_low_nn_balances():
    url = "http://138.201.207.24/nn_balances_report"
    r = requests.get(url)
    return r.json()


def get_notary_funding():
    url = "http://138.201.207.24/nn_funding"
    r = requests.get(url)
    return r.json()


def get_bot_balance_deltas():
    url = "http://138.201.207.24/nn_balances_deltas"
    r = requests.get(url)
    return r.json()