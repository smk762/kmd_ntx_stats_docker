#!/usr/bin/env python3
from lib_const import *
from lib_urls import *
from lib_api import *
from decorators import *


def safe_div(x,y):
    if y==0: return 0
    return float(x/y)


def get_pubkeys(season, server):
    if season in NOTARY_PUBKEYS:
        if server == 'Main':
            return NOTARY_PUBKEYS[season]

        elif server == 'Third_Party':
            if f"{season}_Third_Party" in NOTARY_PUBKEYS:
                return NOTARY_PUBKEYS[f"{season}_Third_Party"]
    return []


def get_address_from_notary(season, notary, chain):
    return NOTARY_ADDRESSES_DICT[season][notary][chain]


def has_season_started(season):
    now = time.time()
    if season in SEASONS_INFO:
        if SEASONS_INFO[season]["start_time"] < now:
            return True
    return False


def get_season_notaries(season):
    if season in NOTARY_PUBKEYS:
        notaries = list(NOTARY_PUBKEYS[season].keys())
        notaries.sort()
        return notaries
    return []


def get_dpow_coin_src(src):
    try:
        return src.split("(")[1].replace(")","")
    except:
        return src


def get_dpow_coin_server(server):
    if server.lower() == "dpow-3p":
        return "Third_Party"
    elif server.lower() == "dpow-mainnet":
        return "Main"


def get_assetchain_launch_params(item):
    params = "~/komodo/src/komodod"
    for k, v in item.items():
        if k == 'addnode':
            for ip in v:
                params += " -"+k+"="+ip
        else:
            params += " -"+k+"="+str(v)
    return params


def get_assetchain_conf_path(ac_name):
    return f"~/.komodo/{ac_name}/{ac_name}.conf"


def get_assetchain_cli(ac_name):
    return f"~/komodo/src/komodo-cli -ac_name={ac_name}"


def pre_populate_coins_data(coins_data, coin):
    if coin not in coins_data:
        coins_data.update({coin: {}})
    if "coins_info" not in coins_data[coin]:
        coins_data[coin].update({"coins_info": {}})
    if "dpow" not in coins_data[coin]:
        coins_data[coin].update({"dpow": {}})
    if "dpow_tenure" not in coins_data[coin]:
        coins_data[coin].update({"dpow_tenure": {}})
    if "dpow_active" not in coins_data[coin]:
        coins_data[coin].update({"dpow_active": 0})
    if "electrums" not in coins_data[coin]:
        coins_data[coin].update({"electrums": []})
    if "electrums_ssl" not in coins_data[coin]:
        coins_data[coin].update({"electrums_ssl": []})
    if "explorers" not in coins_data[coin]:
        coins_data[coin].update({"explorers": []})
    if "mm2_compatible" not in coins_data[coin]:
        coins_data[coin].update({"mm2_compatible": 0})
    return coins_data


def get_coins_repo_electrums(coins_data, coin):
    try:
        electrums_base_url = get_coins_repo_electrums_url()
        if coin == "COQUICASH":
            r = requests.get(f"{electrums_base_url}/COQUI")
        elif coin == "WLC21":
            r = requests.get(f"{electrums_base_url}/electrums/WLC")
        elif coin == "PIRATE":
            r = requests.get(f"{electrums_base_url}/electrums/ARRR")
        elif coin == "TOKEL":
            r = requests.get(f"{electrums_base_url}/electrums/TKL")
        else:
            r = requests.get(f"{electrums_base_url}/"+coin)
        
        for electrum in r.json():
            if "protocol" in electrum:
                if electrum['protocol'] == "SSL":
                    coins_data[coin]['electrums_ssl'].append(electrum['url'])
                else:
                    coins_data[coin]['electrums'].append(electrum['url'])
            else:
                coins_data[coin]['electrums'].append(electrum['url'])

    except Exception as e:
        if r.text != "404: Not Found":
            logger.error(f"Exception in [parse_electrum_explorer]: {e} {r.text}")
                
    return coins_data


def get_coins_repo_explorers(coins_data, coin):
    try:
        explorers_base_url = get_coins_repo_explorers_url()
        if coin == "COQUICASH":
            r = requests.get(f"{explorers_base_url}/COQUI")
        elif coin == "WLC21":
            r = requests.get(f"{explorers_base_url}/WLC")
        elif coin == "TOKEL":
            r = requests.get(f"{explorers_base_url}/TKL")
        else:
            r = requests.get(f"{explorers_base_url}/"+coin)

        for explorer in r.json():
            coins_data[coin]['explorers'].append(explorer.replace("/tx/", "/").replace("/tx.dws?", "/"))

    except Exception as e:
        if r.text != "404: Not Found":
            logger.error(f"Exception in [parse_electrum_explorer]: {e} {r.text}")
                
    return coins_data


def get_coins_repo_icons(coins_data, coin):
    try:
        icons_base_url = get_coins_repo_icons_url()
        if coin == "COQUICASH":
            url = f"{icons_base_url}/coqui.png"
            r = requests.get(url)
        elif coin == "GLEEC-OLD":
            url = f"{icons_base_url}/gleec.png"
            r = requests.get(url)
        elif coin == "TOKEL":
            url = f"{icons_base_url}/tkl.png"
            r = requests.get(url)
        elif coin == "PIRATE":
            url = f"{icons_base_url}/arrr.png"
            r = requests.get(url)
        elif coin == "WLC21":
            url = f"{icons_base_url}/wlc.png"
            r = requests.get(url)
        else:
            url = f"{icons_base_url}/{coin.lower()}.png"
            r = requests.get(url)

        if r.text != "404: Not Found":
            coins_data[coin]["coins_info"].update({"icon":url})

    except Exception as e:
        if r.text != "404: Not Found":
            logger.error(f"Exception in [parse_electrum_explorer]: {e} {r.text}")
                
    return coins_data


