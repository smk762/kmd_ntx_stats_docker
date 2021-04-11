#!/usr/bin/env python3
import time
import logging
import datetime

from .models import *
from .serializers import *
from .lib_query import *
from .lib_api import paginate_wrap, wrap_api

logger = logging.getLogger("mylogger")


def apply_filters_api(request, serializer, queryset, table=None, filter_kwargs=None):
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


def get_addresses_data_api(request):
    print(request)
    resp = []
    data = addresses.objects.all()
    data = apply_filters_api(request, AddressesSerializer, data) \
            .order_by('season', 'notary', 'chain') \
            .values()

    for item in data:
        resp.append(item)

    return resp


def get_balances_data_api(request):
    resp = {}
    data = balances.objects.all()
    data = apply_filters_api(request, BalancesSerializer, data) \
            .order_by('-season','notary', 'chain', 'balance') \
            .values()

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

    return resp


def get_coins_data_api(request):
    resp = {}
    data = coins.objects.all()
    data = apply_filters_api(request, CoinsSerializer, data) \
            .order_by('chain') \
            .values()

    for item in data:
        resp.update({
            item["chain"]:{
                "coins_info":item["coins_info"],
                "dpow":item["dpow"],
                "dpow_tenure":item["dpow_tenure"],
                "explorers":item["explorers"],
                "electrums":item["electrums"],
                "electrums_ssl":item["electrums_ssl"],
                "mm2_compatible":item["mm2_compatible"],
                "dpow_active":item["dpow_active"]
            },
        })

    return resp


def get_electrums_data_api(chain=None):
    resp = {}
    coins_data = coins.objects.all().order_by('chain')

    if chain:
        coins_data = coins_data.filter(chain=chain)

    coins_data = coins_data.values('chain','electrums')

    for item in coins_data:
        electrums = item['electrums']
        if len(electrums) > 0:
            chain = item['chain']
            resp.update({chain:electrums})
    return resp


def get_electrums_ssl_data_api(chain=None):
    resp = {}
    coins_data = coins.objects.all().order_by('chain')
    if chain:
        coins_data = coins_data.filter(chain=chain)

    coins_data = coins_data.values('chain','electrums_ssl')
    
    for item in coins_data:
        electrums_ssl = item['electrums_ssl']
        if len(electrums_ssl) > 0:
            chain = item['chain']
            resp.update({chain:electrums_ssl})
    return resp


def get_explorers_data_api():
    resp = {}
    coins_data = coins.objects.all().order_by('chain').values('chain','explorers')
    for item in coins_data:
        explorers = item['explorers']
        if len(explorers) > 0:
            chain = item['chain']
            resp.update({chain:explorers})
    return resp


def get_launch_params_data_api(chain=None):
    coins_data = coins.objects.all()
    if chain:
        coins_data = coins_data.filter(chain=chain)

    coins_data = coins_data.order_by('chain').values('chain', 'dpow')
    
    resp = {}
    for item in coins_data:
        dpow_info = item['dpow']
        chain = item['chain']
        if len(dpow_info) > 0:
            server = dpow_info['server']
            if "launch_params" in dpow_info:
                launch_params = dpow_info["launch_params"]
            else:
                launch_params = ''
            if server not in resp:
                resp.update({server:{}})
            resp[server].update({chain:launch_params})
    return resp

def get_mined_count_season_data_api(request):
    resp = {}
    data = mined_count_season.objects.all()
    data = apply_filters_api(request, MinedCountSeasonSerializer, data)
    if len(data) == len(mined_count_season.objects.all()):
        season = get_season()
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

    return resp


def get_mined_count_daily_data_api(request):
    resp = {}
    data = mined_count_daily.objects.all()
    data = apply_filters_api(request, MinedCountDailySerializer, data, 'daily_mined_count')
    # default filter if none set.
    if len(data) == len(mined_count_daily.objects.all()) or len(data) == 0:
        today = datetime.date.today()
        data = mined_count_daily.objects.filter(mined_date=str(today))
        mined_date = today
    data = data.order_by('mined_date', 'notary').values()

    for item in data:
        blocks_mined = item['blocks_mined']
        notary = item['notary']
        sum_value_mined = item['sum_value_mined']
        time_stamp = item['time_stamp']
        mined_date = item['mined_date']

        if str(mined_date) not in resp:
            resp.update({str(mined_date):{}})

        resp[str(mined_date)].update({
            notary:{
                "blocks_mined":blocks_mined,
                "sum_value_mined":sum_value_mined,
                "time_stamp":time_stamp
            }
        })
    delta = datetime.timedelta(days=1)
    yesterday = mined_date-delta
    tomorrow = mined_date+delta
    url = request.build_absolute_uri('/api/mined_stats/daily/')
    return paginate_wrap(resp, url, "mined_date",
                         str(yesterday), str(tomorrow))


