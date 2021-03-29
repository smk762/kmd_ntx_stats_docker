import time
import datetime
from django.db.models import Count, Min, Max, Sum
import logging
import random
import requests
import os
from dotenv import load_dotenv
from .models import *
from .lib_const import *
from .lib_query import *
from .lib_helper import *
from .lib_api import *
from .base_58 import *
logger = logging.getLogger("mylogger")

load_dotenv()

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


def get_funding_totals(funding_data):
    funding_totals = {"fees":{}}
    now = int(time.time())

    for item in funding_data:
        tx_time = day_hr_min_sec(now - item['block_time'])
        item.update({"time": tx_time})

        if item["notary"] not in ["unknown", "funding bot"]:
            if item["notary"] not in funding_totals:
                funding_totals.update({item["notary"]:{}})

            if item["chain"] not in funding_totals[item["notary"]]:
                funding_totals[item["notary"]].update({item["chain"]:-item["amount"]})
            else:
                val = funding_totals[item["notary"]][item["chain"]]-item["amount"]
                funding_totals[item["notary"]].update({item["chain"]:val})

            if item["chain"] not in funding_totals["fees"]:
                funding_totals["fees"].update({item["chain"]:-item["fee"]})
            else:
                val = funding_totals["fees"][item["chain"]]-item["fee"]
                funding_totals["fees"].update({item["chain"]:val})

    return funding_totals

def get_dpow_explorers():
    resp = {}
    coins_data = coins.objects.filter(dpow_active=1).values('chain','explorers')
    for item in coins_data:
        explorers = item['explorers']
        if len(explorers) > 0:
            chain = item['chain']
            resp.update({chain:explorers[0].replace('tx/','')})
    return resp


def get_notary_ntx_24hr_summary(ntx_24hr, notary):
    notary_ntx_24hr = {
            "btc_ntx":0,
            "main_ntx":0,
            "third_party_ntx":0,
            "most_ntx":"N/A"
        }
    coins_data = get_active_dpow_coins()
    main_chains = get_mainnet_chains(coins_data)
    third_party_chains = get_third_party_chains(coins_data)

    notary_chain_ntx_counts = {}
    for item in ntx_24hr:
        notaries = item['notaries']
        chain = item['chain']
        if notary in notaries:
            if chain not in notary_chain_ntx_counts:
                notary_chain_ntx_counts.update({chain:1})
            else:
                val = notary_chain_ntx_counts[chain]+1
                notary_chain_ntx_counts.update({chain:val})

    max_ntx_count = 0
    btc_ntx_count = 0
    main_ntx_count = 0
    third_party_ntx_count = 0
    for chain in notary_chain_ntx_counts:
        chain_ntx_count = notary_chain_ntx_counts[chain]
        if chain_ntx_count > max_ntx_count:
            max_chain = chain
            max_ntx_count = chain_ntx_count
        if chain == "BTC":
            btc_ntx_count += chain_ntx_count
        elif chain in main_chains:
            main_ntx_count += chain_ntx_count
        elif chain in third_party_chains:
            third_party_ntx_count += chain_ntx_count
    if max_ntx_count > 0:
        notary_ntx_24hr.update({
                "btc_ntx":btc_ntx_count,
                "main_ntx":main_ntx_count,
                "third_party_ntx":third_party_ntx_count,
                "most_ntx":str(max_ntx_count)+" ("+str(max_chain)+")"
            })
    return notary_ntx_24hr

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
        region = notary.split('_')[-1]
        regions_info[region]['nodes'].append(notary)
    return regions_info

def get_server_info(coins_list):
    coins_list.sort()
    coins_info = {
        'main':{ 
            "name":"Main server",
            "coins":[]
            },
        'third':{ 
            "name":"Third Party Server",
            "coins":[]
            }
    }
    coins_data = coins.objects.filter(dpow_active=1).values('chain','dpow')
    server_chains = get_server_chains(coins_data)
    for coin in coins_list:
        if coin in server_chains['main']:
            server = "main"
        elif coin in server_chains['third_party']:
            server = "third"
        coins_info[server]['coins'].append(coin)
    return coins_info