def is_notary_ltc_address(addr):
    if addr in ALL_SEASON_NOTARY_LTC_ADDRESSES:
        return True
    return False
    

def get_local_addresses(local_info):
    local_addresses = []
    for item in local_info:
        if item["input_index"] != -1:
            local_addresses.append(item["address"])
    return local_addresses


def get_notary_address_lists(vin):
    notary_list = []
    address_list = []
    for item in vin:
        if "address" in item:
            address_list.append(item['address'])
            if item['address'] in KNOWN_ADDRESSES:
                notary = KNOWN_ADDRESSES[item['address']]
                notary_list.append(notary)
            else:
                notary_list.append(item['address'])
    notary_list.sort()
    return notary_list, address_list


def decode_opret_coin(chain):
    """Gets rid of extra data by matching to known coins"""
    # TODO: This could potentially misidentify - be vigilant.
    for x in KNOWN_COINS:
        if len(x) > 2 and x not in EXCLUDE_DECODE_OPRET_COINS:
            if chain.endswith(x):
                chain = x

    # some decodes have a null char error, this gets rid of that so populate script doesnt error out 
    if chain.find('\x00') != -1:
        chain = chain.replace('\x00','')

    return chain




def get_default_season_ntx_dict():
    return {
        "season_ntx_count":0,
        "season_ntx_score":0,
        "chains":{},
        "servers":{},
        "notaries":{}
    }


def get_default_season_ntx_chains_dict(chain):
    return {
        chain: {
            "chain_ntx_count":0,
            "chain_ntx_score":0,
            "chain_ntx_count_pct":0,
            "chain_ntx_score_pct":0,
            "epochs":{}
        }
    }


def get_default_season_ntx_server_dict(server):
    return {
        server: {
            "server_ntx_count":0,
            "server_ntx_score":0,
            "server_ntx_count_pct":0,
            "server_ntx_score_pct":0,
            "epochs":{}
        }
    }


def get_default_season_ntx_notaries_dict(notary):
    return {
        notary: {
            "notary_ntx_count":0,
            "notary_ntx_score":0,
            "notary_ntx_count_pct":0,
            "notary_ntx_score_pct":0,
            "servers":{},
            "chains":{}
        }
    }


def get_default_season_ntx_notary_servers_dict(server):
    return {
        server: {
            "notary_server_ntx_count":0,
            "notary_server_ntx_score":0,
            "notary_server_ntx_count_pct":0,
            "notary_server_ntx_score_pct":0,
            "epochs":{}
        }
    }


def get_default_season_ntx_notary_server_epochs_dict(epoch):
    return {
        epoch: {
            "score_per_ntx":0,
            "notary_server_epoch_ntx_count":0,
            "notary_server_epoch_ntx_score":0,
            "notary_server_epoch_ntx_count_pct":0,
            "notary_server_epoch_ntx_score_pct":0,
            "chains":{}
        }
    }


def get_default_season_ntx_notary_server_epoch_chains_dict(chain):
    return {
        chain: {
            "notary_server_epoch_chain_ntx_count":0,
            "notary_server_epoch_chain_ntx_score":0,
            "notary_server_epoch_chain_ntx_count_pct":0,
            "notary_server_epoch_chain_ntx_score_pct":0
        }
    }


def get_default_season_ntx_server_epochs_dict(epoch):
    return {
        epoch: {
            "score_per_ntx":0,
            "epoch_ntx_count":0,
            "epoch_ntx_score":0,
            "epoch_ntx_count_pct":0,
            "epoch_ntx_score_pct":0,
            "chains":{}
        }
    }


def get_default_season_ntx_server_epoch_chains_dict(chain):
    return {
        chain: {
            "score_per_ntx":0,
            "epoch_chain_ntx_count":0,
            "epoch_chain_ntx_score":0,
            "epoch_chain_ntx_count_pct":0,
            "epoch_chain_ntx_score_pct":0
        }
    }


def get_default_season_ntx_chain_epochs_dict(epoch):
    return {
        epoch: {
            "score_per_ntx":0,
            "chain_epoch_ntx_count":0,
            "chain_epoch_ntx_score":0,
            "chain_epoch_ntx_count_pct":0,
            "chain_epoch_ntx_score_pct":0
        }
    }


def get_default_season_ntx_notary_chains_dict(chain):
    return {
        chain: {
            "notary_chain_ntx_count":0,
            "notary_chain_ntx_score":0,
            "notary_chain_ntx_count_pct":0,
            "notary_chain_ntx_score_pct":0
        }
    }


def is_postseason(timestamp=None):
    if not timestamp:
        timestamp = int(time.time())
    for season in SEASONS_INFO:
        if "post_season_end_time" in SEASONS_INFO[season]:
            if timestamp >= SEASONS_INFO[season]["post_season_end_time"]:
                if timestamp <= SEASONS_INFO[season]["end_time"]:
                    return True
    return False