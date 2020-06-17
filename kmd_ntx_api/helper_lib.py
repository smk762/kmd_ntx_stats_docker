#!/usr/bin/env python3
import logging
import binascii
from .models import *
logger = logging.getLogger("mylogger")

noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'AYA']

 # Need to confirm and fill this in correctly later...
seasons_info = {
    "Season_1": {
            "start_block":1,
            "end_block":1,
            "start_time":1,
            "end_time":1530921600,
            "notaries":[]
        },
    "Season_2": {
            "start_block":1,
            "end_block":1,
            "start_time":1530921600,
            "end_time":1563148799,
            "notaries":[]
        },
    "Season_3": {
            "start_block":1444000,
            "end_block":1921999,
            "start_time":1563148800,
            "end_time":1592146799,
            "notaries":[]
        },
    "Season_4": {
            "start_block":1922000,
            "end_block":2444000,
            "start_time":1592146800,
            "end_time":1751328000,
            "notaries":[]
        }
}

def get_season(time_stamp):
    for season in seasons_info:
        if time_stamp >= seasons_info[season]['start_time'] and time_stamp <= seasons_info[season]['end_time']:
            return season
    return "season_undefined"
    
# convert timestamp to human time 
intervals = (
    ('wks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hrs', 3600),    # 60 * 60
    ('mins', 60),
    ('sec', 1),
    )

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

def region_sort(notary_list):
    new_list = []
    for region in ['AR','EU','NA','SH','DEV']:
        for notary in notary_list:
            if notary.endswith(region):
                new_list.append(notary)
    return new_list

# takes a row from queryset values, and returns a dict using a defined row value as top level key
def items_row_to_dict(items_row, top_key):
    key_list = list(items_row.keys())
    nested_json = {}
    nested_json.update({items_row[top_key]:{}})
    for key in key_list:
        if key != top_key:
            nested_json[items_row[top_key]].update({key:items_row[key]})
    return nested_json

# convert timestamp to human time 
intervals = (
    ('wks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hrs', 3600),    # 60 * 60
    ('mins', 60),
    ('sec', 1),
    )

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


def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

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
    return main_chains

def get_third_party_chains(coins_data):
    third_chains = []
    for item in coins_data:
        if item['dpow']['server'].lower() == "dpow-3p":
            third_chains.append(item['chain'])
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
    '''
    print(len(third_party))
    print(third_party)
    print(len(main_chains))
    print(main_chains)
    '''
    print('main_ntx')
    print(main_ntx)
    print('third_party_ntx')
    print(third_party_ntx)
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