def get_eco_data_link():
    item = random.choice(eco_data)
    ad = random.choice(item['ads'])
    while ad['frequency'] == "never":
        item = random.choice(eco_data)
        ad = random.choice(item['ads'])
    link = ad['data']['string1']+" <a href="+ad['data']['link']+"> " \
          +ad['data']['anchorText']+"</a> "+ad['data']['string2']
    return link

def get_coin_social(coin=None):
    season = get_season()
    coin_social_info = {}
    if coin:
        coin_social_data = coin_social.objects.filter(season=season, chain=coin).values()
    else:
        coin_social_data = coin_social.objects.all().values()
    for item in coin_social_data:
        coin_social_info.update(items_row_to_dict(item,'chain'))
    for coin in coin_social_info:
        for item in coin_social_info[coin]:
            if item in ['twitter', 'youtube', 'discord', 'telegram', 'github', 'explorer', 'website']:
                if coin_social_info[coin][item].endswith('/'):
                    coin_social_info[coin][item] = coin_social_info[coin][item][:-1]
                coin_social_info[coin][item] = coin_social_info[coin][item].replace("http://", "")
                coin_social_info[coin][item] = coin_social_info[coin][item].replace("https://", "")
                coin_social_info[coin][item] = coin_social_info[coin][item].replace("t.me/", "")
                coin_social_info[coin][item] = coin_social_info[coin][item].replace("twitter.com/", "")
                coin_social_info[coin][item] = coin_social_info[coin][item].replace("github.com/", "")
                coin_social_info[coin][item] = coin_social_info[coin][item].replace("www.youtube.com/", "")
    return coin_social_info

def get_nn_social(notary_name=None):
    season = get_season()
    nn_social_info = {}
    if notary_name:
        nn_social_data = nn_social.objects.filter(season=season, notary=notary_name).values()
    else:
        nn_social_data = nn_social.objects.all().values()
    for item in nn_social_data:
        nn_social_info.update(items_row_to_dict(item,'notary'))
    for notary in nn_social_info:
        for item in nn_social_info[notary]:
            if item in ['twitter', 'youtube', 'discord', 'telegram', 'github', 'keybase']:   
                if nn_social_info[notary][item].endswith('/'):
                   nn_social_info[notary][item] = nn_social_info[notary][item][:-1]
                nn_social_info[notary][item] = nn_social_info[notary][item].replace("https://", "")
                nn_social_info[notary][item] = nn_social_info[notary][item].replace("https://", "")
                nn_social_info[notary][item] = nn_social_info[notary][item].replace("t.me/", "")
                nn_social_info[notary][item] = nn_social_info[notary][item].replace("twitter.com/", "")
                nn_social_info[notary][item] = nn_social_info[notary][item].replace("github.com/", "")
                nn_social_info[notary][item] = nn_social_info[notary][item].replace("www.youtube.com/", "")
                nn_social_info[notary][item] = nn_social_info[notary][item].replace("keybase.io/", "")

    return nn_social_info

