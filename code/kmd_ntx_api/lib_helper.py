#!/usr/bin/env python3
import time
import json
import math
import random
import logging
import requests
from .lib_const import *
import string
import itertools
from datetime import datetime, timezone


logger = logging.getLogger("mylogger")


def get_active_mm2_versions(ts):
    data = requests.get(VERSION_TIMESPANS_URL).json()
    active_versions = []
    for version in data:
        if int(ts) > data[version]["start"] and int(ts) < data[version]["end"]:
            active_versions.append(version)
    return active_versions


def is_mm2_version_valid(version, timestamp):
    active_versions = get_active_mm2_versions(timestamp)
    if version in active_versions:
        return True
    return False


def floor_to_utc_day(ts):
    return math.floor(ts/(24*60*60))*(24*60*60)

def date_hour(timestamp):
    date, hour = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%x %H").split(" ")
    return f"{date} {hour}:00"

def get_notary_list(season):
    return requests.get(f"{THIS_SERVER}/api/info/notary_nodes/?season={season}").json()["results"]

def get_sidebar_links(season):
    notary_list = get_notary_list(season)
    region_notaries = get_regions_info(notary_list)
    coins_dict = get_dpow_server_coins_dict(season)
    coins_dict["Main"] += ["KMD", "LTC"]
    coins_dict["Main"].sort()
    sidebar_links = {
        "server": os.getenv("SERVER"),
        "chains_menu": coins_dict,
        "notaries_menu": region_notaries,
    }
    return sidebar_links

def get_context(request):
    mm2_coins = list(get_dexstats_explorers().keys())
    season = get_page_season(request)
    scheme_host = get_current_host(request)
    return {
        "season":season,
        "scheme_host": scheme_host,
        "mm2_coins":mm2_coins,
        "eco_data_link":get_eco_data_link()
    }

def get_base_context(request):
    season = get_page_season(request)
    scheme_host = get_current_host(request)
    context = {
        "season":season,
        "scheme_host": scheme_host,
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link()
    }


def get_or_none(request, key):
    return request.GET[key] if key in request.GET else None
    

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

    if table in ['daily_notarised_chain', 'daily_notarised_count']:

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


def get_regions_info(notary_list):
    notary_list.sort()
    regions_info = {
        'AR':{ 
            "name": "Asia and Russia",
            "nodes": []
            },
        'EU':{ 
            "name": "Europe",
            "nodes": []
            },
        'NA':{ 
            "name": "North America",
            "nodes": []
            },
        'SH':{ 
            "name": "Southern Hemisphere",
            "nodes": []
            },
        'DEV':{ 
            "name": "Developers",
            "nodes": []
            }
    }
    for notary in notary_list:
        try:
            region = notary.split('_')[-1]
            regions_info[region]['nodes'].append(notary)
        except:
            pass

    return regions_info

def get_mm2_coins():
    r = requests.get(f"{THIS_SERVER}/api/info/coins/?mm2_compatible=1")
    coins = list(r.json()["results"].keys())
    coins.sort()
    return coins

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
    dpow_main_chains = requests.get(f"{url}/?season={season}&server=Main").json()['results']
    dpow_3p_chains = requests.get(f"{url}/?season={season}&server=Third_Party").json()['results']

    chains_dict = {
        "Main": dpow_main_chains,
        "Third_Party": dpow_3p_chains
    }
    
    return chains_dict

def get_chain_server(chain, season):
    if chain in ["KMD", "BTC", "LTC"]:
        return chain
    coins_dict = get_dpow_server_coins_dict(season)
    for server in coins_dict:
        if chain in coins_dict[server]:
            return server
    return "Unofficial"


def get_mainnet_chains(coins_dict):
    if "Main" in coins_dict:
        return coins_dict["Main"]
    return []


def get_third_party_chains(coins_dict):
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
            bg_color.append(RED)
        elif label.endswith("_EU"):
            bg_color.append(MAIN_COLOR)
        elif label.endswith("_NA"):
            bg_color.append(THIRD_PARTY_COLOR)
        elif label.endswith("_SH"):
            bg_color.append(LT_BLUE)
        else:
            bg_color.append(OTHER_COIN_COLOR)
        border_color.append(BLACK)

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
    main_chains = get_mainnet_chains(coins_dict)
    third_chains = get_third_party_chains(coins_dict)

    for label in labels:
        if label in third_chains:
            bg_color.append(THIRD_PARTY_COLOR)
        elif label in main_chains:
            bg_color.append(MAIN_COLOR)
        else:
            bg_color.append(OTHER_COIN_COLOR)
        border_color.append(BLACK)

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

def is_hex(s):
    hex_digits = set(string.hexdigits)
    return all(c in hex_digits for c in s)

def safe_div(x,y):
    if y==0: return 0
    return float(x/y)