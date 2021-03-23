#!/usr/bin/env python3
import logging
import binascii
from .models import *
from .lib_const import *

logger = logging.getLogger("mylogger")

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])
    
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

def get_season(time_stamp):
    for season in seasons_info:
        if time_stamp >= seasons_info[season]['start_time'] and time_stamp <= seasons_info[season]['end_time']:
            return season
    return "season_undefined"
    
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
def get_ticker(scriptPubKeyBinary):
    chain = ''
    while len(chain) < 1:
        for i in range(len(scriptPubKeyBinary)):
            if chr(scriptPubKeyBinary[i]).encode() == b'\x00':
                j = i+1
                while j < len(scriptPubKeyBinary)-1:
                    chain += chr(scriptPubKeyBinary[j])
                    j += 1
                    if chr(scriptPubKeyBinary[j]).encode() == b'\x00':
                        break
                break
    if chr(scriptPubKeyBinary[-4])+chr(scriptPubKeyBinary[-3])+chr(scriptPubKeyBinary[-2]) =="KMD":
        chain = "KMD"
    return chain


def decode_opret(scriptPubKey_asm):   
    ac_ntx_blockhash = lil_endian(scriptPubKey_asm[:64])
    try:
        ac_ntx_height = int(lil_endian(scriptPubKey_asm[64:72]),16) 
    except:
        return {"error":scriptPubKey_asm+ " is invalid and can not be decoded."}
    scriptPubKeyBinary = binascii.unhexlify(scriptPubKey_asm[70:])
    chain = get_ticker(scriptPubKeyBinary)
    if chain.endswith("KMD"):
        chain = "KMD"
    if chain == "KMD":
        btc_txid = lil_endian(scriptPubKey_asm[72:136])
    elif chain not in noMoM:
        # not sure about this bit, need another source to validate the data
        try:
            start = 72+len(chain)*2+4
            end = 72+len(chain)*2+4+64
            MoM_hash = lil_endian(scriptPubKey_asm[start:end])
            MoM_depth = int(lil_endian(scriptPubKey_asm[end:]),16)
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
            bg_color.append('#b541ea')
        elif label in main_chains:
            bg_color.append('#2fea8b')
        else:
            bg_color.append('#f7931a')
        border_color.append('#000')

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
            bg_color.append('#DC0333')
        elif label.endswith("_EU"):
            bg_color.append('#2FEA8B')
        elif label.endswith("_NA"):
            bg_color.append('#B541EA')
        elif label.endswith("_SH"):
            bg_color.append('#00E2FF')
        else:
            bg_color.append('#F7931A')
        border_color.append('#000')

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