def get_nn_ntx_summary(notary):
    season = get_season()
    now = int(time.time())
    day_ago = now - 24*60*60
    week_ago = now - 24*60*60*7

    today = datetime.date.today()
    delta = datetime.timedelta(days=1)
    week_ago = today-delta*7

    ntx_summary = {
        "today":{
            "btc_ntx":0,
            "main_ntx":0,
            "third_party_ntx":0,
            "most_ntx":str(0)+" ("+str('-')+")"
        },
        "season":{
            "btc_ntx":0,
            "main_ntx":0,
            "third_party_ntx":0,
            "most_ntx":str(0)+" ("+str('-')+")"
        },
        "time_since_last_btc_ntx":-1,
        "time_since_last_ntx":-1,
        "last_ntx_chain":'-',
        "premining_ntx_score":0,
    }

    # 24hr ntx 
    ntx_24hr = notarised.objects.filter(
        block_time__gt=str(int(time.time()-24*60*60))
        ).values()

    notary_ntx_24hr_summary = get_notary_ntx_24hr_summary(ntx_24hr, notary)
    ntx_summary.update({"today":notary_ntx_24hr_summary})


    # season ntx stats
    ntx_season = notarised_count_season.objects \
                                    .filter(season=season, notary=notary) \
                                    .values()

    if len(ntx_season) > 0:
        chains_ntx_season = ntx_season[0]['chain_ntx_counts']
        season_max_chain = max(chains_ntx_season, key=chains_ntx_season.get) 
        season_max_ntx = chains_ntx_season[season_max_chain]

        ntx_summary['season'].update({
            "btc_ntx":ntx_season[0]['btc_count'],
            "main_ntx":ntx_season[0]['antara_count'],
            "third_party_ntx":ntx_season[0]['third_party_count'],
            "most_ntx":season_max_chain+" ("+str(season_max_ntx)+")"
        })
        ntx_summary.update({
            "premining_ntx_score":get_ntx_score(
                ntx_season[0]['btc_count'],
                ntx_season[0]['antara_count'],
                ntx_season[0]['third_party_count']
            ),
        })

    #last ntx data
    ntx_last = last_notarised.objects \
                             .filter(season=season, notary=notary) \
                             .values()
    last_chain_ntx_times = {}
    for item in ntx_last:
        if item['chain'] != "KMD":
            last_chain_ntx_times.update({item['chain']:item['block_time']})

    if len(last_chain_ntx_times) > 0:
        max_last_ntx_chain = max(last_chain_ntx_times, key=last_chain_ntx_times.get) 
        max_last_ntx_time = last_chain_ntx_times[max_last_ntx_chain]
        time_since_last_ntx = int(time.time()) - int(max_last_ntx_time)
        time_since_last_ntx = day_hr_min_sec(time_since_last_ntx)
        ntx_summary.update({
            "time_since_last_ntx":time_since_last_ntx,
            "last_ntx_chain":max_last_ntx_chain,
        })

    if "BTC" in last_chain_ntx_times:
        max_btc_ntx_time = last_chain_ntx_times["BTC"]
        time_since_last_btc_ntx = int(time.time()) - int(max_btc_ntx_time)
        time_since_last_btc_ntx = day_hr_min_sec(time_since_last_btc_ntx)
        ntx_summary.update({
            "time_since_last_btc_ntx":time_since_last_btc_ntx,
        })


    return ntx_summary

# notary > chain > data
def get_last_nn_chain_ntx(season):
    ntx_last = last_notarised.objects \
                             .filter(season=season) \
                             .values()
    last_nn_chain_ntx = {}
    for item in ntx_last:
        notary = item['notary']
        if notary not in last_nn_chain_ntx:
            last_nn_chain_ntx.update({notary:{}})
        chain = item['chain']
        if chain != "KMD":
            time_since = int(time.time()) - int(item['block_time'])
            time_since = day_hr_min_sec(time_since)
            last_nn_chain_ntx[notary].update({
                chain:{
                    "txid": item['txid'],
                    "block_height": item['block_height'],
                    "block_time": item['block_time'],
                    "time_since": time_since
                }
            })
    return last_nn_chain_ntx

# chain > data
def get_season_chain_ntx_data(season):
    ntx_season = notarised_chain_season.objects \
                                    .filter(season=season) \
                                    .values()
    dpow_coins_list = get_dpow_coins_list()
    season_chain_ntx_data = {}
    if len(ntx_season) > 0:
        for item in ntx_season:
            time_since_last_ntx = int(time.time()) - int(item['kmd_ntx_blocktime'])
            time_since_last_ntx = day_hr_min_sec(time_since_last_ntx)
            if item['chain'] in dpow_coins_list:
                if item['chain'] != 'KMD':
                    season_chain_ntx_data.update({
                        item['chain']: {
                            'chain_ntx_season':item['ntx_count'],
                            'last_ntx_time':item['kmd_ntx_blocktime'],
                            'time_since_ntx':time_since_last_ntx,
                            'last_ntx_block':item['block_height'],
                            'last_ntx_hash':item['kmd_ntx_blocktime'],
                            'last_ntx_ac_block':item['ac_ntx_height'],
                            'ac_block_height':item['ac_block_height'],
                            'ac_ntx_blockhash':item['ac_ntx_blockhash'],
                            'ntx_lag':item['ntx_lag']
                        }
                    })
    return season_chain_ntx_data

# notary > chain > count
def get_nn_season_ntx_counts(season):
    ntx_season = notarised_count_season.objects \
                                    .filter(season=season) \
                                    .values()
    nn_season_ntx_counts = {}
    for item in ntx_season:
        nn_season_ntx_counts.update({
            item['notary']:item['chain_ntx_counts']
        })
    return nn_season_ntx_counts

