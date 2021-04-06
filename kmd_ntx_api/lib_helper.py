#!/usr/bin/env python3
import time
import json
import random
import logging
import requests
import binascii
from .lib_const import *
from .lib_stats import *

logger = logging.getLogger("mylogger")

def get_season(time_stamp=None):
    if not time_stamp:
        time_stamp = int(time.time())
    for season in SEASONS_INFO:
        if season.find("Testnet") == -1:
            if POSTSEASON:
                if 'post_season_end_time' in SEASONS_INFO[season]:
                    end_time = SEASONS_INFO[season]['post_season_end_time']
                else:
                    end_time = SEASONS_INFO[season]['end_time']
            else:
                end_time = SEASONS_INFO[season]['end_time']
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
            "name":"Asia and Russia",
            "nodes":[]
            },
        'EU':{ 
            "name":"Europe",
            "nodes":[]
            },
        'NA':{ 
            "name":"North America",
            "nodes":[]
            },
        'SH':{ 
            "name":"Southern Hemisphere",
            "nodes":[]
            },
        'DEV':{ 
            "name":"Developers",
            "nodes":[]
            }
    }
    for notary in notary_list:
        try:
            region = notary.split('_')[-1]
            regions_info[region]['nodes'].append(notary)
        except:
            pass

    return regions_info

def day_hr_min_sec(seconds, granularity=2):
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

def get_eco_data_link():
    item = random.choice(ECO_DATA)
    ad = random.choice(item['ads'])
    while ad['frequency'] == "never":
        item = random.choice(ECO_DATA)
        ad = random.choice(item['ads'])
    link = ad['data']['string1']+" <a href="+ad['data']['link']+"> " \
          +ad['data']['anchorText']+"</a> "+ad['data']['string2']
    return link

def get_mainnet_chains(coins_dict):
    if "Main" in coins_dict:
        return coins_dict["Main"]
    return []

def get_third_party_chains(coins_dict):
    if "Third_Party" in coins_dict:
        return coins_dict["Third_Party"]
    return []


def paginate_wrap(resp, url, field, prev_value, next_value):
    api_resp = {
        "count":len(resp),
        "next":url+"?"+field+"="+next_value,
        "previous":url+"?"+field+"="+prev_value,
        "results":[resp]
    }
    return api_resp

def wrap_api(resp, filters=None):
    api_resp = {
        "count":len(resp),
        "results":[resp]
    }
    if filters:
        api_resp.update({"filters":filters})
    return api_resp

def get_notary_region(notary):
    return notary.split("_")[-1]

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
            bg_color.append(LT_GREEN)
        elif label.endswith("_NA"):
            bg_color.append(LT_PURPLE)
        elif label.endswith("_SH"):
            bg_color.append(LT_BLUE)
        else:
            bg_color.append(LT_ORANGE)
        border_color.append(BLACK)

    chartdata = []
    for label in labels:
        chartdata.append(graph_data[label])
    
    data = { 
        "labels":labels, 
        "chartLabel":chartLabel, 
        "chartdata":chartdata, 
        "bg_color":bg_color, 
        "border_color":border_color, 
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
        season = "Season_4"
    main_chains = get_mainnet_chains(coins_dict)
    third_chains = get_third_party_chains(coins_dict)

    for label in labels:
        if label in third_chains:
            bg_color.append(LT_PURPLE)
        elif label in main_chains:
            bg_color.append(LT_GREEN)
        else:
            bg_color.append(LT_ORANGE)
        border_color.append(BLACK)

    chartdata = []
    for label in labels:
        chartdata.append(graph_data[label])
    
    data = { 
        "labels":labels, 
        "chartLabel":chartLabel, 
        "chartdata":chartdata, 
        "bg_color":bg_color, 
        "border_color":border_color, 
    } 
    return data

# OP_RETURN functions

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])
    
def get_ticker(x):
    chain = ''
    while len(chain) < 1:
        for i in range(len(x)):
            if chr(x[i]).encode() == b'\x00':
                j = i+1
                while j < len(x)-1:
                    chain += chr(x[j])
                    j += 1
                    if chr(x[j]).encode() == b'\x00':
                        break
                break
    if chr(x[-4])+chr(x[-3])+chr(x[-2]) == "KMD":
        chain = "KMD"
    return chain


def decode_opret(op_return, coins_list):  
    ac_ntx_blockhash = lil_endian(op_return[:64])

    try:
        ac_ntx_height = int(lil_endian(op_return[64:72]),16) 

    except Exception as e:
        err = {"error":f"{op_return} is invalid and can not be decoded. {e}"}
        logger.error(err)
        return err

    x = binascii.unhexlify(op_return[70:])
    chain = get_ticker(x)

    for x in coins_list:
        if len(x) > 2 and x not in EXCLUDE_DECODE_OPRET_COINS:
            if chain.endswith(x):
                chain = x

    if chain == "KMD":
        btc_txid = lil_endian(op_return[72:136])
        
    elif chain not in noMoM:
        # not sure about this bit, need another source to validate the data
        try:
            start = 72+len(chain)*2+4
            end = 72+len(chain)*2+4+64
            MoM_hash = lil_endian(op_return[start:end])
            MoM_depth = int(lil_endian(op_return[end:]),16)
        except Exception as e:
            logger.error(f"Error in decode_opret [{op_return}] {e}")
    resp = { "chain":chain, "notarised_block":ac_ntx_height, "notarised_blockhash":ac_ntx_blockhash }
    logger.info(f"decode_opret: {resp}")
    return resp