def get_notarised_data_api(request):

    resp = {}

    data = notarised.objects.all()

    if "notary" in request.GET:
        data = data.filter(notaries__contains=[request.GET["notary"]])

    if "address" in request.GET:
        data = data.filter(notary_addresses__contains=[request.GET["address"]])

    if "season" in request.GET:
        data = data.filter(season=request.GET["season"])

    else:
        data = data.filter(season="Season_4")

    if "chain" in request.GET:
        data = data.filter(chain=request.GET["chain"])

    else:
        data = data.filter(chain="KMD")

    data = apply_filters_api(request, NotarisedSerializer, data) \
            .order_by('-season', 'chain', "-block_time") \
            .values()

    for item in data:
        resp.update({item["txid"]:{}})
        for x in item.keys():
            if x != "txid":
                resp[item["txid"]].update({x:item[x]})

    return resp


def get_notarised_chain_season_data_api(request):
    resp = {}
    data = notarised_chain_season.objects.all()
    data = apply_filters_api(request, NotarisedChainSeasonSerializer, data) \
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


    return resp


def get_notarised_count_season_data_api(request):
    resp = {}
    data = notarised_count_season.objects.all()
    data = apply_filters_api(request, NotarisedCountSeasonSerializer, data)
    # default filter if none set.
    if len(data) == notarised_count_season.objects.count() or len(data) == 0:
        season = get_season()
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
            if chain not in resp[season][notary]["chains"]:
                resp[season][notary]["chains"].update({chain:{}})
            resp[season][notary]["chains"][chain].update({
                "percentage":chain_ntx_pct[chain]
            }),


    return resp


def get_notarised_chain_daily_data_api(request):
    resp = {}
    data = notarised_chain_daily.objects.all()
    data = apply_filters_api(request, NotarisedChainDailySerializer, data, 'daily_notarised_chain')
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
    url = request.build_absolute_uri('/api/chain_stats/daily/')
    return paginate_wrap(resp, url, "notarised_date",
                         str(yesterday), str(tomorrow))


def get_notarised_count_date_data_api(request):
    resp = {}
    data = get_notarised_count_daily_data()
    data = apply_filters_api(request, NotarisedCountDailySerializer, data, 'daily_notarised_count')
    # default filter if none set.
    if len(data) == len(get_notarised_count_daily_data()):
        today = datetime.date.today()
        data = get_notarised_count_daily_data().filter(notarised_date=today)
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

    url = request.build_absolute_uri('/api/notary_stats/daily/')
    return paginate_wrap(resp, url, "notarised_date",
                         str(yesterday), str(tomorrow))


def get_notarised_tenure_data_api(request):
    resp = {}
    data = notarised_tenure.objects.all()
    data = apply_filters_api(request, ntxTenureSerializer, data)
    data = data.order_by('chain', 'season').values()
    for item in data:

        if item["season"] not in resp: 
            resp.update({item["season"]:{}})

        if item["server"] not in resp[item["season"]]: 
            resp[item["season"]].update({item["server"]:{}})

        if item["chain"] not in resp[item["season"]][item["server"]]:
            resp[item["season"]][item["server"]].update({
                item["chain"]: {
                    "first_ntx_block":item["first_ntx_block"],
                    "last_ntx_block":item["last_ntx_block"], 
                    "first_ntx_block_time":item["first_ntx_block_time"],
                    "last_ntx_block_time":item["last_ntx_block_time"],
                    "official_start_block_time":item["official_start_block_time"],
                    "official_end_block_time":item["official_end_block_time"],
                    "scored_ntx_count":item["scored_ntx_count"],
                    "unscored_ntx_count":item["unscored_ntx_count"]
                }
            })

    return resp


def get_rewards_data_api(request):
    address_data = addresses.objects.filter(chain='KMD')
    if 'season' in request.GET:
        season = request.GET['season']
    else:
        season = get_season()
    address_data = address_data.filter(season__contains=season)
    address_data = address_data.order_by('season','notary')
    address_data = address_data.values('address', 'season')

    address_season = {}
    for item in address_data:
        if item['address'] not in address_season:
            address_season.update({item['address']:season})


    resp = {}
    data = rewards.objects.all()
    data = apply_filters_api(request, RewardsSerializer, data) \
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


    return resp


def get_nn_social_data_api(request):
    if "season" in request.GET and "notary" in request.GET:
        data = nn_social.objects.filter(season=season, notary=notary)
    elif "season" in request.GET:
        data = nn_social.objects.filter(season=season)
    elif "notary" in request.GET:
        data = nn_social.objects.filter(notary=notary) 
    else:
        data = nn_social.objects.all()

    return data.order_by('-season','notary').values()