def get_season_nn_chain_ntx_data(season):
    notary_list = get_notary_list(season)
    coins_list = get_dpow_coins_list()
    nn_season_ntx_counts = get_nn_season_ntx_counts(season)
    season_chain_ntx_data = get_season_chain_ntx_data(season)
    last_nn_chain_ntx = get_last_nn_chain_ntx(season)
    season_nn_chain_ntx_data = {}
    for notary in notary_list:
        for chain in coins_list:
            if chain != "KMD":
                total_chain_ntx = 0
                last_ntx_block = 0
                num_nn_chain_ntx = 0
                time_since = "N/A"
                participation_pct = 0
                if chain in season_chain_ntx_data:
                    total_chain_ntx = season_chain_ntx_data[chain]['chain_ntx_season']
                else:
                    total_chain_ntx = 0

                if notary in nn_season_ntx_counts:
                    num_nn_chain_ntx = nn_season_ntx_counts[notary]
                else:
                    num_nn_chain_ntx = 0

                if notary in last_nn_chain_ntx:
                    if chain in last_nn_chain_ntx[notary]:
                        time_since = last_nn_chain_ntx[notary][chain]["time_since"]
                        last_ntx_block = last_nn_chain_ntx[notary][chain]['block_height']
                        last_ntx_txid = last_nn_chain_ntx[notary][chain]['txid']
                    else:
                        time_since = ''
                        last_ntx_block = ''
                        last_ntx_txid = ''
                else:
                    time_since = ''
                    last_ntx_block = ''
                    last_ntx_txid = ''

                if total_chain_ntx != 0 and not isinstance(num_nn_chain_ntx, int):
                    if chain in num_nn_chain_ntx:
                        participation_pct = round(num_nn_chain_ntx[chain]/total_chain_ntx*100,2)
                    else:
                        participation_pct = 0
                else:
                    participation_pct = 0

                if notary not in season_nn_chain_ntx_data:
                    season_nn_chain_ntx_data.update({notary:{}})
                if not isinstance(num_nn_chain_ntx, int):
                    if chain in num_nn_chain_ntx:
                        num_ntx = num_nn_chain_ntx[chain]
                    else:
                        num_ntx = 0
                else:
                    num_ntx = 0

                season_nn_chain_ntx_data[notary].update({
                    chain: {
                        "num_nn_chain_ntx":num_ntx,
                        "time_since":time_since,
                        "last_ntx_block":last_ntx_block,
                        "last_ntx_txid":last_ntx_txid,
                        "participation_pct":participation_pct
                    }
                })
    return season_nn_chain_ntx_data
                     
def get_nn_mining_summary(notary):
    season = get_season()
    now = int(time.time())
    day_ago = now - 24*60*60
    week_ago = now - 24*60*60*7

    mining_summary = {
        "mined_last_24hrs": 0,
        "season_value_mined": 0,
        "season_blocks_mined": 0,
        "season_largest_block": 0,
        "largest_block_height": 0,
        "last_mined_datetime": -1,
        "time_since_mined": -1,
    }
    notary_mined = mined.objects.filter(season=season, name=notary)

    mined_last_24hrs = notary_mined.filter(block_time__gte=str(day_ago), block_time__lte=str(now)) \
                      .values('name').annotate(mined_24hrs=Sum('value'))

    if len(mined_last_24hrs) > 0:
        mining_summary.update({
            "mined_last_24hrs": float(mined_last_24hrs[0]['mined_24hrs'])
        })



    mined_this_season = get_mined_this_season()
    if len(mined_last_24hrs) > 0:
        time_since_mined = int(time.time()) - int(mined_this_season[0]['last_mined_time'])
        time_since_mined = day_hr_min_sec(time_since_mined)
        mining_summary.update({
            "season_value_mined": float(mined_this_season[0]['season_value_mined']),
            "season_blocks_mined": int(mined_this_season[0]['season_blocks_mined']),
            "season_largest_block": float(mined_this_season[0]['season_largest_block']),
            "last_mined_datetime": mined_this_season[0]['last_mined_datetime'],
            "time_since_mined": time_since_mined,
            "largest_block_height": int(mined_this_season[0]['last_mined_block']),
        })
    logger.info(mining_summary)
    return mining_summary

