#!/usr/bin/env python3
import time
import logging
import datetime
from datetime import datetime as dt
from .models import *
from .lib_const import *
#from .lib_info import *

from django.db.models import Count, Min, Max, Sum
from .lib_helper import *
from .lib_api import *
from kmd_ntx_api.serializers import *
logger = logging.getLogger("mylogger")

def get_notary_addresses(notary, season=None):
    if season:
        return addresses.objects.filter(notary=notary, season=season) \
                                .order_by('chain') \
                                .values('chain','address')
    else:
        return addresses.objects.filter(notary=notary) \
                                .order_by('chain') \
                                .values('chain','address')

def get_chain_addresses(chain, season=None):
    if season:
        return addresses.objects.filter(chain=chain, season=season) \
                                .order_by('notary') \
                                .values('notary','address')
    else:
        return addresses.objects.filter(chain=chain) \
                                .order_by('notary') \
                                .values('notary','address')

def get_notary_balances(notary, season=None):
    if season:
        return balances.objects.filter(season=season, notary=notary) \
                               .order_by('-season','notary', 'chain', 'balance') \
                               .values()
    else:
        return balances.objects.filter(notary=notary) \
                               .order_by('-season','notary', 'chain', 'balance') \
                               .values()

def get_chain_balances(notary, season=None):
    if season:
        return balances.objects.filter(season=season, chain=chain) \
                               .order_by('-season','notary', 'chain', 'balance') \
                               .values()
    else:
        return balances.objects.filter(chain=chain) \
                               .order_by('-season','notary', 'chain', 'balance') \
                               .values()

def get_nn_social_data(request):
    if "season" in request.GET and "notary" in request.GET:
        return nn_social.objects.filter(season=season, notary=notary) \
                               .order_by('-season','notary', 'chain', 'balance') \
                               .values()        
    if "season" in request.GET:
        return nn_social.objects.filter(season=season) \
                               .order_by('-season','notary', 'chain', 'balance') \
                               .values()
    if "notary" in request.GET:
        return nn_social.objects.filter(notary=notary) \
                               .order_by('-season','notary', 'chain', 'balance') \
                               .values()
    return nn_social.objects.all() \
                           .order_by('-season','notary', 'chain', 'balance') \
                           .values()

def get_notary_season_mined(season, notary):
    return mined.objects.filter(season=season, name=notary)

def get_notary_season_aggr(season, notary):
    now = int(time.time())
    return mined.objects.filter(name=notary, block_time__gte=SEASONS_INFO[season]['start_time'],
                          block_time__lte=str(now)) \
                         .values('name').annotate(season_value_mined=Sum('value'),\
                                            season_blocks_mined=Count('value'),
                                            season_largest_block=Max('value'),
                                            last_mined_datetime=Max('block_datetime'),
                                            last_mined_block=Max('block_height'),
                                            last_mined_time=Max('block_time'))

def get_notary_mined_last_24hrs(notary):
    now = int(time.time())
    day_ago = now - 24*60*60
    return mined.objects.filter(name=notary, block_time__gte=str(day_ago), block_time__lte=str(now)) \
                      .values('name').annotate(mined_24hrs=Sum('value'))

def get_btc_txid_data(category=None):
    resp = {}
    filter_kwargs = {}
    data = nn_btc_tx.objects.exclude(category="SPAM")
    print(category)
    if not category:
        resp = []
        for item in data:
            resp.append(item)
    else:
        if category == "NTX":
            data = nn_btc_tx.objects.filter(category="NTX")
        elif category == "splits":
            data = nn_btc_tx.objects.filter(category="Split")
        elif category == "SPAM":
            data = nn_btc_tx.objects.filter(category="SPAM")
        if category == "other":
            data = nn_btc_tx.objects.exclude(category="Split").exclude(category="NTX").exclude(category="SPAM")

        data = data.order_by('-block_height','address').values()

        for item in data:        
            address = item['address']

            if address not in resp:
                resp.update({address:[]})
            resp[address].append(item)

    return wrap_api(resp)

def get_all_coins():

    resp = []
    data = coins.objects.all()
    for item in data:
        resp.append(item.chain)
    return resp

