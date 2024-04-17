import os
import math
import time
import string
import random
import requests
import datetime
from calendar import monthrange
from datetime import datetime as dt
from django.http import JsonResponse
from kmd_ntx_api.notary_seasons import get_seasons_info, get_season
from kmd_ntx_api.cache_data import ecosystem_links_cache
from kmd_ntx_api.logger import logger



##################

def get_nn_region_split(notary):
    x = notary.split("_")
    region = x[-1]
    nn = notary.replace(f"_{region}", "")
    return nn, region

def get_random_notary(notary_list):
    if notary_list:
        return random.choice(notary_list)
    return None

# TODO: reduce calls missing `seasons_info` param
def get_notary_list(season, seasons_info=None):
    logger.calc("get_notary_list")
    if seasons_info is None:
        seasons_info = get_seasons_info()
    if season not in seasons_info:
        return []
    return seasons_info[season]["notaries"]




def get_notary_region(notary):
    return notary.split("_")[-1]


def pad_dec_to_hex(num):
    hex_val = hex(num)[2:]
    if len(hex_val) % 2 != 0:
        hex_val = f"0{hex_val}"
    return hex_val.upper()


def get_mainnet_coins(dpow_coins_dict):
    if "Main" in dpow_coins_dict:
        return dpow_coins_dict["Main"]
    return []


def get_regions_info(season):
    logger.calc("get_regions_info")
    seasons_info = get_seasons_info()
    if season in seasons_info:
        return seasons_info[season]["regions"]
    return {}


def get_page_server(request):
    if "server" in request.GET:
        if request.GET['server'] == "3P": return "Third_Party"
        if request.GET["server"].title() in ["Main", "Third_Party", "LTC", "KMD"]:
            return request.GET["server"].title()
    return None


def get_notary_clean(notary):
    if notary:
        notary_split = notary.split("_")
        notary = notary_split[0].title()
        if len(notary_split) > 1:
            notary = f"{notary} {notary_split[1]}"
    return notary


def get_eco_data_link():
    ecosystem_links = ecosystem_links_cache()
    if len(ecosystem_links) == 0:
        return ""
    item = random.choice(ecosystem_links)
    ad = random.choice(item['ads'])
    while ad['frequency'] == "never": 
        item = random.choice(ecosystem_links)
        ad = random.choice(item['ads'])
    link = ad['data']['string1']+" <a href="+ad['data']['link']+"> " \
          +ad['data']['anchorText']+"</a> "+ad['data']['string2']
    return link

def json_resp(resp, filters=None, params=None, ignore_errors=False, raw=False):

    if raw:
        return JsonResponse(resp)

    data = {}
    if filters:
        data.update({"filters": filters})

    if params:
        data.update({"params": params})

    if has_error(resp) and not ignore_errors:
        data.update({"error": resp["error"]})

    if "filters" in resp:
        data.update({"filters": resp["filters"]})
        
    if "selected" in resp:
        data.update({"selected": resp["selected"]})

    if "required" in resp:
        data.update({"required": resp["required"]})

    if "distinct" in resp:
        data.update({"distinct": resp["distinct"]})

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


def is_hex(str_):
    hex_digits = set(string.hexdigits)
    return all(i in hex_digits for i in str_)


def safe_div(x,y):
    if y==0: return 0
    return float(x/y)


def has_error(_dict):
    if "error" in _dict:
        return True
    return False


def sort_dict(item: dict):
    return {k: sort_dict(v) if isinstance(v, dict) else v for k, v in sorted(item.items())}


def get_or_none(request, key, default=None):
    val = request.GET[key] if key in request.GET else None
    if default and not val:
        return default
    return val

def get_third_party_coins(dpow_coins_dict):
    if "Third_Party" in dpow_coins_dict:
        return dpow_coins_dict["Third_Party"]
    return []

# takes a row from queryset values, and returns a dict using a defined row value as top level key
def items_row_to_dict(items_row, top_key):
    key_list = list(items_row.keys())
    nested_json = {}
    nested_json.update({items_row[top_key]:{}})
    for key in key_list:
        if key != top_key:
            nested_json[items_row[top_key]].update({key:items_row[key]})
    return nested_json


def region_sort(notary_list):
    new_list = []
    for region in ['AR','EU','NA','SH','DEV']:
        for notary in notary_list:
            if notary.endswith(region):
                new_list.append(notary)
    return new_list


# These were in lib_helper, but are not used anywhere except in the testnet.py file.
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
        old_dict[key].update({new_key: ""})
    return old_dict


def create_dict(key_list):
    new_dict = {}
    for key in key_list:
        new_dict.update({key:{}})
    return new_dict


# Only used in seednodes.py
def date_hour(timestamp):
    if timestamp > time.time() * 10: timestamp /= 1000
    date, hour = dt.utcfromtimestamp(timestamp).strftime("%x %H").split(" ")
    return f"{date} {hour}:00"


def floor_to_utc_day(ts):
    return math.floor(int(ts) / (SINCE_INTERVALS['day'])) * (SINCE_INTERVALS['day'])


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



# Only used in graph.py
def update_unique(dict_, key, val):
    if key not in dict_:
        dict_.update({key:val})
        return True
    return False


def append_unique(list_, item):
    if item not in list_:
        list_.append(item)
        return True
    return False


# Unused functions
def qset_values_to_list(qset_vals):
    table_data = []
    for item in qset_vals:
        table_data.append([v for k, v in item.items()])
    return table_data



def keys_to_list(_dict):
    _list = list(_dict.keys())
    _list.sort()
    return _list