def get_nn_info():
    # widget using this has been deprecated, but leaving code here for reference
    # to use in potential replacement functions.
    season = get_season()
    notary_list = get_notary_list(season)
    regions_info = get_regions_info(notary_list)
    nn_info = {
        "regions_info":regions_info,
    }
    return nn_info

def get_coin_info():
    # widget using this has been deprecated, but leaving code here for reference
    # to use in potential replacement functions.
    season = get_season()
    coins_list = get_dpow_coins_list()
    server_info = get_server_info(coins_list)
    coins_info = {
        "server_info":server_info,
    }
    return coins_info

def get_coin_ntx_summary(coin):
    now = int(time.time())
    season = get_season(now)

    chain_ntx_summary = {
            'chain_ntx_today':0,
            'chain_ntx_season':0,
            'last_ntx_time':'',
            'time_since_ntx':'',
            'last_ntx_block':'',
            'last_ntx_hash':'',
            'last_ntx_ac_block':'',
            'last_ntx_ac_hash':'',
            'ntx_lag':-1
    }
    
    # today's ntx stats
    today = datetime.date.today()
    # 24hr ntx 
    chain_ntx_24hr = notarised.objects.filter(
        block_time__gt=str(now-24*60*60), chain=coin).count()

    chain_ntx_summary.update({
        'chain_ntx_today':chain_ntx_24hr
    })

    # season ntx stats
    ntx_season = notarised_chain_season.objects \
                                    .filter(season=season, chain=coin) \
                                    .values()
    if len(ntx_season) > 0:
        time_since_last_ntx = now - int(ntx_season[0]['kmd_ntx_blocktime'])
        time_since_last_ntx = day_hr_min_sec(time_since_last_ntx)
        chain_ntx_summary.update({
            'chain_ntx_season':ntx_season[0]['ntx_count'],
            'last_ntx_time':ntx_season[0]['kmd_ntx_blocktime'],
            'time_since_ntx':time_since_last_ntx,
            'last_ntx_block':ntx_season[0]['block_height'],
            'last_ntx_hash':ntx_season[0]['kmd_ntx_blocktime'],
            'last_ntx_ac_block':ntx_season[0]['ac_ntx_height'],
            'last_ntx_ac_hash':ntx_season[0]['ac_ntx_blockhash'],
            'ntx_lag':ntx_season[0]['ntx_lag']
        })
    return chain_ntx_summary

def get_balances_dict(filter_kwargs):
    balances_dict = {}
    balances_data = balances.objects.filter(**filter_kwargs).order_by('notary', 'chain').values('notary', 'chain', 'balance')
    for item in balances_data:
        if item['notary'] not in balances_dict:
            balances_dict.update({item['notary']:{}})
        if item['chain'] not in balances_dict[item['notary']]:
            balances_dict[item['notary']].update({item['chain']:item['balance']})
        else:
            bal = balances_dict[item['notary']][item['chain']] + item['balance']
            balances_dict[item['notary']].update({item['chain']:bal})
    return balances_dict  

def get_low_balances(notary_list, balances_dict, ignore_chains):
    low_balances_dict = {}
    sufficient_balance_count = 0
    low_balance_count = 0
    for notary in notary_list:
        if notary in balances_dict:
            for chain in balances_dict[notary]:
                if chain not in ignore_chains:
                    bal = balances_dict[notary][chain]
                    if bal < 0.03:
                        if notary not in low_balances_dict:
                            low_balances_dict.update({notary:{}})
                        if chain not in low_balances_dict[notary]:
                                low_balances_dict[notary].update({chain:str(round(bal.normalize(),4))})
                        low_balance_count += 1
                    else:
                        sufficient_balance_count += 1
    return low_balances_dict, low_balance_count, sufficient_balance_count