def get_notarisation_txid_single(txid=None):

    data = notarised.objects.filter(txid=txid)

    for item in data:

        return {
            "chain":item.chain,
            "txid":item.txid,
            "block_hash":item.block_hash,
            "block_height":item.block_height,
            "block_time":item.block_time,
            "block_datetime":item.block_datetime,
            "notaries":item.notaries,
            "notary_addresses":item.notary_addresses,
            "ac_ntx_blockhash":item.ac_ntx_blockhash,
            "ac_ntx_height":item.ac_ntx_height,
            "opret":item.opret,
            "season":item.season,
            "server":item.server,
            "epoch":item.epoch,
            "scored":item.scored,
            "score_value":item.score_value,
            "btc_validated":item.btc_validated
        }

    return {"error":"TXID not found!"}

def get_chain_notarisation_txid_list(chain, season=None):
    resp = []
    if season:
        data = notarised.objects.filter(chain=chain, season=season)
    else:
        data = notarised.objects.filter(chain=chain)
    for item in data:
        resp.append(item.txid)

    return resp

def get_btc_txid_single(txid=None):
    resp = []
    filter_kwargs = {}
    data = nn_btc_tx.objects.filter(txid=txid)
    for item in data:
        row = {
            "txid":item.txid,
            "block_hash":item.block_hash,
            "block_height":item.block_height,
            "block_time":item.block_time,
            "block_datetime":item.block_datetime,
            "address":item.address,
            "notary":item.notary,
            "season":item.season,
            "category":item.category,
            "input_index":item.input_index,
            "input_sats":item.input_sats,
            "output_index":item.output_index,
            "output_sats":item.output_sats,
            "num_inputs":item.num_inputs,
            "num_outputs":item.num_outputs,
            "fees":item.fees
        }
        resp.append(row)
    return wrap_api(resp)

def get_btc_txid_list(notary=None, season=None):
    resp = []
    if notary and season:
        data = nn_btc_tx.objects.filter(notary=notary, season=season)
    elif notary:
        data = nn_btc_tx.objects.filter(notary=notary)
    elif season:
        data = nn_btc_tx.objects.filter(season=season)
    else:
        data = nn_btc_tx.objects.all()
    for item in data:
        resp.append(item.txid)
    resp = list(set(resp))
    return wrap_api(resp)

def get_ltc_txid_list(notary=None, season=None):
    resp = []
    if notary and season:
        data = nn_ltc_tx.objects.filter(notary=notary, season=season)
    elif notary:
        data = nn_ltc_tx.objects.filter(notary=notary)
    elif season:
        data = nn_ltc_tx.objects.filter(season=season)
    else:
        data = nn_ltc_tx.objects.all()
    for item in data:
        resp.append(item.txid)
    resp = list(set(resp))
    return wrap_api(resp)

def get_btc_txid_notary(notary=None, category=None):
    resp = {}
    txid_list = []
    txid_season_list = {}
    if category and notary:
        data = nn_btc_tx.objects.filter(notary=notary, category=category).values()
    elif category:
        data = nn_btc_tx.objects.filter(category=category).values()
    elif notary:
        data = nn_btc_tx.objects.filter(notary=notary).values()
    else:
        data = []
    for item in data:

        if item['season'] not in resp:
            resp.update({item['season']:{}})
            txid_season_list.update({item['season']:[]})

        if item['category'] not in resp[item['season']]:
            resp[item['season']].update({item['category']:{}})

        if item['txid'] not in resp[item['season']][item['category']]:
            resp[item['season']][item['category']].update({item['txid']:[item]})
            
        else:
            resp[item['season']][item['category']][item['txid']].append(item)

        txid_list.append(item['txid'])
        txid_season_list[item['season']].append(item['txid'])

    api_resp = {
        "count":len(list(set(txid_list))),
        "results":{}
    }
    for season in resp:
        if season not in api_resp["results"]:
            api_resp["results"].update({season:{"count":len(list(set(txid_season_list[season])))}})
        for category in resp[season]:
            api_resp["results"][season].update({
                category:{
                    "count":len(resp[season][category]),
                    "txids":resp[season][category]
                }
            })
    return api_resp

