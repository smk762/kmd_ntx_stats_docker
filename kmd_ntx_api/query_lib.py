#!/usr/bin/env python3
import logging
import datetime
from datetime import datetime as dt
from .models import *
from .info_lib import *
from .helper_lib import *
from kmd_ntx_api.serializers import *
logger = logging.getLogger("mylogger")

def apply_filters(request, serializer, queryset, table=None, filter_kwargs=None):
    if not filter_kwargs:
        filter_kwargs = {}
    for field in serializer.Meta.fields:
        val = request.query_params.get(field, None)
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
    if table in ['daily_mined_count']:
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

def paginate_wrap(resp, url, field, prev_value, next_value):
    api_resp = {
        "count":len(resp),
        "next":url+"?"+field+"="+next_value,
        "previous":url+"?"+field+"="+prev_value,
        "results":[resp]
    }
    return api_resp

def wrap_api(resp):
    api_resp = {
        "count":len(resp),
        "results":[resp]
    }
    return api_resp

def get_notary_list(season):
    notaries = nn_social.objects.filter(season=season).values('notary')
    notary_list = []
    for item in notaries:
        if item['notary'] not in notary_list:
            notary_list.append(item['notary'])
    notary_list.sort()
    return notary_list

def get_notary_region(notary):
    return notary.split("_")[-1]

 
def get_dpow_coins_list():
    dpow_chains = coins.objects.filter(dpow_active=1).values('chain')
    chains_list = []
    for item in dpow_chains:
        if item['chain'] not in chains_list:
            chains_list.append(item['chain'])
    chains_list.sort()
    return chains_list

def get_coins_data(request):
    resp = {}
    data = coins.objects.all()
    data = apply_filters(request, CoinsSerializer, data) \
            .order_by('chain') \
            .values()
    for item in data:
        resp.update({
            item["chain"]:{
                "coins_info":item["coins_info"],
                "dpow":item["dpow"],
                "explorers":item["explorers"],
                "electrums":item["electrums"],
                "electrums_ssl":item["electrums_ssl"],
                "mm2_compatible":item["mm2_compatible"],
                "dpow_active":item["dpow_active"]
            },
        })
    return wrap_api(resp)

def get_addresses_data(request):
    resp = {}
    data = addresses.objects.all()
    full_count = data.count()
    data = apply_filters(request, AddressesSerializer, data)
    season = get_season(int(time.time()))
    if data.count() == full_count:
        data = addresses.objects.filter(season=season)
    data = data.order_by('notary','season', 'chain').values()
    for item in data:
        if item["notary"] not in resp: 
            resp.update({item["notary"]:{}})
        if item["season"] not in resp[item["notary"]]:
            resp[item["notary"]].update({
                item["season"]: {
                    "notary_id":item["notary_id"],
                    "pubkey":item["pubkey"],
                    "addresses":{}
                }
            })

        if item["chain"] not in resp[item["notary"]][item["season"]]["addresses"]:
            resp[item["notary"]][item["season"]]["addresses"].update({
                item["chain"]: item['address']
            })
    return wrap_api(resp)

def get_balances_data(request):
    resp = {}
    data = balances.objects.all()
    data = apply_filters(request, BalancesSerializer, data)
    season = get_season(int(time.time()))
    if len(data) == len(balances.objects.all()):
        data = balances.objects.filter(season=season) 
    data = data.order_by('-season','notary', 'chain', 'balance').values()
    for item in data:
        
        season = item['season']
        if season not in resp:
            resp.update({season:{}})

        notary = item['notary']
        if notary not in resp[season]:
            resp[season].update({notary:{}})

        chain = item['chain']
        if chain not in resp[season][notary]:
            resp[season][notary].update({chain:{}})

        address = item['address']
        balance = item['balance']
        resp[season][notary][chain].update({address:balance})

    return wrap_api(resp)

def get_mined_count_season_data(request):
    resp = {}
    data = mined_count_season.objects.all()
    data = apply_filters(request, MinedCountSeasonSerializer, data)
    if len(data) == len(mined_count_season.objects.all()):
        season = get_season(int(time.time()))
        data = mined_count_season.objects.filter(season=season)
    data = data.order_by('season', 'notary').values()

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

            if season not in resp:
                resp.update({season:{}})

            resp[season].update({
                notary:{
                    "blocks_mined":blocks_mined,
                    "sum_value_mined":sum_value_mined,
                    "max_value_mined":max_value_mined,
                    "last_mined_block":last_mined_block,
                    "last_mined_blocktime":last_mined_blocktime,
                    "time_stamp":time_stamp
                }
            })

    return wrap_api(resp)

