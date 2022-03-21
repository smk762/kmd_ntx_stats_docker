#!/usr/bin/env python3
from lib_const import *
from lib_electrum import *
from lib_urls import *
from lib_api import *
from lib_table_select import *
from decorators import *


def safe_div(x,y):
    if y==0: return 0
    return float(x/y)


def handle_dual_server_chains(server, chain, addr=None):
    chain = handle_translate_chains(chain)
    if chain == "GLEEC":
        if addr:
            if addr.startswith("R"):
                server = "Main"
            else:
                server = "Third_Party"
        if server == "Third_Party":
            chain = "GLEEC-OLD"

    return server, chain


def handle_translate_chains(chain):
    if chain in TRANSLATE_COINS:
        return TRANSLATE_COINS[chain]
    return chain


def get_pubkeys(season, server):
    if season in NOTARY_PUBKEYS:
        if server == 'Main':
            return NOTARY_PUBKEYS[season]

        elif server == 'Third_Party':
            if f"{season}_Third_Party" in NOTARY_PUBKEYS:
                return NOTARY_PUBKEYS[f"{season}_Third_Party"]
    return []


def get_scored(score_value):
    if score_value > 0:
        return True
    else:
        return False


def get_name_from_address(address):
    if address in KNOWN_ADDRESSES:
        return KNOWN_ADDRESSES[address]
    return address

def get_address_from_notary(season, notary, chain):
    return NOTARY_ADDRESSES_DICT[season][notary][chain]

def has_season_started(season):
    now = time.time()
    if season in SEASONS_INFO:
        if SEASONS_INFO[season]["start_time"] < now:
            return True
    return False


def get_season_from_block(block):
    if not isinstance(block, int):
        block = int(block)
    for season in SEASONS_INFO:
        if season.find("Testnet") == -1:
            start_block = SEASONS_INFO[season]['start_block']
            end_block = SEASONS_INFO[season]['end_block']
            if block >= start_block and block <= end_block:
                return season
    return None


def get_chain_epoch_at(season, server, chain, timestamp):
    if season in DPOW_EXCLUDED_CHAINS: 
        if chain not in DPOW_EXCLUDED_CHAINS[season]:
            if int(timestamp) >= SEASONS_INFO[season]["start_time"]:
                if int(timestamp) <= SEASONS_INFO[season]["end_time"]:
                    if chain in ["KMD", "BTC", "LTC"]:
                            if int(timestamp) <= SEASONS_INFO[season]["end_time"]:
                                return f"{chain}"

            epochs = get_epochs(season, server)
            for epoch in epochs:
                if chain in epoch["epoch_chains"]:
                    if int(timestamp) >= epoch["epoch_start"] and int(timestamp) <= epoch["epoch_end"]:
                        return epoch["epoch"]

    return "Unofficial"


def get_server_active_scoring_dpow_chains_at_time(season, server, timestamp):
    url = get_notarised_tenure_table_url(season, server)
    r = requests.get(url)
    tenure = r.json()["results"]
    server_active_scoring_dpow_chains = []
    count = 0
    for item in tenure:
        if timestamp >= item["official_start_block_time"]:
            if timestamp <= item["official_end_block_time"]:
                if item["chain"] not in ["BTC", "LTC", "KMD"] and item["chain"] not in DPOW_EXCLUDED_CHAINS[season]:
                    server_active_scoring_dpow_chains.append(item["chain"])

    return list(set(server_active_scoring_dpow_chains)), len(list(set(server_active_scoring_dpow_chains)))


def check_excluded_chains(season, server, chain):
    if season in DPOW_EXCLUDED_CHAINS: 
        if chain in DPOW_EXCLUDED_CHAINS[season]:
            return "Unofficial", "Unofficial"
    return season, server


def get_season(time_stamp=None):

    if not time_stamp:
        time_stamp = int(time.time())
    time_stamp = int(time_stamp)

    # detect & convert js timestamps
    if round((time_stamp/1000)/time.time()) == 1:
        time_stamp = time_stamp/1000

    for season in SEASONS_INFO:

        if season.find("Testnet") == -1:
            if is_postseason(time_stamp):
                end_time = SEASONS_INFO[season]['post_season_end_time']
            else:
                end_time = SEASONS_INFO[season]['end_time']

        if time_stamp >= SEASONS_INFO[season]['start_time'] and time_stamp <= end_time:
            return season

    return "Unofficial"