def get_btc_txid_address(address, category=None):
    resp = {}
    txid_list = []
    txid_season_list = {}
    if category:
        data = nn_btc_tx.objects.filter(address=address, category=category).values()
    else:
        data = nn_btc_tx.objects.filter(address=address).values()
    for item in data:
        if item['season'] not in resp:
            resp.update({item['season']:{}})
            txid_season_list.update({item['season']:[]})
        if item['category'] not in resp[item['season']]:
            resp[item['season']].update({item['category']:{}})
        if item['txid'] not in resp[item['season']][item['category']]:
            resp[item['season']][item['category']].update({item['txid']:[item]})
        else:
            resp[item['season']][item['category']][item['txid']].append(item)
        txid_list.append(item['txid'])
        txid_season_list[item['season']].append(item['txid'])

    api_resp = {
        "count":len(list(set(txid_list))),
        "results":{}
    }
    for season in resp:
        if season not in api_resp["results"]:
            api_resp["results"].update({season:{"count":len(list(set(txid_season_list[season])))}})
        for category in resp[season]:
            api_resp["results"][season].update({
                category:{
                    "count":len(resp[season][category]),
                    "txids":resp[season][category]
                }
            })
    return api_resp


def get_ltc_txid_single(txid=None):
    resp = []
    filter_kwargs = {}
    data = nn_ltc_tx.objects.filter(txid=txid)
    for item in data:
        row = {
            "txid":item.txid,
            "block_hash":item.block_hash,
            "block_height":item.block_height,
            "block_time":item.block_time,
            "block_datetime":item.block_datetime,
            "address":item.address,
            "notary":item.notary,
            "season":item.season,
            "category":item.category,
            "input_index":item.input_index,
            "input_sats":item.input_sats,
            "output_index":item.output_index,
            "output_sats":item.output_sats,
            "num_inputs":item.num_inputs,
            "num_outputs":item.num_outputs,
            "fees":item.fees
        }
        resp.append(row)
    return wrap_api(resp)

def get_ltc_txid_notary(notary=None, category=None):
    resp = {}
    txid_list = []
    txid_season_list = {}
    if category and notary:
        data = nn_ltc_tx.objects.filter(notary=notary, category=category).values()
    elif category:
        data = nn_ltc_tx.objects.filter(category=category).values()
    elif notary:
        data = nn_ltc_tx.objects.filter(notary=notary).values()
    else:
        data = []
    for item in data:

        if item['season'] not in resp:
            resp.update({item['season']:{}})
            txid_season_list.update({item['season']:[]})

        if item['category'] not in resp[item['season']]:
            resp[item['season']].update({item['category']:{}})

        if item['txid'] not in resp[item['season']][item['category']]:
            resp[item['season']][item['category']].update({item['txid']:[item]})
            
        else:
            resp[item['season']][item['category']][item['txid']].append(item)

        txid_list.append(item['txid'])
        txid_season_list[item['season']].append(item['txid'])

    api_resp = {
        "count":len(list(set(txid_list))),
        "results":{}
    }
    for season in resp:
        if season not in api_resp["results"]:
            api_resp["results"].update({season:{"count":len(list(set(txid_season_list[season])))}})
        for category in resp[season]:
            api_resp["results"][season].update({
                category:{
                    "count":len(resp[season][category]),
                    "txids":resp[season][category]
                }
            })
    return api_resp


def get_active_dpow_coins():
    return coins.objects.filter(dpow_active=1).values('chain', 'dpow')



def get_dpow_coins_list():
    dpow_chains = get_active_dpow_coins()
    chains_list = []
    for item in dpow_chains:
        if item['chain'] not in chains_list:
            chains_list.append(item['chain'])
    chains_list.sort()
    return chains_list


def get_notary_list(season):
    notaries = nn_social.objects.filter(season=season).values('notary')
    notary_list = []
    for item in notaries:
        if item['notary'] not in notary_list:
            notary_list.append(item['notary'])
    notary_list.sort()
    return notary_list

def get_server_chains_lists(coins_data):

    main_chains = []
    third_chains = []
    for item in coins_data:

        if item['dpow']['server'].lower() == "dpow-mainnet":
            main_chains.append(item['chain'])

        if item['dpow']['server'].lower() == "dpow-3p":
            third_chains.append(item['chain'])

    third_chains.append("KMD_3P")
    main_chains.sort()
    third_chains.sort()

    return main_chains, third_chains