def get_notary_ntx_24hr_summary(ntx_24hr, notary):
    notary_ntx_24hr = {
            "btc_ntx":0,
            "main_ntx":0,
            "third_party_ntx":0,
            "most_ntx":"N/A"
        }
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
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
        if chain == "KMD":
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

# returns region > notary > chain > season ntx count
def get_coin_notariser_ranks(season):
    # season ntx stats
    ntx_season = notarised_count_season.objects \
                                    .filter(season=season) \
                                    .values()
    region_notary_ranks = {
        "AR":{},
        "EU":{},
        "NA":{},
        "SH":{},
        "DEV":{}
    }
    notary_list = get_notary_list(season)
    for notary in notary_list:
        region = get_notary_region(notary)
        if region in ["AR","EU","NA","SH", "DEV"]:
            region_notary_ranks[region].update({notary:{}})
    for item in ntx_season:
        notary = item['notary']
        if notary in notary_list:
            for coin in item['chain_ntx_counts']:
                if coin == "BTC":
                    coin = "KMD"
                region = get_notary_region(notary)
                if region in ["AR","EU","NA","SH", "DEV"]:
                    region_notary_ranks[region][notary].update({
                        coin:item['chain_ntx_counts'][coin]
                    })
    return region_notary_ranks


def get_notarisation_scores(season, coin_notariser_ranks):
    notarisation_scores = {}
    print(coin_notariser_ranks)
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

            coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')

            main_chains = []
            for item in coins_data:
                if item['dpow']['server'] == "dPoW-mainnet":
                    main_chains.append(item['chain'])

            third_chains = []
            for item in coins_data:
                if item['dpow']['server'] == "dPoW-3P":
                    third_chains.append(item['chain'])

            for chain in coin_notariser_ranks[region][notary]:
                if chain in ["KMD", "BTC"]:
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

    for region in notarisation_scores:
        for notary in notarisation_scores[region]:
            print(notary)
            print(notarisation_scores[region][notary])
            score = get_ntx_score(
                notarisation_scores[region][notary]["btc"],
                notarisation_scores[region][notary]["main"],
                notarisation_scores[region][notary]["third_party"]
            )
            print(score)
            notarisation_scores[region][notary].update({
                "score": score
            })
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
    if chain == "BTC":
        chain = "KMD"
    for region in top_region_notarisers:
        if chain in top_region_notarisers[region]:
            top_coin_notarisers.update({
                region:{
                    "top_notary": top_region_notarisers[region][chain]["top_notary"],
                    "top_ntx_count": top_region_notarisers[region][chain]["top_ntx_count"]
                }
            })
    return top_coin_notarisers


def get_mined_count_daily_data(request):
    resp = {}
    data = mined_count_daily.objects.all()
    data = apply_filters(request, MinedCountDailySerializer, data, 'daily_mined_count')
    # default filter if none set.
    if len(data) == len(mined_count_daily.objects.all()) or len(data) == 0:
        today = datetime.date.today()
        data = mined_count_daily.objects.filter(mined_date=str(today))
    data = data.order_by('mined_date', 'notary').values()

    for item in data:
        blocks_mined = item['blocks_mined']
        notary = item['notary']
        sum_value_mined = item['sum_value_mined']
        time_stamp = item['time_stamp']
        mined_date = str(item['mined_date'])

        if mined_date not in resp:
            resp.update({mined_date:{}})

        resp[mined_date].update({
            notary:{
                "blocks_mined":blocks_mined,
                "sum_value_mined":sum_value_mined,
                "time_stamp":time_stamp
            }
        })
    delta = datetime.timedelta(days=1)
    yesterday = item['mined_date']-delta
    tomorrow = item['mined_date']+delta
    url = request.build_absolute_uri('/mined_stats/daily/')
    return paginate_wrap(resp, url, "mined_date",
                         str(yesterday), str(tomorrow))