def get_low_balance_tooltip(low_balances, ignore_chains):
    low_balances_dict = low_balances[0]
    low_balance_count = low_balances[1]
    sufficient_balance_count = low_balances[2]
    low_balances_pct = round(sufficient_balance_count/(low_balance_count+sufficient_balance_count)*100,2)
    low_balances_tooltip = "<h4 class='kmd_teal'>"+str(sufficient_balance_count)+"/"+str(low_balance_count+sufficient_balance_count)+" ("+str(low_balances_pct)+"%)</h4>\n"
    low_balances_tooltip += "<h6 class='kmd_ui_light1'>where balances < 0.03 </h6>\n"
    low_balances_tooltip += "<h6 class='kmd_ui_light1'>"+str(ignore_chains)+" ignored (no electrum) </h6>\n"
    # open container
    low_balances_tooltip += "<div class='container m-auto' style='width:100%;'>\n"
    i = 1
    notaries = list(low_balances_dict.keys())
    notaries.sort()
    notaries = region_sort(notaries)
    for notary in notaries:
        if i == 1:
            # open row
            low_balances_tooltip += "<div class='row m-auto py-1' style='width:100%;'>\n"
        # open col
        low_balances_tooltip += "<div class='col'><b class='kmd_teal'>"+notary.upper()+"</b><br />"
        if len(low_balances_dict[notary]) > 3:
            low_balances_tooltip += "<b class='kmd_secondary_red'>>3 CHAINS<br /> LOW BALANCE!!!<br /></b>"
        else:
            for chain in low_balances_dict[notary]:
                bal = low_balances_dict[notary][chain]
                low_balances_tooltip += "<b>"+chain+": </b>"+bal+"<br />"
        low_balances_tooltip += "</div>\n"
        # close col
        if i == 5 or notary == notaries[-1]:
            i = 0
            # close row
            low_balances_tooltip += "</div>\n"
        i += 1
    # close container
    low_balances_tooltip += "</div>"
    return low_balances_tooltip

def get_sidebar_links(notary_list, coins_data):
    region_notaries = get_regions_info(notary_list)
    server_chains = get_server_chains(coins_data)
    sidebar_links = {
        "server":os.getenv("SERVER"),
        "chains_menu":server_chains,
        "notaries_menu":region_notaries,
    }
    return sidebar_links

def get_btc_split_stats(address):
    resp = {}
    filter_kwargs = {}
    data = nn_btc_tx.objects.filter(category="Split or Consolidate").filter(address=address)
    sum_fees = data.annotate(Sum("fees"))
    num_splits = data.exclude().distinct("txid")
    avg_split_size = 0
    for item in data:        
        address = item['address']

        if address not in resp:
            resp.update({address:[]})
        resp[address].append(item)

    return wrap_api(resp)

def get_daily_stats_sorted(notary_list):

    now = int(time.time())
    day_ago = now - 24*60*60
    mined_last_24hrs = mined.objects.filter(block_time__gte=str(day_ago), block_time__lte=str(now)) \
                      .values('name').annotate(mined_24hrs=Sum('value'), blocks_24hrs=Count('value'))

    nn_mined_last_24hrs = {}
    for item in mined_last_24hrs:
        nn_mined_last_24hrs.update({item['name']:item['blocks_24hrs']})

    ntx_24hr = notarised.objects.filter(
        block_time__gt=str(int(time.time()-24*60*60))
        ).values()

    daily_stats = {}
    for notary_name in notary_list:
        region = get_notary_region(notary_name)
        notary_ntx_24hr_summary = get_notary_ntx_24hr_summary(ntx_24hr, notary_name)
        score = get_ntx_score(
            notary_ntx_24hr_summary["btc_ntx"],
            notary_ntx_24hr_summary["main_ntx"],
            notary_ntx_24hr_summary["third_party_ntx"]
        )

        if region not in daily_stats:
            daily_stats.update({region:[]})

        if notary_name not in nn_mined_last_24hrs:
            nn_mined_last_24hrs.update({notary_name:0})

        daily_stats[region].append({
            "notary":notary_name,
            "btc":notary_ntx_24hr_summary["btc_ntx"],
            "main":notary_ntx_24hr_summary["main_ntx"],
            "third_party":notary_ntx_24hr_summary["third_party_ntx"],
            "mining":nn_mined_last_24hrs[notary_name],
            "score":score,
        })

    daily_stats_sorted = {}
    for region in daily_stats:
        daily_stats_sorted.update({region:[]})
        scores_dict = {}
        for item in daily_stats[region]:
            scores_dict.update({item['notary']:item['score']})
        sorted_scores = {k: v for k, v in sorted(scores_dict.items(), key=lambda x: x[1])}
        dec_sorted_scores = dict(reversed(list(sorted_scores.items()))) 
        i = 1
        for notary in dec_sorted_scores:
            for item in daily_stats[region]:
                if notary == item['notary']:
                    new_item = item.copy()
                    new_item.update({"rank":i})
                    daily_stats_sorted[region].append(new_item)
            i += 1
    return daily_stats_sorted