# returns region > notary > chain > season ntx count
def get_coin_notariser_ranks(season):
    # season ntx stats
    ntx_season = notarised_count_season.objects \
                                    .filter(season=season) \
                                    .values()
    if season == "Season_5_Testnet":
        region_notary_ranks = {
            "TESTNET":{}
        }
        notary_list = get_notary_list(season)
        dpow_coins = ["RICK", "MORTY"]

        for notary in notary_list:
            region_notary_ranks["TESTNET"].update({notary:{}})

        for item in ntx_season:
            notary = item['notary']

            if notary in notary_list:
                for coin in item['chain_ntx_counts']:
                    if coin in dpow_coins:
                        region_notary_ranks[region][notary].update({
                            coin:item['chain_ntx_counts'][coin]
                        })
    else:
        region_notary_ranks = {
            "AR":{},
            "EU":{},
            "NA":{},
            "SH":{},
            "DEV":{}
        }
        notary_list = get_notary_list(season)
        dpow_coins = get_dpow_coins_list()
        for notary in notary_list:
            region = get_notary_region(notary)
            if region in ["AR","EU","NA","SH", "DEV"]:
                region_notary_ranks[region].update({notary:{}})
        for item in ntx_season:
            notary = item['notary']
            if notary in notary_list:
                for coin in item['chain_ntx_counts']:
                    if coin in dpow_coins:
                        region = get_notary_region(notary)
                        if region in ["AR","EU","NA","SH", "DEV"]:
                            region_notary_ranks[region][notary].update({
                                coin:item['chain_ntx_counts'][coin]
                            })
    return region_notary_ranks

def get_notarisation_scores(season, coin_notariser_ranks):
    notarisation_scores = {}
    # set coins lists
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    main_chains = get_mainnet_chains(coins_data)
    third_chains = get_third_party_chains(coins_data)

    # init scores dict
    for region in coin_notariser_ranks:
        notarisation_scores.update({region:{}})
        for notary in coin_notariser_ranks[region]:
            notarisation_scores[region].update({
                notary:{
                    "btc":0,
                    "main":0,
                    "third_party":0,
                    "mining":0
                }
            })
    # populate mining data
    mined_season = mined.objects.filter(block_time__gte=SEASONS_INFO[season]['start_time'],
                                            block_time__lte=str(int(time.time()))).values('name') \
                                           .annotate(season_blocks_mined=Count('value'))
    for item in mined_season:
        notary = item["name"]
        region = get_notary_region(notary)
        if region in ["AR","EU","NA","SH", "DEV"]:
            blocks_mined = item["season_blocks_mined"]
            if notary in notarisation_scores[region]:
                notarisation_scores[region][notary].update({
                    "mining": blocks_mined
                })

    # update chain / server counts
    for region in notarisation_scores:
        for notary in notarisation_scores[region]:
            for chain in coin_notariser_ranks[region][notary]:
                if chain == "BTC":
                    val = notarisation_scores[region][notary]["btc"] \
                        +coin_notariser_ranks[region][notary][chain]
                    notarisation_scores[region][notary].update({
                        "btc":val
                    })
                elif chain in main_chains:
                    val = notarisation_scores[region][notary]["main"] \
                        +coin_notariser_ranks[region][notary][chain]
                    notarisation_scores[region][notary].update({
                        "main":val
                    })
                elif chain in third_chains:
                    val = notarisation_scores[region][notary]["third_party"] \
                        +coin_notariser_ranks[region][notary][chain]
                    notarisation_scores[region][notary].update({
                        "third_party":val
                    })

    # calc scores
    for region in notarisation_scores:
        for notary in notarisation_scores[region]:
            score = get_ntx_score(
                notarisation_scores[region][notary]["btc"],
                notarisation_scores[region][notary]["main"],
                notarisation_scores[region][notary]["third_party"]
            )
            notarisation_scores[region][notary].update({
                "score": score
            })
        # determine ranks
        for notary in notarisation_scores[region]:
            rank = 1
            for other_notary in notarisation_scores[region]:
                other_score = notarisation_scores[region][other_notary]["score"]
                score = notarisation_scores[region][notary]["score"]
                if other_score > score:
                    rank += 1
            notarisation_scores[region][notary].update({
                "rank": rank
            })


    return notarisation_scores


def get_region_score_stats(notarisation_scores):
    region_score_stats = {}
    for region in notarisation_scores:
        region_total = 0
        notary_count = 0
        for notary in notarisation_scores[region]:
            notary_count += 1
            region_total += notarisation_scores[region][notary]["score"]
        region_average = region_total/notary_count
        region_score_stats.update({
            region:{
                "notary_count": notary_count,
                "total_score": region_total,
                "average_score": region_average
            }
        })
    return region_score_stats