def get_season_server_from_addresses(address_list, chain):

    tx_chain = "KMD"
    if chain in ["BTC", "KMD", "LTC"]:
        tx_chain = chain

    if len(address_list) == 13:
        seasons = list(NOTARY_ADDRESSES_DICT.keys())[::-1]

        for season in seasons:
            notary_seasons = []
            season_notaries = list(NOTARY_ADDRESSES_DICT[season].keys())

            for notary in season_notaries:
                if season in NOTARY_ADDRESSES_DICT:
                    if notary in NOTARY_ADDRESSES_DICT[season]:
                        if tx_chain in NOTARY_ADDRESSES_DICT[season][notary]:
                            if NOTARY_ADDRESSES_DICT[season][notary][tx_chain] in address_list:
                                notary_seasons.append(season)

            if len(notary_seasons) == 13:
                break

        if len(notary_seasons) == 13 and len(set(notary_seasons)) == 1:
            ntx_season = notary_seasons[0].replace("_Third_Party", "").replace(".5", "")

            if chain in ["BTC", "KMD", "LTC"]:
                server = chain
            
            elif notary_seasons[0].find("_Third_Party") > -1:
                server = "Third_Party"
            else:
                server = "Main"

            return ntx_season, server

    return  "Unofficial", "Unofficial"


def get_chain_server(chain, season):
    if chain in ["KMD", "LTC", "BTC"]:
        return chain
    else:
        main_coins = requests.get(get_dpow_server_coins_url(season, 'Main')).json()["results"]
        third_party_coins = requests.get(get_dpow_server_coins_url(season, 'Third_Party')).json()["results"]
    if chain in main_coins:
        return "Main"
    elif chain in third_party_coins:
        return "Third_Party"
    else:
        return "Unofficial"


def get_season_notaries(season):
    if season in NOTARY_PUBKEYS:
        notaries = list(NOTARY_PUBKEYS[season].keys())
        notaries.sort()
        return notaries
    return []


def get_chain_epoch_score_at(season, server, chain, timestamp):
    if season in DPOW_EXCLUDED_CHAINS: 
        if chain not in DPOW_EXCLUDED_CHAINS[season]:
            if chain in ["BTC", "LTC"]:
                return 0
            if chain in ["KMD"]:
                season_start = SEASONS_INFO[season]["start_time"]
                season_end = SEASONS_INFO[season]["end_time"]
                if int(timestamp) >= season_start and int(timestamp) <= season_end:
                    return 0.0325
                return 0

            active_chains, num_coins = get_server_active_scoring_dpow_chains_at_time(
                                            season, server, timestamp
                                        )

            if chain in active_chains:
                if server == "Main":
                    return round(0.8698/num_coins, 8)
                elif server == "Third_Party":
                    return round(0.0977/num_coins, 8)
                elif server == "Testnet":
                    return round(0.0977/num_coins, 8)
    return 0


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
        if coin == "COQUICASH":
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/COQUI")
        elif coin == "WLC21":
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/WLC")
        elif coin == "PIRATE":
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/ARRR")
        elif coin == "TOKEL":
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/TKL")
        else:
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/"+coin)
        
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
        if coin == "COQUICASH":
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/explorers/COQUI")
        elif coin == "WLC21":
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/explorers/WLC")
        elif coin == "TOKEL":
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/explorers/TKL")
        else:
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/explorers/"+coin)

        for explorer in r.json():
            coins_data[coin]['explorers'].append(explorer.replace("/tx/", "/").replace("/tx.dws?", "/"))

    except Exception as e:
        if r.text != "404: Not Found":
            logger.error(f"Exception in [parse_electrum_explorer]: {e} {r.text}")
                
    return coins_data


def get_coins_repo_icons(coins_data, coin):
    try:
        if coin == "COQUICASH":
            url = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/icons/coqui.png"
            r = requests.get(url)
        elif coin == "GLEEC-OLD":
            url = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/icons/gleec.png"
            r = requests.get(url)
        elif coin == "TOKEL":
            url = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/icons/tkl.png"
            r = requests.get(url)
        elif coin == "PIRATE":
            url = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/icons/arrr.png"
            r = requests.get(url)
        elif coin == "WLC21":
            url = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/icons/wlc.png"
            r = requests.get(url)
        else:
            url = f"https://raw.githubusercontent.com/KomodoPlatform/coins/master/icons/{coin.lower()}.png"
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