def get_split_stats():
    resp = get_btc_txid_data("splits")
    split_summary = {}
    for address in resp["results"][0]:
        for tx in resp["results"][0][address]:

            nn_name = tx["notary"]
            if nn_name not in split_summary:
                split_summary.update({
                    nn_name:{}
                })

            season = tx["season"]
            if season not in split_summary[nn_name]:
                split_summary[nn_name].update({
                    season: {
                        "split_count":0,
                        "last_split_block":0,
                        "last_split_time":0,
                        "sum_split_utxos":0,
                        "average_split_utxos":0,
                        "sum_fees":0,
                        "txids":[]
                    }
                })

            fees = int(tx["fees"])/100000000
            num_outputs = int(tx["num_outputs"])
            split_summary[nn_name][season].update({
                "split_count":split_summary[nn_name][season]["split_count"]+1,
                "sum_split_utxos":split_summary[nn_name][season]["sum_split_utxos"]+num_outputs,
                "sum_fees":split_summary[nn_name][season]["sum_fees"]+fees
            })

            split_summary[nn_name][season].update({
                "average_split_utxos":split_summary[nn_name][season]["sum_split_utxos"]/split_summary[nn_name][season]["split_count"],
            })

            txid = tx["txid"]
            
            split_summary[nn_name][season]["txids"].append(txid)

            block_height = int(tx["block_height"])
            block_time = int(tx["block_time"])
            if block_time > split_summary[nn_name][season]["last_split_time"]:
                split_summary[nn_name][season].update({
                    "last_split_block":block_height,
                    "last_split_time":block_time
                })
    return split_summary

def get_split_stats_table():
    split_summary = get_split_stats()
    split_rows = []
    for nn in split_summary:
        if nn != 'non-NN':
            row = split_summary[nn]['Season_4']
            row.append(nn)
            split_rows.append(row)
    return split_rows

def get_address_from_pubkey(request):
    coin = "KMD"
    if "coin" in request.GET:
        if request.GET["coin"] in COIN_PARAMS:
            coin = request.GET["coin"]

    if "pubkey" in request.GET:
        pubkey = request.GET["pubkey"]
        return {
            "coin": coin,
            "pubkey": pubkey,
            "address": get_addr_from_pubkey(coin, pubkey)
        }

    else:
        return {
            "Error": "You need to specify a pubkey and coin like '?coin=KMD&pubkey=<YOUR_PUBKEY>'\nIf coin not specified or unknown, will revert to KMD"
        }

def get_testnet_addresses(season):
    addresses_dict = {}
    addresses_data = addresses.objects.filter(season=season, chain="KMD")
    addresses_data = addresses_data.order_by('notary').values()

    for item in addresses_data:
        if item["notary"] not in addresses_dict: 
            addresses_dict.update({item["notary"]:item['address']})

    return addresses_dict

def prepare_testnet_stats_dict(season, testnet_chains):
    notaries = get_notary_list(season)
    testnet_stats_dict = create_dict(notaries)

    addresses_dict = get_testnet_addresses(season)

    testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, "Total")
    testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, "Rank")
    testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, "24hr_Total")
    testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, "24hr_Rank")
    testnet_stats_dict = add_string_dict_nest(testnet_stats_dict, "Address")

    for chain in testnet_chains:
        testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, chain)
        testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, f"24hr_{chain}")
        testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, f"Last_{chain}")

    for notary in testnet_stats_dict:
        if notary in addresses_dict:
            address = addresses_dict[notary]
            testnet_stats_dict[notary].update({"Address":address})
    return testnet_stats_dict