def get_top_region_notarisers(region_notary_ranks):
    top_region_notarisers = {
        "AR":{
        },
        "EU":{
        },
        "NA":{
        },
        "SH":{
        },
        "DEV":{
        }
    }
    top_ntx_count = {}
    for region in region_notary_ranks:
        if region not in top_ntx_count:
            top_ntx_count.update({region:{}})
        for notary in region_notary_ranks[region]:
            for chain in region_notary_ranks[region][notary]:
                if chain not in top_ntx_count:
                    top_ntx_count[region].update({chain:0})

                if chain not in top_region_notarisers[region]:
                    top_region_notarisers[region].update({chain:{}})

                ntx_count = region_notary_ranks[region][notary][chain]
                if ntx_count > top_ntx_count[region][chain]:
                    top_notary = notary
                    top_ntx_count[region].update({chain:ntx_count})
                    top_region_notarisers[region][chain].update({
                        "top_notary": top_notary,
                        "top_ntx_count": top_ntx_count[region][chain]

                    })
    return top_region_notarisers

def get_top_coin_notarisers(top_region_notarisers, chain):
    top_coin_notarisers = {}
    for region in top_region_notarisers:
        if chain in top_region_notarisers[region]:
            top_coin_notarisers.update({
                region:{
                    "top_notary": top_region_notarisers[region][chain]["top_notary"],
                    "top_ntx_count": top_region_notarisers[region][chain]["top_ntx_count"]
                }
            })
    return top_coin_notarisers


def get_btc_ntx_lag(request):
    data = notarised.objects.filter(chain="BTC").values()
    block_time_list = []
    for item in data:
        block_time_list.append(item["block_time"])
    block_time_list = list(set(block_time_list))
    block_time_list.sort()

    max_lags = []
    max_lag_vals = []
    while len(max_lags) < 25:
        max_blocktime_lag = 0
        for block_time in block_time_list:
            try:
                blocktime_lag = block_time - last_blocktime

                if blocktime_lag > max_blocktime_lag and blocktime_lag not in max_lag_vals:
                    max_blocktime_lag = blocktime_lag
                    max_lag_blocktime = block_time
            except:
                pass
            last_blocktime = block_time

        lagged_blocks = []
        for item in data:
            if item["block_time"] == max_lag_blocktime:
                lagged_blocks.append(item)

        max_lags.append({
            "max_blocktime_lag_sec":max_blocktime_lag,
            "max_blocktime_lag":day_hr_min_sec(max_blocktime_lag),
            "max_lag_blocktime":max_lag_blocktime,
            "max_lag_block_datetime":dt.fromtimestamp(max_lag_blocktime),
            "num_lagged_blocks":len(lagged_blocks),
            "lagged_blocks":lagged_blocks
        })
        max_lag_vals.append(max_blocktime_lag)
    return {"max_lags":max_lags}


def get_chain_sync_data(request):
    season = get_season()
    notaries_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    context = {}
    r = requests.get('http://138.201.207.24/show_sync_node_data')
    try:
        chain_sync_data = r.json()
        sync_data_keys = list(chain_sync_data.keys())
        chain_count = 0
        sync_count = 0
        for chain in sync_data_keys:
            if chain == 'last_updated':
                last_data_update = day_hr_min_sec(
                    int(time.time()) - int(chain_sync_data['last_updated'])
                )
                chain_sync_data.update({
                    "last_data_update": last_data_update
                })
            elif chain.find('last') == -1:
                chain_count += 1
                if "last_sync_blockhash" in chain_sync_data[chain]:
                    if chain_sync_data[chain]["last_sync_blockhash"] == chain_sync_data[chain]["last_sync_dexhash"]:
                        sync_count += 1
                if 'last_sync_timestamp' in chain_sync_data[chain] :
                    last_sync_update = day_hr_min_sec(
                        int(time.time()) - int(chain_sync_data[chain]['last_sync_timestamp'])
                    )
                else:
                    last_sync_update = "-"
                chain_sync_data[chain].update({
                    "last_sync_update": last_sync_update
                })
        sync_pct = round(sync_count/chain_count*100,3)
        context.update({
            "chain_sync_data":chain_sync_data,
            "sync_count":sync_count,
            "sync_pct":sync_pct,
            "chain_count":chain_count
        })
    except Exception as e:
        logger.info(e)
        messages.error(request, 'Sync Node API not Responding!')
    return context

## TODO: MOVE TO LIB_GRAPH

