#!/usr/bin/env python3
import logging
import datetime
from datetime import datetime as dt
from .models import *
from .lib_const import *
from .lib_info import *
from .lib_helper import *
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

def wrap_api(resp, filters=None):
    api_resp = {
        "count":len(resp),
        "results":[resp]
    }
    if filters:
        api_resp.update({"filters":filters})
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
                "dpow_tenure":item["dpow_tenure"],
                "explorers":item["explorers"],
                "electrums":item["electrums"],
                "electrums_ssl":item["electrums_ssl"],
                "mm2_compatible":item["mm2_compatible"],
                "dpow_active":item["dpow_active"]
            },
        })
    return wrap_api(resp)

def get_addresses_data(request):
    filters = AddressesSerializer.Meta.fields
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
    return wrap_api(resp, filters)

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
                bg_color.append('#DC0333')
            elif notary.endswith("_EU"):
                bg_color.append('#2FEA8B')
            elif notary.endswith("_NA"):
                bg_color.append('#B541EA')
            elif notary.endswith("_SH"):
                bg_color.append('#00E2FF')
            else:
                bg_color.append('#F7931A')
            border_color.append('#000')
    else:
        notary = notary_list[0]
        labels = chain_list
        chartLabel = notary+ " Notarisations"
        for chain in chain_list:
            if chain in third_chains:
                bg_color.append('#00E2FF')
            elif chain in main_chains:
                bg_color.append('#2FEA8B')
            else:
                bg_color.append('#B541EA')
            border_color.append('#000')

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
                bg_color.append('#DC0333')
            elif notary.endswith("_EU"):
                bg_color.append('#2FEA8B')
            elif notary.endswith("_NA"):
                bg_color.append('#B541EA')
            elif notary.endswith("_SH"):
                bg_color.append('#00E2FF')
            else:
                bg_color.append('#F7931A')
            border_color.append('#000')
    else:
        notary = notary_list[0]
        labels = chain_list
        chartLabel = notary+ " Notary Balances"
        for chain in chain_list:
            if chain in third_chains:
                bg_color.append('#b541ea')
            elif chain in main_chains:
                bg_color.append('#2fea8b')
            else:
                bg_color.append('#f7931a')
            border_color.append('#000')

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


def get_chain_sync_data(request):
    season = get_season(int(time.time()))
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
    mined_season = mined.objects.filter(block_time__gte=seasons_info[season]['start_time'],
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


def get_mined_count_daily_data(request):
    resp = {}
    data = mined_count_daily.objects.all()
    print(data)
    print(len(data))

    data = apply_filters(request, MinedCountDailySerializer, data, 'daily_mined_count')
    print(len(data))
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
    url = request.build_absolute_uri('/api/chain_stats/daily/')
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

    url = request.build_absolute_uri('/api/notary_stats/daily/')
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

def get_notarisation_txid_single(txid=None):
    resp = []
    filter_kwargs = {}
    data = notarised.objects.filter(txid=txid)
    print(data)
    for item in data:
        row = {
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
            "scored":item.scored,
            "btc_validated":item.btc_validated
        }
        resp.append(row)
    print(resp)
    if len(resp) > 0:
        return wrap_api(resp)
    else:
        return wrap_api("TXID not found!")


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

def get_ntx_tenure_data(request):
    filters = ntxTenureSerializer.Meta.fields
    resp = {}
    data = notarised_tenure.objects.all()
    data = apply_filters(request, ntxTenureSerializer, data)
    data = data.order_by('chain', 'season').values()
    for item in data:

        if item["chain"] not in resp: 
            resp.update({item["chain"]:{}})

        if item["season"] not in resp[item["chain"]]:
            resp[item["chain"]].update({
                item["season"]: {
                    "first_ntx_block":item["first_ntx_block"],
                    "last_ntx_block":item["last_ntx_block"], 
                    "first_ntx_block_time":item["first_ntx_block_time"],
                    "last_ntx_block_time":item["last_ntx_block_time"],
                    "ntx_count":item["ntx_count"]
                }
            })

    return wrap_api(resp, filters)


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