def get_api_testnet(request):
    season = "Season_5_Testnet"

    # Prepare ntx data
    ntx_data = notarised.objects.filter(season=season) \
            .order_by('chain', '-block_height') \
            .values()

    # Prepare 24hr ntx data
    ntx_data_24hr = notarised.objects.filter(season=season, 
        block_time__gt=str(int(time.time()-24*60*60))) \
        .order_by('chain', '-block_height') \
        .values()

    ntx_dict = {}
    ntx_dict_24hr = {}

    for item in ntx_data:
        chain = item['chain']
        if chain not in ntx_dict:
            ntx_dict.update({chain:[]})
            ntx_dict_24hr.update({chain:[]})
        # RICK/MORTY heights from gcharang
        # https://discord.com/channels/412898016371015680/455755767132454913/823823358768185344
        if chain in ["RICK", "MORTY"] and item["block_height"] >= 2316959:
            ntx_dict[chain].append(item)
        elif chain in ["LTC"] and item["block_height"] >= 2022000:
            ntx_dict[chain].append(item)
            print(item)


    for item in ntx_data_24hr:
        chain = item['chain']
        if chain in ["RICK", "MORTY"] and item["block_height"] >= 2316959:
            ntx_dict_24hr[chain].append(item)
        elif chain in ["LTC"] and item["block_height"] >= 2022000:
            ntx_dict_24hr[chain].append(item)
            print(item)

    testnet_chains = list(ntx_dict.keys())

    testnet_stats_dict = prepare_testnet_stats_dict(season, testnet_chains)

    last_notarisations = get_last_nn_chain_ntx(season)

    for chain in testnet_chains:

        # Get last notarised times
        for notary in testnet_stats_dict:
            try:
                last_chain_ntx = last_notarisations[notary][chain]["time_since"]
                testnet_stats_dict[notary].update({f"Last_{chain}":last_chain_ntx})
            except Exception as e:
                print(e)
                testnet_stats_dict[notary].update({f"Last_{chain}":"> 24hrs"})

        # Get notarisation counts
        for item in ntx_dict[chain]:
            ntx_notaries = item["notaries"]

            for notary in ntx_notaries:
                if notary in testnet_stats_dict:

                    if testnet_stats_dict[notary]["Total"] == 0:
                        testnet_stats_dict[notary].update({"Total":1})

                    else:
                        count = testnet_stats_dict[notary]["Total"]+1
                        testnet_stats_dict[notary].update({"Total":count})

                    if testnet_stats_dict[notary][chain] == 0:
                        testnet_stats_dict[notary].update({chain:1})
                        testnet_stats_dict[notary].update({chain:1})
                        
                    else:
                        count = testnet_stats_dict[notary][chain]+1
                        testnet_stats_dict[notary].update({chain:count})
                else:
                    print(item)

        # Get notarisation counts 24hr
        for item in ntx_dict_24hr[chain]:
            ntx_notaries = item["notaries"]

            for notary in ntx_notaries:
                if notary in testnet_stats_dict:

                    if testnet_stats_dict[notary]["24hr_Total"] == 0:
                        testnet_stats_dict[notary].update({"24hr_Total":1})

                    else:
                        count = testnet_stats_dict[notary]["24hr_Total"]+1
                        testnet_stats_dict[notary].update({"24hr_Total":count})

                    if testnet_stats_dict[notary][chain] == 0:
                        testnet_stats_dict[notary].update({f"24hr_{chain}":1})
                        testnet_stats_dict[notary].update({f"24hr_{chain}":1})
                        
                    else:
                        count = testnet_stats_dict[notary][f"24hr_{chain}"]+1
                        testnet_stats_dict[notary].update({f"24hr_{chain}":count})
                else:
                    print(item)


    # Get notarisation rank
    notary_totals = {}
    for notary in testnet_stats_dict:
        notary_totals.update({notary:testnet_stats_dict[notary]["Total"]})
    ranked_totals = {k: v for k, v in sorted(notary_totals.items(), key=lambda x: x[1])}
    ranked_totals = dict(reversed(list(ranked_totals.items()))) 

    i = 0
    for notary in ranked_totals:
        i += 1
        testnet_stats_dict[notary].update({"Rank":i})

    # Get 24hr notarisation rank
    notary_totals_24hr = {}
    for notary in testnet_stats_dict:
        notary_totals_24hr.update({notary:testnet_stats_dict[notary]["24hr_Total"]})
    ranked_totals_24hr = {k: v for k, v in sorted(notary_totals_24hr.items(), key=lambda x: x[1])}
    ranked_totals_24hr = dict(reversed(list(ranked_totals_24hr.items()))) 

    i = 0
    for notary in ranked_totals_24hr:
        i += 1
        testnet_stats_dict[notary].update({"24hr_Rank":i})

    return wrap_api(testnet_stats_dict)