def get_daily_ntx_graph_data(request):
    ntx_dict = {}
    bg_color = []
    border_color = []
    third_chains = []
    main_chains = []
    notary_list = []                                                                         
    chain_list = []
    filter_kwargs = {}

    if 'notarised_date' in request.GET:
        filter_kwargs.update({'notarised_date':request.GET['notarised_date']})
    else:
        today = datetime.date.today()
        filter_kwargs.update({'notarised_date':today})
    if 'notary' in request.GET:
        filter_kwargs.update({'notary':request.GET['notary']})
    elif 'chain' not in request.GET:
        filter_kwargs.update({'notary':'alien_AR'})

    data = notarised_count_daily.objects.filter(**filter_kwargs) \
                .values('notary', 'notarised_date','chain_ntx_counts')

    for item in data:
        if item['notary'] not in notary_list:
            notary_list.append(item['notary'])
        chain_list += list(item['chain_ntx_counts'].keys())
        ntx_dict.update({item['notary']:item['chain_ntx_counts']})

    if 'chain' in request.GET:
        chain_list = [request.GET['chain']]
    else:
        chain_list = list(set(chain_list))
        chain_list.sort()

    notary_list.sort()
    notary_list = region_sort(notary_list)
    coins_data = coins.objects.filter(dpow_active=1).values('chain','dpow')
    for item in coins_data:
        if item['dpow']['server'] == "dPoW-mainnet":
            main_chains.append(item['chain'])
        if item['dpow']['server'] == "dPoW-3P":
            third_chains.append(item['chain'])

    if len(chain_list) == 1:
        chain = chain_list[0]
        labels = notary_list
        chartLabel = chain+ " Notarisations"
        for notary in notary_list:
            if notary.endswith("_AR"):
                bg_color.append(RED)
            elif notary.endswith("_EU"):
                bg_color.append(LT_GREEN)
            elif notary.endswith("_NA"):
                bg_color.append(LT_PURPLE)
            elif notary.endswith("_SH"):
                bg_color.append(LT_BLUE)
            else:
                bg_color.append(LT_ORANGE)
            border_color.append(BLACK)
    else:
        notary = notary_list[0]
        labels = chain_list
        chartLabel = notary+ " Notarisations"
        for chain in chain_list:
            if chain in third_chains:
                bg_color.append(LT_BLUE)
            elif chain in main_chains:
                bg_color.append(LT_GREEN)
            else:
                bg_color.append(LT_PURPLE)
            border_color.append(BLACK)

    chartdata = []
    for notary in notary_list:
        for chain in chain_list:
            if chain in ntx_dict[notary]:
                chartdata.append(ntx_dict[notary][chain])
            else:
                chartdata.append(0)
    

    data = { 
        "labels":labels, 
        "chartLabel":chartLabel, 
        "chartdata":chartdata, 
        "bg_color":bg_color, 
        "border_color":border_color, 
    }
    return data

def get_balances_graph_data(request, filter_kwargs):

    if 'chain' in request.GET:
        filter_kwargs.update({'chain':request.GET['chain']})
    elif 'notary' in request.GET:
        filter_kwargs.update({'notary':request.GET['notary']})
    else:
        filter_kwargs.update({'chain':'BTC'})

    data = balances.objects.filter(**filter_kwargs).values('notary', 'chain', 'balance')
    notary_list = []                                                                          
    chain_list = []
    balances_dict = {}
    for item in data:
        if item['notary'] not in notary_list:
            notary_list.append(item['notary'])
        if item['chain'] not in chain_list:
            chain_list.append(item['chain'])
        if item['notary'] not in balances_dict:
            balances_dict.update({item['notary']:{}})
        if item['chain'] not in balances_dict[item['notary']]:
            balances_dict[item['notary']].update({item['chain']:item['balance']})
        else:
            bal = balances_dict[item['notary']][item['chain']] + item['balance']
            balances_dict[item['notary']].update({item['chain']:bal})

    chain_list.sort()
    notary_list.sort()
    notary_list = region_sort(notary_list)

    bg_color = []
    border_color = []

    third_chains = []
    main_chains = []
    coins_data = coins.objects.filter(dpow_active=1).values('chain','dpow')
    for item in coins_data:
        if item['dpow']['server'] == "dPoW-mainnet":
            main_chains.append(item['chain'])
        if item['dpow']['server'] == "dPoW-3P":
            third_chains.append(item['chain'])

    if len(chain_list) == 1:
        chain = chain_list[0]
        labels = notary_list
        chartLabel = chain+ " Notary Balances"
        for notary in notary_list:
            if notary.endswith("_AR"):
                bg_color.append(RED)
            elif notary.endswith("_EU"):
                bg_color.append(LT_GREEN)
            elif notary.endswith("_NA"):
                bg_color.append(LT_PURPLE)
            elif notary.endswith("_SH"):
                bg_color.append(LT_BLUE)
            else:
                bg_color.append(LT_ORANGE)
            border_color.append(BLACK)
    else:
        notary = notary_list[0]
        labels = chain_list
        chartLabel = notary+ " Notary Balances"
        for chain in chain_list:
            if chain in third_chains:
                bg_color.append(LT_PURPLE)
            elif chain in main_chains:
                bg_color.append(LT_GREEN)
            else:
                bg_color.append(LT_ORANGE)
            border_color.append(BLACK)

    chartdata = []
    for notary in notary_list:
        for chain in chain_list:
            chartdata.append(balances_dict[notary][chain])
    
    data = { 
        "labels":labels, 
        "chartLabel":chartLabel, 
        "chartdata":chartdata, 
        "bg_color":bg_color, 
        "border_color":border_color, 
    } 
    return data

