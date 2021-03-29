#!/usr/bin/env python3
import time
import logging
import binascii
from .models import *
from .lib_const import *

logger = logging.getLogger("mylogger")
    
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

def get_season(time_stamp=None):
    if not time_stamp:
        time_stamp = int(time.time())
    for season in SEASONS_INFO:
        if time_stamp >= SEASONS_INFO[season]['start_time'] and time_stamp <= SEASONS_INFO[season]['end_time']:
            return season
    return "season_undefined"

def get_notary_region(notary):
    return notary.split("_")[-1]

def region_sort(notary_list):
    new_list = []
    for region in ['AR','EU','NA','SH','DEV']:
        for notary in notary_list:
            if notary.endswith(region):
                new_list.append(notary)
    return new_list

def get_region_rank(region_notarisation_scores, notary_score):
    higher_ranked_notaries = []
    for notary in region_notarisation_scores:
        score = region_notarisation_scores[notary]['score']
        if score > notary_score:
            higher_ranked_notaries.append(notary)
    rank = len(higher_ranked_notaries)+1
    if rank == 1:
        rank = str(rank)+"st"
    elif rank == 2:
        rank = str(rank)+"nd"
    elif rank == 3:
        rank = str(rank)+"rd"
    else:
        rank = str(rank)+"th"
    return rank
    
# takes a row from queryset values, and returns a dict using a defined row value as top level key
def items_row_to_dict(items_row, top_key):
    key_list = list(items_row.keys())
    nested_json = {}
    nested_json.update({items_row[top_key]:{}})
    for key in key_list:
        if key != top_key:
            nested_json[items_row[top_key]].update({key:items_row[key]})
    return nested_json

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

def decode_opret(op_return):   
    ac_ntx_blockhash = lil_endian(op_return[:64])

    try:
        ac_ntx_height = int(lil_endian(op_return[64:72]),16) 

    except:
        return {"error":f"{op_return} is invalid and can not be decoded."}

    x = binascii.unhexlify(op_return[70:])
    chain = get_ticker(x)

    if chain.endswith("PBC"):
        chain = "PCB"

    if chain.endswith("KMD"):
        chain = "KMD"

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
            logger.debug(e)
    return { "chain":chain, "notarised_block":ac_ntx_height, "notarised_blockhash":ac_ntx_blockhash }

def get_mainnet_chains(coins_data):
    main_chains = []
    for item in coins_data:
        if item['dpow']['server'].lower() == "dpow-mainnet":
            main_chains.append(item['chain'])
    main_chains.sort()
    return main_chains

def get_third_party_chains(coins_data):
    third_chains = []
    for item in coins_data:
        if item['dpow']['server'].lower() == "dpow-3p":
            third_chains.append(item['chain'])
    third_chains.sort()
    return third_chains

def get_server_chains(coins_data):
    server_chains = {
        "main":get_mainnet_chains(coins_data),
        "third_party":get_third_party_chains(coins_data)
    }
    return server_chains





# TODO: use notarised table values
def get_ntx_score(btc_ntx, main_ntx, third_party_ntx):
    coins_data = coins.objects.filter(dpow_active=1).values('chain','dpow')
    third_party = get_third_party_chains(coins_data)
    main_chains = get_mainnet_chains(coins_data)
    if 'BTC' in main_chains:
        main_chains.remove('BTC')
    if 'KMD' in main_chains:
        main_chains.remove('KMD')
    return btc_ntx*0.0325 + main_ntx*0.8698/len(main_chains) + third_party_ntx*0.0977/len(third_party)
 






def prepare_notary_balance_graph_data(chain_low_balance_notary_counts):
    bg_color = []
    border_color = []
    chartdata = []
    chartLabel = ""

    labels = list(chain_low_balance_notary_counts.keys())
    labels.sort()
        
    third_chains = []
    main_chains = []
    coins_data = coins.objects.filter(dpow_active=1).values('chain','dpow')
    for item in coins_data:
        if item['dpow']['server'] == "dPoW-mainnet":
            main_chains.append(item['chain'])
        if item['dpow']['server'] == "dPoW-3P":
            third_chains.append(item['chain'])

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
        chartdata.append(chain_low_balance_notary_counts[label])
    
    data = { 
        "labels":labels, 
        "chartLabel":chartLabel, 
        "chartdata":chartdata, 
        "bg_color":bg_color, 
        "border_color":border_color, 
    } 
    return data

def create_dict(key_list):
    new_dict = {}
    for key in key_list:
        new_dict.update({key:{}})
    return new_dict

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

def get_server_chains_at_time(season, server, timestamp):

    # Query notarised_tenure 
    # Return list of chains actively dpow'd at timestamp
    
    pass

def prepare_chain_balance_graph_data(notary_low_balance_chain_counts):
    bg_color = []
    border_color = []
    chartdata = []
    chartLabel = ""

    labels = list(notary_low_balance_chain_counts.keys())
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
        chartdata.append(notary_low_balance_chain_counts[label])
    
    data = { 
        "labels":labels, 
        "chartLabel":chartLabel, 
        "chartdata":chartdata, 
        "bg_color":bg_color, 
        "border_color":border_color, 
    } 
    return data

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