def get_notarised_chain_season_data(request):
    resp = {}
    data = notarised_chain_season.objects.all()
    data = apply_filters(request, NotarisedChainSeasonSerializer, data) \
            .order_by('-season', 'chain') \
            .values()

    for item in data:
        season = item['season']
        chain = item['chain']
        ntx_lag = item['ntx_lag']
        ntx_count = item['ntx_count']
        block_height = item['block_height']
        kmd_ntx_txid = item['kmd_ntx_txid']
        kmd_ntx_blockhash = item['kmd_ntx_blockhash']
        kmd_ntx_blocktime = item['kmd_ntx_blocktime']
        opret = item['opret']
        ac_ntx_blockhash = item['ac_ntx_blockhash']
        ac_ntx_height = item['ac_ntx_height']
        ac_block_height = item['ac_block_height']

        if season not in resp:
            resp.update({season:{}})

        resp[season].update({
            chain:{
                "ntx_count":ntx_count,
                "kmd_ntx_height":block_height,
                "kmd_ntx_blockhash":kmd_ntx_blockhash,
                "kmd_ntx_txid":kmd_ntx_txid,
                "kmd_ntx_blocktime":kmd_ntx_blocktime,
                "ac_ntx_blockhash":ac_ntx_blockhash,
                "ac_ntx_height":ac_ntx_height,
                "ac_block_height":ac_block_height,
                "opret":opret,
                "ntx_lag":ntx_lag
            }
        })


    return wrap_api(resp)

def get_notarised_count_season_data(request):
    resp = {}
    data = notarised_count_season.objects.all()
    data = apply_filters(request, NotarisedCountSeasonSerializer, data)
    # default filter if none set.
    if len(data) == notarised_count_season.objects.count() or len(data) == 0:
        season = get_season(int(time.time()))
        data = notarised_count_season.objects.filter(season=season)

    data = data.order_by('season', 'notary').values()

    for item in data:
        season = item['season']
        notary = item['notary']
        btc_count = item['btc_count']
        antara_count = item['antara_count']
        third_party_count = item['third_party_count']
        other_count = item['other_count']
        total_ntx_count = item['total_ntx_count']
        chain_ntx_counts = item['chain_ntx_counts']
        chain_ntx_pct = item['chain_ntx_pct']
        time_stamp = item['time_stamp']

        if season not in resp:
            resp.update({season:{}})

        resp[season].update({
            notary:{
                "btc_count":btc_count,
                "antara_count":antara_count,
                "third_party_count":third_party_count,
                "other_count":other_count,
                "total_ntx_count":total_ntx_count,
                "time_stamp":time_stamp,
                "chains":{}
            }
        })
        for chain in chain_ntx_counts:
            resp[season][notary]["chains"].update({
                chain:{
                    "count":chain_ntx_counts[chain]
                }
            })
        for chain in chain_ntx_pct:
            resp[season][notary]["chains"][chain].update({
                "percentage":chain_ntx_pct[chain]
            }),


    return wrap_api(resp)

def get_notarised_chain_daily_data(request):
    resp = {}
    data = notarised_chain_daily.objects.all()
    data = apply_filters(request, NotarisedChainDailySerializer, data, 'daily_notarised_chain')
    # default filter if none set.
    if len(data) == len(notarised_chain_daily.objects.all()):
        today = datetime.date.today()
        data = notarised_chain_daily.objects.filter(notarised_date=str(today))
    data = data.order_by('notarised_date', 'chain').values()
    if len(data) > 0:
        for item in data:
            notarised_date = str(item['notarised_date'])
            chain = item['chain']
            ntx_count = item['ntx_count']

            if notarised_date not in resp:
                resp.update({notarised_date:{}})

            resp[notarised_date].update({
                chain:ntx_count
            })


        delta = datetime.timedelta(days=1)
        yesterday = item['notarised_date']-delta
        tomorrow = item['notarised_date']+delta
    else:
        today = datetime.date.today()
        delta = datetime.timedelta(days=1)
        yesterday = today-delta
        tomorrow = today+delta
    url = request.build_absolute_uri('/chain_stats/daily/')
    return paginate_wrap(resp, url, "notarised_date",
                         str(yesterday), str(tomorrow))