def get_notary_balances_data(coins_data, balances_data):
 
    main_chains, third_chains = get_server_chains_lists(coins_data)

    balances_graph_dict = {}
    notary_balances_list = []
    for item in balances_data:

        if item['node'] == 'third party' and item['chain'] == "KMD":
            chain = "KMD_3P"

        else: 
            chain = item['chain']

        if chain in main_chains and item["node"] == 'main':
            notary_balances_list.append(item)
            balances_graph_dict.update({chain:float(item['balance'])})

        elif item["node"] == 'third party' and chain in third_chains or chain == "KMD_3P":
            balances_graph_dict.update({chain:float(item['balance'])})
            notary_balances_list.append(item)


    labels = list(main_chains+third_chains)

    bg_color = []
    border_color = []
    for label in labels:
        border_color.append(BLACK)

        if label in ['KMD', 'KMD_3P', 'BTC']:
            bg_color.append(LT_ORANGE)

        elif label in third_chains:
            bg_color.append(LT_PURPLE)

        elif label in main_chains:
            bg_color.append(LT_GREEN)

    chartdata = []
    for label in labels:
        if label in balances_graph_dict:
            chartdata.append(balances_graph_dict[label])

    notary_balances_graph = { 
        "labels":labels, 
        "chartLabel":f"BALANCES",
        "chartdata":chartdata, 
        "bg_color":bg_color, 
        "border_color":border_color, 
    } 

    return notary_balances_list, notary_balances_graph


def get_epoch_scoring_table(request):
    resp = []
    
    if "season" in request.GET:
        season=request.GET["season"]
        data = scoring_epochs.objects.filter(season=season)
    else:
        data = scoring_epochs.objects.all()

    data = data.order_by('season', 'server').values()
    for item in data:

        resp.append({
                "season":item['season'],
                "server":item['server'],
                "epoch":item['epoch'].split("_")[1],
                "epoch_start":dt.fromtimestamp(item['epoch_start']),
                "epoch_end":dt.fromtimestamp(item['epoch_end']),
                "duration":item['epoch_end']-item['epoch_start'],
                "start_event":item['start_event'],
                "end_event":item['end_event'],
                "epoch_chains":", ".join(item['epoch_chains']),
                "num_epoch_chains":len(item['epoch_chains']),
                "score_per_ntx":item['score_per_ntx']
        })
    return resp


def get_mined_count_season_table(request):
    resp = []
    data = mined_count_season.objects.all()

    if "season" in request.GET:
        season=request.GET["season"]

    elif len(data) == len(mined_count_season.objects.all()):
        season = get_season()
        
    data = mined_count_season.objects.filter(season=season).order_by('season', 'notary').values()

    # name num sum max last
    for item in data:
        blocks_mined = item['blocks_mined']
        if blocks_mined > 10:
            notary = item['notary']
            sum_value_mined = item['sum_value_mined']
            max_value_mined = item['max_value_mined']
            last_mined_block = item['last_mined_block']
            last_mined_blocktime = item['last_mined_blocktime']
            time_stamp = item['time_stamp']
            season = item['season']

            resp.append({
                    "notary":notary,
                    "blocks_mined":blocks_mined,
                    "sum_value_mined":sum_value_mined,
                    "max_value_mined":max_value_mined,
                    "last_mined_block":last_mined_block,
                    "last_mined_blocktime":last_mined_blocktime
            })

    return resp