def get_balance(chain, pubkey, addr, server):
    balance = -1
    try:
        if chain in ELECTRUMS:
            try:
                if chain == "GLEEC" and server == "Third_Party":
                    electrum = ELECTRUMS["GLEEC-OLD"][0].split(":")
                else:
                    electrum = ELECTRUMS[chain][0].split(":")
                url = electrum[0]
                port = electrum[1]
                balance = get_full_electrum_balance(pubkey, url, port)
            except Exception as e:
                logger.warning(">>>>> "+chain+" via ["+url+":"+str(port)+"] FAILED | addr: "+addr+" | "+str(e))
                try:
                    balance = get_dexstats_balance(chain, addr)
                    logger.info(f"{chain} via [DEXSTATS] OK | addr: {addr} | balance: {balance}")
                except Exception as e:
                    logger.warning(">>>>> "+chain+" via [DEXSTATS] FAILED | addr: "+addr+" | "+str(e))

        elif chain in ANTARA_COINS:
            try:
                balance = get_dexstats_balance(chain, addr)
            except Exception as e:
                logger.warning(">>>>> "+chain+" via [DEXSTATS] FAILED | addr: "+addr+" | "+str(e))

        elif chain == "AYA":
            url = 'https://explorer.aryacoin.io/ext/getaddress/'+addr
            r = requests.get(url)
            if 'balance' in r.json():
                balance = r.json()['balance']
            else:
                logger.warning(">>>>> "+chain+" via explorer.aryacoin.io FAILED | addr: "+addr+" | "+str(r.text))

    except Exception as e:
        logger.error(">>>>> "+chain+" FAILED ALL METHODS | addr: "+addr+" | "+str(e))
    return balance


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


@print_runtime
def get_server_epochs(season):
    server_epochs = {}
    servers = get_notarised_servers(season)
    for server in servers:
        server_epochs.update({
            server: get_notarised_epochs(season, server)
        })
    return server_epochs

@print_runtime
def get_server_epoch_chains(season, server_epochs):
    server_epoch_chains = {}
    for server in server_epochs:
        server_epoch_chains.update({
            server:{}
        })
        for epoch in server_epochs[server]:
            server_epoch_chains[server].update({
                epoch: get_notarised_chains(season, server, epoch)
            })
    return server_epoch_chains


def get_chain_ntx_count_dict(season, day):
    # get daily ntx total for each chain
    chain_ntx_count_dict = {}
    chains_aggr_resp = get_notarised_chain_date_aggregates(season, day)

    for item in chains_aggr_resp:
        chain = item[0]
        max_block = item[1]
        max_blocktime = item[2]
        ntx_count = item[3]
        chain_ntx_count_dict.update({chain:ntx_count})
    return chain_ntx_count_dict

def get_notary_ntx_count_dict(season, day):
    notary_ntx_count_dict = {}
    notarised_on_day = get_notarised_for_day(season, day)

    for item in notarised_on_day:
        notaries = item[1]
        chain = item[0]
        for notary in notaries:
            if notary not in notary_ntx_count_dict:
                notary_ntx_count_dict.update({notary:{}})
            if chain not in notary_ntx_count_dict[notary]:
                notary_ntx_count_dict[notary].update({chain:1})
            else:
                count = notary_ntx_count_dict[notary][chain]+1
                notary_ntx_count_dict[notary].update({chain:count})

    return notary_ntx_count_dict


def get_notary_count_categorized(notary_ntx_count_dict, chain_ntx_count_dict):

    season_main_coins = requests.get(
                        get_dpow_server_coins_url(season, 'Main')
                    ).json()["results"]

    season_3P_coins = requests.get(
                        get_dpow_server_coins_url(season, 'Third_Party')
                    ).json()["results"]

    # iterate over notary chain counts to calculate scoring category counts.
    notary_counts = {}
    notary_ntx_pct = {}

    for notary in notary_ntx_count_dict:
        notary_ntx_pct.update({notary:{}})
        notary_counts.update({notary:{
                "btc_count":0,
                "antara_count":0,
                "third_party_count":0,
                "other_count":0,
                "total_ntx_count":0
            }})

        for chain in notary_ntx_count_dict[notary]:
            if chain == "KMD":
                count = notary_counts[notary]["btc_count"] + notary_ntx_count_dict[notary][chain]
                notary_counts[notary].update({"btc_count":count})
            elif chain in season_main_coins:
                count = notary_counts[notary]["antara_count"] + notary_ntx_count_dict[notary][chain]
                notary_counts[notary].update({"antara_count":count})
            elif chain in season_3P_coins:
                count = notary_counts[notary]["third_party_count"] + notary_ntx_count_dict[notary][chain]
                notary_counts[notary].update({"third_party_count":count})
            else:
                count = notary_counts[notary]["other_count"] + notary_ntx_count_dict[notary][chain]
                notary_counts[notary].update({"other_count":count})

            count = notary_counts[notary]["total_ntx_count"] + notary_ntx_count_dict[notary][chain]
            notary_counts[notary].update({"total_ntx_count":count})

            pct = round(notary_ntx_count_dict[notary][chain] / chain_ntx_count_dict[chain] * 100, 2)
            notary_ntx_pct[notary].update({chain:pct})

    return notary_counts, notary_ntx_pct