def get_notarised_count_date_data(request):
    resp = {}
    data = notarised_count_daily.objects.all()
    data = apply_filters(request, NotarisedCountDailySerializer, data, 'daily_notarised_count')
    # default filter if none set.
    if len(data) == len(notarised_count_daily.objects.all()):
        today = datetime.date.today()
        data = notarised_count_daily.objects.filter(notarised_date=today)
    data = data.order_by('notarised_date', 'notary').values()
    if len(data) > 0:
        for item in data:
            notarised_date = str(item['notarised_date'])
            notary = item['notary']
            btc_count = item['btc_count']
            antara_count = item['antara_count']
            third_party_count = item['third_party_count']
            other_count = item['other_count']
            total_ntx_count = item['total_ntx_count']
            chain_ntx_counts = item['chain_ntx_counts']
            chain_ntx_pct = item['chain_ntx_pct']
            time_stamp = item['time_stamp']

            if notarised_date not in resp:
                resp.update({notarised_date:{}})

            resp[notarised_date].update({
                notary:{
                    "btc_count":btc_count,
                    "antara_count":antara_count,
                    "third_party_count":third_party_count,
                    "other_count":other_count,
                    "total_ntx_count":total_ntx_count,
                    "time_stamp":time_stamp,
                    "chains":{}
                }
            })
            for chain in chain_ntx_counts:
                resp[notarised_date][notary]["chains"].update({
                    chain:{
                        "count":chain_ntx_counts[chain],
                        "percentage":chain_ntx_pct[chain]
                    }
                })

        delta = datetime.timedelta(days=1)
        yesterday = item['notarised_date']-delta
        tomorrow = item['notarised_date']+delta
    else:
        today = datetime.date.today()
        delta = datetime.timedelta(days=1)
        yesterday = today-delta
        tomorrow = today+delta

    url = request.build_absolute_uri('/notary_stats/daily/')
    return paginate_wrap(resp, url, "notarised_date",
                         str(yesterday), str(tomorrow))

def get_mined_data(request):
    resp = {}
    data = mined.objects.all()
    data = apply_filters(request, MinedSerializer, data)
    if len(data) == len(mined.objects.all()):
        yesterday = int(time.time() -60*60*24)
        data = mined.objects.filter(block_time__gte=yesterday) \
            .order_by('season','name', 'block_height') \
            .values()
    for item in data:
        name = item['name']
        address = item['address']
        #ignore unknown addresses
        if name != address:
            season = item['season']
            block_height = item['block_height']
            if season not in resp:
                resp.update({season:{}})
            if name not in resp[season]:
                resp[season].update({name:{}})
            resp[season][name].update({
                block_height:{
                    "block_time":item['block_time'],
                    "block_datetime":item['block_datetime'],
                    "value":item['value'],
                    "address":address,
                    "txid":item['txid']
                }
            })

    return wrap_api(resp)

def get_notarised_data(request):
    resp = {}
    data = notarised.objects.all()
    data = apply_filters(request, NotarisedSerializer, data)
    if len(data) == len(notarised.objects.all()):
        yesterday = int(time.time()-60*60*24)
        data = notarised.objects.filter(block_time__gte=yesterday) \
            .order_by('season', 'chain', '-block_height') \
            .values()

    for item in data:
        txid = item['txid']
        chain = item['chain']
        block_hash = item['block_hash']
        block_time = item['block_time']
        block_datetime = item['block_datetime']
        block_height = item['block_height']
        ac_ntx_blockhash = item['ac_ntx_blockhash']
        ac_ntx_height = item['ac_ntx_height']
        season = item['season']
        opret = item['opret']

        if season not in resp:
            resp.update({season:{}})

        if chain not in resp[season]:
            resp[season].update({chain:{}})

        resp[season][chain].update({
            block_height:{
                "block_hash":block_hash,
                "block_time":block_time,
                "block_datetime":block_datetime,
                "txid":txid,
                "ac_ntx_blockhash":ac_ntx_blockhash,
                "ac_ntx_height":ac_ntx_height,
                "opret":opret
            }
        })

    return wrap_api(resp)

def get_rewards_data(request):
    address_data = addresses.objects.filter(chain='KMD')
    if 'season' in request.GET:
        season = request.GET['season']
    else:
        season = get_season(int(time.time()))
    address_data = address_data.filter(season__contains=season)
    address_data = address_data.order_by('season','notary')
    address_data = address_data.values('address', 'season')

    address_season = {}
    for item in address_data:
        if item['address'] not in address_season:
            address_season.update({item['address']:season})


    resp = {}
    data = rewards.objects.all()
    data = apply_filters(request, RewardsSerializer, data) \
            .order_by('notary') \
            .values()

    for item in data:
        address = item['address']
        if address in address_season:
            season = address_season[address]
            notary = item['notary']
            utxo_count = item['utxo_count']
            eligible_utxo_count = item['eligible_utxo_count']
            oldest_utxo_block = item['oldest_utxo_block']
            balance = item['balance']
            pending_rewards = item['rewards']
            update_time = item['update_time']

            if season not in resp:
                resp.update({season:{}})
            if notary not in resp[season]:
                resp[season].update({notary:{}})

            resp[season][notary].update({
                address:{
                    "utxo_count":utxo_count,
                    "eligible_utxo_count":eligible_utxo_count,
                    "oldest_utxo_block":oldest_utxo_block,
                    "balance":balance,
                    "rewards":pending_rewards,
                    "update_time":update_time,
                }
            })


    return wrap_api(resp)