def get_epochs_dict(season=None):
    if not season:
        season = get_season()

    epoch_data = scoring_epochs.objects.filter(season=season).values()
    epochs = {}
    for item in epoch_data:

        server = item['server']
        epoch_id = item['epoch']
        start = item['epoch_start']
        end = item['epoch_end']
        start_event = item['start_event']
        end_event = item['end_event']
        epoch_chains = item['epoch_chains']
        score_per_ntx = item['score_per_ntx']

        if season not in epochs:
            epochs.update({season:{}})

        if server not in epochs[season]:
            epochs[season].update({server:{}})

        if epoch_id not in epochs[season][server]:
            epochs[season][server].update({epoch_id:{
                "start":start,
                "end":end,
                "start_event":start_event,
                "end_event":end_event,
                "score_per_ntx":score_per_ntx
            }})

    return epochs

def get_epoch_id(season, server, block_time):
    epochs = get_epochs_dict()
    for epoch_id in epochs[season][server]:
        if block_time > epochs[season][server][epoch_id]["start"]:
            if block_time < epochs[season][server][epoch_id]["end"]:
                return epoch_id


def get_notarised_season_score(season=None, chain=None):
    if not season:
        season = get_season()
    if not chain:
        chain = "BTC"

    notarised_data = notarised.objects.filter(season=season, chain=chain).values()

    resp = {}
    for item in notarised_data:

        txid = item['txid']
        chain = item['chain']
        block_hash = item['block_hash']
        block_time = item['block_time']
        block_datetime = item['block_datetime']
        block_height = item['block_height']
        notaries = item['notaries']
        notary_addresses = item['notary_addresses']
        ac_ntx_blockhash = item['ac_ntx_blockhash']
        ac_ntx_height = item['ac_ntx_height']
        opret = item['opret']
        season = item['season']
        server = item['server']
        scored = item['scored']
        score_value = item['score_value']
        btc_validated = item['btc_validated']

        if chain == "BTC":
            server = "BTC"
            epoch_id = "epoch_BTC"

        else:
            epoch_id = get_epoch_id(season, server, block_time)

        if not epoch_id:
            logger.info(f"no epoch for txid {txid}")

        else:
            for notary in notaries:
                if notary not in resp:
                    resp.update({
                        notary:{
                            "servers": {
                                server:{
                                    "epochs":{
                                        epoch_id:{
                                            "chains": {
                                                chain:{
                                                    "chain_ntx":0,
                                                    "chain_score":0
                                                },
                                            },
                                            "epoch_ntx":0,
                                            "epoch_score":0
                                        }
                                    },
                                    "server_ntx":0,
                                    "server_score":0
                                }
                            },
                            "season_score":0
                        }
                    })

                if server not in resp[notary]["servers"]:
                    resp[notary]["servers"].update({
                        server:{
                            "epochs":{
                                epoch_id:{
                                    "chains": {
                                        chain:{
                                            "chain_ntx":0,
                                            "chain_score":0
                                        },
                                    },
                                    "epoch_ntx":0,
                                    "epoch_score":0
                                }
                            },
                            "server_ntx":0,
                            "server_score":0
                        }
                    })

                if epoch_id not in resp[notary]["servers"][server]["epochs"]:
                    resp[notary]["servers"][server]["epochs"].update({
                        epoch_id:{
                            "chains": {
                                chain:{
                                    "chain_ntx":0,
                                    "chain_score":0
                                },
                            },
                            "epoch_ntx":0,
                            "epoch_score":0
                        }
                    })

                if chain not in resp[notary]["servers"][server]["epochs"][epoch_id]["chains"]:
                    resp[notary]["servers"][server]["epochs"][epoch_id]["chains"].update({
                        chain:{
                            "chain_ntx":0,
                            "chain_score":0
                        },
                    })

                resp[notary]["season_score"] += score_value

                resp[notary]["servers"][server]["server_ntx"] += 1
                resp[notary]["servers"][server]["server_score"] += score_value

                resp[notary]["servers"][server]["epochs"][epoch_id]["epoch_ntx"] += 1
                resp[notary]["servers"][server]["epochs"][epoch_id]["epoch_score"] += score_value

                resp[notary]["servers"][server]["epochs"][epoch_id]["chains"][chain]["chain_ntx"] += 1
                resp[notary]["servers"][server]["epochs"][epoch_id]["chains"][chain]["chain_score"] += score_value
           

                

    return resp