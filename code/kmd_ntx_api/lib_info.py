import requests
from django.db.models import Count, Min, Max, Sum
from datetime import datetime, timezone
import datetime as dt
from kmd_ntx_api.endpoints import ENDPOINTS
from kmd_ntx_api.notary_pubkeys import get_notary_pubkeys
from kmd_ntx_api.pages import PAGES
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_dexstats as dexstats
import kmd_ntx_api.serializers as serializers


def get_coin_ntx_summary(season, coin):
    server = None

    coin_ntx_summary = {
            'ntx_24hr_count': 0,
            'ntx_season_count': 0,
            'ntx_season_score': 0,
            'last_ntx_time': '',
            'time_since_ntx': '',
            'last_ntx_block': '',
            'last_ntx_hash': '',
            'last_ntx_ac_block': '',
            'last_ntx_ac_hash': '',
            'ntx_block_lag': ''
    }
    coin_ntx_last = query.get_coin_last_ntx_data(season, server, coin).values()
    coin_ntx_season = query.get_coin_ntx_season_data(season).values()
    block_tip = dexstats.get_sync("KMD")["height"]

    for item in coin_ntx_season:
        if item["coin"] == coin:
            coin_ntx_summary.update({
                "ntx_season_count": item["coin_data"]['ntx_count'],
                "ntx_season_score": item["coin_data"]['ntx_score']
            })

    # season ntx stats
    if len(coin_ntx_last) > 0:
        time_since_last_ntx = helper.get_time_since(
                    coin_ntx_last[0]['kmd_ntx_blocktime']
                )[1]
        coin_ntx_summary.update({
            'ntx_24hr_count': get_notarised_data_24hr(season, server, coin).count(),
            'last_ntx_time': coin_ntx_last[0]['kmd_ntx_blocktime'],
            'time_since_ntx': time_since_last_ntx,
            'last_ntx_txid': coin_ntx_last[0]['kmd_ntx_txid'],
            'last_ntx_block': coin_ntx_last[0]['kmd_ntx_blockheight'],
            'last_ntx_hash': coin_ntx_last[0]['kmd_ntx_blockhash'],
            'last_ntx_ac_block': coin_ntx_last[0]['ac_ntx_height'],
            'last_ntx_ac_hash': coin_ntx_last[0]['ac_ntx_blockhash'],
            'ntx_block_lag': block_tip - coin_ntx_last[0]['kmd_ntx_blockheight']
        })

    return coin_ntx_summary


def get_all_coins():
    resp = []
    data = query.get_coins_data()
    for item in data:
        resp.append(item.coin)
    return resp


# TODO: Deprecate once CHMEX migrates to new endpoint
def get_btc_txid_data(category=None):
    resp = {}
    data = query.get_nn_btc_tx_data(None, None, category).exclude(category="SPAM")
    data = data.order_by('-block_height','address').values()

    for item in data:        
        address = item['address']

        if address not in resp:
            resp.update({address:[]})
        resp[address].append(item)

    return resp

 
# notary > coin > data
def get_last_nn_coin_ntx(season):
    ntx_last = query.get_notary_last_ntx_data(season).values()
    last_nn_coin_ntx = {}
    for item in ntx_last:
        notary = item['notary']
        if notary not in last_nn_coin_ntx:
            last_nn_coin_ntx.update({notary:{}})
        coin = item['coin']
        time_since = helper.get_time_since(item['kmd_ntx_blocktime'])[1]
        last_nn_coin_ntx[notary].update({
            coin:{
                "txid": item['kmd_ntx_txid'],
                "block_height": item['kmd_ntx_blockheight'],
                "block_time": item['kmd_ntx_blocktime'],
                "time_since": time_since
            }
        })
    return last_nn_coin_ntx   


def get_funding_totals(funding_data):
    funding_totals = {"fees": {}}
    now = int(time.time())

    for item in funding_data:
        tx_time = helper.day_hr_min_sec(now - item['block_time'])
        item.update({"time": tx_time})

        if item["notary"] not in ["unknown", "funding bot"]:
            if item["notary"] not in funding_totals:
                funding_totals.update({item["notary"]:{}})

            if item["coin"] not in funding_totals[item["notary"]]:
                funding_totals[item["notary"]].update({item["coin"]:-item["amount"]})
            else:
                val = funding_totals[item["notary"]][item["coin"]]-item["amount"]
                funding_totals[item["notary"]].update({item["coin"]:val})

            if item["coin"] not in funding_totals["fees"]:
                funding_totals["fees"].update({item["coin"]:-item["fee"]})
            else:
                val = funding_totals["fees"][item["coin"]]-item["fee"]
                funding_totals["fees"].update({item["coin"]:val})

    return funding_totals



def get_seed_stat_season(season, notary=None):
     return query.get_seed_version_data(season, notary).values('name').annotate(sum_score=Sum('score'))



def get_dpow_coins_list(season=None, server=None, epoch=None):
    dpow_coins = query.get_scoring_epochs_data(season, server, None, epoch).values('epoch_coins')
    
    coins_list = []
    for item in dpow_coins:
        coins_list += item['epoch_coins']
    coins_list = list(set(coins_list))
    coins_list.sort()
    return coins_list



def get_coin_addresses(coin, season=None):
    data = query.get_addresses_data(season, None, coin)
    return data.order_by('notary').values('notary','address')


def get_notary_ntx_24hr_summary(ntx_24hr, notary, season=None, coins_dict=None):
    if not season:
        season = SEASON
    if not coins_dict:
        coins_dict = helper.get_dpow_server_coins_dict(season)

    notary_ntx_24hr = {
            "btc_ntx": 0,
            "main_ntx": 0,
            "third_party_ntx": 0,
            "seed_node_status": 0,
            "most_ntx": "N/A",
            "score": 0
        }

    main_coins = helper.get_mainnet_coins(coins_dict)
    third_party_coins = helper.get_third_party_coins(coins_dict)   

    notary_coin_ntx_counts = {}

    for item in ntx_24hr:
        notaries = item['notaries']
        coin = item['coin']
        ntx_score = item['score_value']

        if notary in notaries:

            if coin not in notary_coin_ntx_counts:
                notary_coin_ntx_counts.update({coin:1})

            else:
                val = notary_coin_ntx_counts[coin]+1
                notary_coin_ntx_counts.update({coin:val})

            notary_ntx_24hr["score"] += ntx_score

    max_ntx_count = 0
    btc_ntx_count = 0
    main_ntx_count = 0
    third_party_ntx_count = 0

    for coin in notary_coin_ntx_counts:
        coin_ntx_count = notary_coin_ntx_counts[coin]
        if coin_ntx_count > max_ntx_count:
            max_coin = coin
            max_ntx_count = coin_ntx_count
        if coin == "KMD": 
            btc_ntx_count += coin_ntx_count
        elif coin in main_coins:
            main_ntx_count += coin_ntx_count
        elif coin in third_party_coins:
            third_party_ntx_count += coin_ntx_count

    seed_node_score = 0
    start = time.time() - SINCE_INTERVALS["day"]
    end = time.time()
    seed_data = query.get_seednode_version_stats_data(start, end-1, notary).values()
    notary_ntx_24hr["score"] = float(notary_ntx_24hr["score"])
    for item in seed_data:
        seed_node_score += round(item["score"], 2)
        notary_ntx_24hr["score"] += round(item["score"], 2)

    if max_ntx_count > 0:
        notary_ntx_24hr.update({
                "btc_ntx": btc_ntx_count,
                "main_ntx": main_ntx_count,
                "third_party_ntx": third_party_ntx_count,
                "seed_node_status": round(seed_node_score, 2),
                "most_ntx": str(max_ntx_count)+" ("+str(max_coin)+")"
            })
    return notary_ntx_24hr
 

def get_region_rank(region_season_stats_sorted, notary):
    higher_ranked_notaries = []
    for item in region_season_stats_sorted:
        if item["notary"] == notary:
            notary_score = item["score"]

    for item in region_season_stats_sorted:
        score = item['score']
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




# TODO: Deprecate once CHMEX migrates to new endpoint
# DONT MESS WITH THIS WITHOUT LETTING CHMEX KNOW !!!
def get_split_stats():
    resp = get_btc_txid_data("Split")
    split_summary = {}
    for address in resp:
        for tx in resp[address]:

            nn_name = tx["notary"]
            if nn_name not in split_summary:
                split_summary.update({
                    nn_name:{}
                })

            season = tx["season"]
            if season not in split_summary[nn_name]:
                split_summary[nn_name].update({
                    season: {
                        "split_count": 0,
                        "last_split_block": 0,
                        "last_split_time": 0,
                        "sum_split_utxos": 0,
                        "average_split_utxos": 0,
                        "sum_fees": 0,
                        "txids": []
                    }
                })

            fees = int(tx["fees"])/100000000
            num_outputs = int(tx["num_outputs"])
            split_summary[nn_name][season].update({
                "split_count": split_summary[nn_name][season]["split_count"]+1,
                "sum_split_utxos": split_summary[nn_name][season]["sum_split_utxos"]+num_outputs,
                "sum_fees": split_summary[nn_name][season]["sum_fees"]+fees
            })

            split_summary[nn_name][season].update({
                "average_split_utxos": split_summary[nn_name][season]["sum_split_utxos"]/split_summary[nn_name][season]["split_count"],
            })

            txid = tx["txid"]
            
            split_summary[nn_name][season]["txids"].append(txid)

            block_height = int(tx["block_height"])
            block_time = int(tx["block_time"])
            if block_time > split_summary[nn_name][season]["last_split_time"]:
                split_summary[nn_name][season].update({
                    "last_split_block": block_height,
                    "last_split_time": block_time
                })
    return split_summary

def get_epoch_coins_dict(season):
    epoch_coins_dict = {}
    epoch_coins_queryset = query.get_scoring_epochs_data(season).values()
    for item in epoch_coins_queryset:
        if item["season"] not in epoch_coins_dict:
            epoch_coins_dict.update({item["season"]:{}})
        if item["server"] not in epoch_coins_dict[item["season"]]:
            epoch_coins_dict[item["season"]].update({item["server"]:{}})
        if item["epoch"] not in epoch_coins_dict[season][item["server"]]:
            epoch_coins_dict[item["season"]][item["server"]].update({
                item["epoch"]: {
                    "coins": item["epoch_coins"],
                    "score_per_ntx": item["score_per_ntx"]
                }
            })
    return epoch_coins_dict



### V2 for API/INFO
def get_api_index(request):
    category = helper.get_or_none(request, "category")
    sidebar = helper.get_or_none(request, "sidebar")

    resp = []
    for endpoint in ENDPOINTS:
        endpoint_category = ENDPOINTS[endpoint]["category"]
        sidebar_status = ENDPOINTS[endpoint]["sidebar"]
        if (not category or category == endpoint_category) and (not sidebar or sidebar == sidebar_status):
            item = {"url": f"{THIS_SERVER}/api/{endpoint}"}
            item.update(ENDPOINTS[endpoint])
            resp.append(item)

    return resp


def get_pages_index(request):
    category = helper.get_or_none(request, "category")
    sidebar = helper.get_or_none(request, "sidebar")

    resp = []
    for page in PAGES:
        page_category = PAGES[page]["category"]
        sidebar_status = PAGES[page]["sidebar"]
        if (not category or category == page_category) and (not sidebar or sidebar == sidebar_status):
            item = {"url": f"{THIS_SERVER}/{page}"}
            item.update(PAGES[page])
            resp.append(item)

    return resp


def get_balances(request):
    resp = {}
    data = query.get_balances_data()
    data = helper.apply_filters_api(request, serializers.balancesSerializer, data) \
            .order_by('-season','notary', 'coin', 'balance') \
            .values()

    for item in data:
        
        season = item['season']
        if season not in resp:
            resp.update({season:{}})

        notary = item['notary']
        if notary not in resp[season]:
            resp[season].update({notary:{}})

        coin = item['coin']
        if coin not in resp[season][notary]:
            resp[season][notary].update({coin:{}})

        address = item['address']
        balance = item['balance']
        resp[season][notary][coin].update({address:balance})

    return resp


def get_base_58_coin_params(request):
    coin = helper.get_or_none(request, "coin")

    data = query.get_coins_data(coin)
    data = data.order_by('coin').values('coin', 'coins_info')

    resp = {}
    for item in data:
        coins_info = item['coins_info']
        coin = item['coin']
        if len(coins_info) > 0:
            if "pubtype" in coins_info and "wiftype" in coins_info and "p2shtype" in coins_info:
                pubtype = coins_info["pubtype"]
                wiftype = coins_info["wiftype"]
                p2shtype = coins_info["p2shtype"]
                resp.update({
                    coin: {
                        "pubtype": pubtype,
                        "wiftype": wiftype,
                        "p2shtype": p2shtype
                    }
                })
    return resp


def get_coins(request, coin=None):
    resp = {}
    coin = helper.get_or_none(request, "coin", coin)
    data = query.get_coins_data()
    if coin:
        data = data.filter(coin=coin)

    data = helper.apply_filters_api(request, serializers.coinsSerializer, data)
    data = data.order_by('coin').values()

    for item in data:
        resp.update({
            item["coin"]:{
                "coins_info": item["coins_info"],
                "dpow": item["dpow"],
                "dpow_tenure": item["dpow_tenure"],
                "explorers": item["explorers"],
                "electrums": item["electrums"],
                "electrums_ssl": item["electrums_ssl"],
                "mm2_compatible": item["mm2_compatible"],
                "dpow_active": item["dpow_active"]
            },
        })

    return resp


def get_coin_electrums(coin):
    data = query.get_coins_data(coin)
    if data.count() == 1:
        return data[0].values('electrums')[0]['electrums']


def get_coin_electrums_ssl(coin):
    data = query.get_coins_data(coin)
    if data.count() == 1:
        return data.values('electrums_ssl')[0]['electrums_ssl']


def get_coin_prefixes(request, coin=None):
    coin = helper.get_or_none(request, "coin", coin)
    data = query.get_coins_data(coin)
    data = data.order_by('coin').values('coin', 'coins_info')

    resp = {}
    for item in data:
        for i in ["pubtype", "wiftype", "p2shtype"]:
            if i in item['coins_info']:
                if item['coin'] not in resp:
                    resp.update({item['coin']: {
                        "decimal": {},
                        "hex": {}
                    }})
                resp[item['coin']]["decimal"].update({i: item['coins_info'][i]})
                resp[item['coin']]["hex"].update({i: pad_dec_to_hex(item['coins_info'][i])})
    return resp


def pad_dec_to_hex(num):
    hex_val = hex(num)[2:]
    if len(hex_val) % 2 != 0:
        hex_val = f"0{hex_val}"
    return hex_val.upper()

def get_coin_icons(request):
    coin = helper.get_or_none(request, "coin")

    data = query.get_coins_data(coin)
    data = data.order_by('coin').values('coin', 'coins_info')

    resp = {}
    for item in data:
        if "icon" in item['coins_info']:
            resp.update({item['coin']:item['coins_info']["icon"]})
    return resp


def get_daemon_cli(request):
    coin = helper.get_or_none(request, "coin")

    data = query.get_coins_data(coin)
    data = data.order_by('coin').values('coin', 'coins_info')

    resp = {}
    for item in data:
        coins_info = item['coins_info']
        coin = item['coin']
        if len(coins_info) > 0:
            if "cli" in coins_info:
                cli = coins_info["cli"]
                resp.update({coin:cli})
    return resp


def get_dpow_server_coins_info(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    epoch = helper.get_or_none(request, "epoch")
    coin = helper.get_or_none(request, "coin")
    timestamp = helper.get_or_none(request, "timestamp")

    if not season or not server:
        return {
            "error": "You need to specify both of the following filter parameters: ['season', 'server']"
        }
    data = query.get_scoring_epochs_data(season, server, coin, epoch, timestamp)
    data = data.values('epoch_coins')

    resp = []
    for item in data:
        resp += item['epoch_coins']

    resp = list(set(resp))
    resp.sort()

    return resp


def get_explorers(request):
    coin = helper.get_or_none(request, "coin")

    data = query.get_coins_data(coin)
    data = data.order_by('coin').values('coin', 'explorers')

    resp = {}
    for item in data:
        explorers = item['explorers']
        if len(explorers) > 0:
            coin = item['coin']
            resp.update({coin:explorers})
    return resp


def get_electrums(request):
    coin = helper.get_or_none(request, "coin")

    data = query.get_coins_data(coin)
    data = data.order_by('coin').values('coin', 'electrums')

    resp = {}
    for item in data:
        electrums = item['electrums']
        if len(electrums) > 0:
            coin = item['coin']
            resp.update({coin:electrums})
    return resp


def get_electrums_ssl(request):
    coin = helper.get_or_none(request, "coin")

    data = query.get_coins_data(coin)
    data = data.order_by('coin').values('coin', 'electrums_ssl')

    resp = {}
    for item in data:
        electrums_ssl = item['electrums_ssl']
        if len(electrums_ssl) > 0:
            coin = item['coin']
            resp.update({coin:electrums_ssl})
    return resp


def get_notary_icons(request):
    notary_social = get_nn_social_info(request)
    resp = {}
    for notary in notary_social:
        resp.update({notary:notary_social[notary]["icon"]})
    return resp


def get_mm2_coins_list():
    data = query.get_coins_data(None, True)
    data = data.order_by('coin').values('coin')

    resp = []
    for item in data:
        coin = item['coin']
        resp.append(coin)
    return resp


def get_launch_params(request):
    coin = helper.get_or_none(request, "coin")

    data = query.get_coins_data(coin)
    data = data.order_by('coin').values('coin', 'coins_info')

    resp = {}
    for item in data:
        coins_info = item['coins_info']
        coin = item['coin']
        if len(coins_info) > 0:
            if "launch_params" in coins_info:
                launch_params = coins_info["launch_params"]
                resp.update({coin:launch_params})
    return resp



def get_notarised_coin_daily(request):

    if "notarised_date" in request.GET:
        date_today = [int(x) for x in request.GET["notarised_date"].split("-")]
        notarised_date = dt.date(date_today[0], date_today[1], date_today[2])
    else:
        notarised_date = dt.date.today()

    resp = {str(notarised_date):{}}
    data = query.get_notarised_coin_daily_data(notarised_date)
    data = helper.apply_filters_api(request, serializers.notarisedCoinDailySerializer, data, 'daily_notarised_coin')
    data = data.order_by('notarised_date', 'coin').values()
    if len(data) > 0:
        for item in data:
            coin = item['coin']
            ntx_count = item['ntx_count']

            resp[str(notarised_date)].update({
                coin:ntx_count
            })

        delta = dt.timedelta(days=1)
        yesterday = item['notarised_date']-delta
        tomorrow = item['notarised_date']+delta
    else:
        today = dt.date.today()
        delta = dt.timedelta(days=1)
        yesterday = today-delta
        tomorrow = today+delta
    url = request.build_absolute_uri('/api/info/notarised_coin_daily/')
    return {
        "count": len(resp[str(notarised_date)]),
        "next": f"{url}?notarised_date={tomorrow}",
        "previous": f"{url}?notarised_date={yesterday}",
        "results": resp
    }


def get_notarised_count_daily(request):

    if "notarised_date" in request.GET:
        date_today = [int(x) for x in request.GET["notarised_date"].split("-")]
        notarised_date = dt.date(date_today[0], date_today[1], date_today[2])
    else:
        notarised_date = dt.date.today()

    resp = {str(notarised_date):{}}
    data = query.get_notarised_count_daily_data(notarised_date)
    data = helper.apply_filters_api(request, serializers.notarisedCountDailySerializer, data, 'daily_notarised_count')
    data = data.order_by('notarised_date', 'notary').values()
    if len(data) > 0:
        for item in data:
            notary = item['notary']

            resp[str(notarised_date)].update({
                notary:{
                    "master_server_count": item['master_server_count'],
                    "main_server_count": item['main_server_count'],
                    "third_party_server_count": item['third_party_server_count'],
                    "other_server_count": item['other_server_count'],
                    "total_ntx_count": item['total_ntx_count'],
                    "time_stamp": item['time_stamp'],
                    "coins": {}
                }
            })
            for coin in item['coin_ntx_counts']:
                resp[str(notarised_date)][notary]["coins"].update({
                    coin: {
                        "count": item['coin_ntx_counts'][coin],
                        "percentage": item['coin_ntx_pct'][coin]
                    }
                })

        delta = dt.timedelta(days=1)
        yesterday = item['notarised_date']-delta
        tomorrow = item['notarised_date']+delta
    else:
        today = dt.date.today()
        delta = dt.timedelta(days=1)
        yesterday = today-delta
        tomorrow = today+delta

    url = request.build_absolute_uri('/api/info/notarised_count_daily/')
    return {
        "count": len(resp[str(notarised_date)]),
        "next": f"{url}?notarised_date={tomorrow}",
        "previous": f"{url}?notarised_date={yesterday}",
        "results": resp
    }


def get_notarised_txid(request):
    txid = helper.get_or_none(request, "txid")

    if not txid:
        return {
            "error": "You need to specify the following filter parameter: ['txid']"
        }
    data = query.get_notarised_data(None, None, None, None, None, None, txid)
    data = data.values()

    serializer = serializers.notarisedSerializer(data, many=True)

    return serializer.data


def get_notarised_coins(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    epoch = helper.get_or_none(request, "epoch")
    data = query.get_notarised_coins_data(season, server, epoch)
    data = data.distinct('coin')
    resp = []
    for item in data.values():
        resp.append(item["coin"])
    return resp


def get_notarised_servers(request):
    season = helper.get_or_none(request, "season", SEASON)
    data = query.get_notarised_coins_data(season)
    data = data.distinct('server')
    resp = []
    for item in data.values():
        resp.append(item["server"])
    return resp


def get_notary_nodes_info(request):
    season = helper.get_or_none(request, "season", SEASON)
    if not season:
        return {
            "error": "You need to specify the following filter parameter: ['season']"
        }
    data = query.get_nn_social_data(season).values('notary')

    resp = []
    for item in data:
        resp.append(item['notary'])

    resp = list(set(resp))
    resp.sort()
    return resp


def get_notary_btc_transactions(request):
    season = helper.get_or_none(request, "season", SEASON)
    notary = helper.get_or_none(request, "notary")
    category = helper.get_or_none(request, "category")
    address = helper.get_or_none(request, "address")

    if not season or not notary:
        return {
            "error": "You need to specify both of the following filter parameters: ['season', 'notary']"
        }

    resp = {
        "season": season,
        "notary": notary,
    }
    txid_list = []
    data = query.get_nn_btc_tx_data(season, notary, category, address).values()

    for item in data:

        if item['category'] not in resp:
            resp.update({item['category']:{}})

        if item['txid'] not in resp[item['category']]:
            resp[item['category']].update({item['txid']:[item]})
            
        else:
            resp[item['category']][item['txid']].append(item)

        txid_list.append(item['txid'])

    api_resp = {
        "count": 0,
        "results": {}
    }

    for category in resp:
        if category not in ["season", "notary"]:
            api_resp["results"].update({
                category:{
                    "count": len(resp[category]),
                    "txids": resp[category]
                }
            })
            api_resp["count"] += len(resp[category])

    return api_resp


def get_notary_ltc_transactions(request):
    season = helper.get_or_none(request, "season", SEASON)
    notary = helper.get_or_none(request, "notary")
    category = helper.get_or_none(request, "category")
    address = helper.get_or_none(request, "address")

    if not season or not notary:
        return {
            "error": "You need to specify the following filter parameter: ['season', 'notary']"
        }

    resp = {
        "season": season,
        "notary": notary,
    }
    txid_list = []
    data = query.get_nn_ltc_tx_data(season, notary, category, address).values()

    for item in data:

        if item['category'] not in resp:
            resp.update({item['category']:{}})

        if item['txid'] not in resp[item['category']]:
            resp[item['category']].update({item['txid']:[item]})
            
        else:
            resp[item['category']][item['txid']].append(item)

        txid_list.append(item['txid'])

    api_resp = {
        "count": 0,
        "results": {}
    }

    for category in resp:
        if category not in ["season", "notary"]:
            api_resp["results"].update({
                category:{
                    "count": len(resp[category]),
                    "txids": resp[category]
                }
            })
            api_resp["count"] += len(resp[category])

    return api_resp


def get_notarisation_txid_list(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    epoch = helper.get_or_none(request, "epoch")
    coin = helper.get_or_none(request, "coin")
    notary = helper.get_or_none(request, "notary")

    if coin in ["BTC", "LTC", "KMD"]:
        server = coin

    if not season or not server or not coin:
        return {
            "error": "You need to specify the following filter parameters: ['season', 'server', 'coin']"
        }

    data = query.get_notarised_data(season, server, epoch, coin, notary).values('txid')

    resp = []
    for item in data:
        resp.append(item["txid"])

    resp = list(set(resp))
    return resp


def get_notary_btc_txid(request):
    txid = helper.get_or_none(request, "txid")

    if not txid:
        return {
            "error": "You need to specify the following filter parameter: ['txid']"
        }
    data = query.get_nn_btc_tx_data(None, None, None, None, txid)
    data = data.values()

    serializer = serializers.nnBtcTxSerializer(data, many=True)

    return serializer.data


def get_notary_ltc_txid(request):
    txid = helper.get_or_none(request, "txid")

    if not txid:
        return {
            "error": "You need to specify the following filter parameter: ['txid']"
        }
    data = query.get_nn_ltc_tx_data(None, None, None, None, txid)
    data = data.values()

    serializer = serializers.nnLtcTxSerializer(data, many=True)

    return serializer.data


def get_btc_txid_list(request):
    season = helper.get_or_none(request, "season", SEASON)
    notary = helper.get_or_none(request, "notary")
    category = helper.get_or_none(request, "category")
    address = helper.get_or_none(request, "address")

    if (not season or not notary) and (not season or not address):
        return {
            "error": "You need to specify the following filter parameters: ['season', 'notary'] or ['season', 'address']"
        }


    data = query.get_nn_btc_tx_data(season, notary, category, address).values('txid')

    resp = []
    for item in data:
        resp.append(item["txid"])

    resp = list(set(resp))
    return resp


def get_ltc_txid_list(request):
    season = helper.get_or_none(request, "season", SEASON)
    notary = helper.get_or_none(request, "notary")
    category = helper.get_or_none(request, "category")
    address = helper.get_or_none(request, "address")

    if (not season or not notary) and (not season or not address):
        return {
            "error": "You need to specify the following filter parameters: ['season', 'notary'] or ['season', 'address']"
        }

    data = query.get_nn_ltc_tx_data(season, notary, category, address).values('txid')

    resp = []
    for item in data:
        resp.append(item["txid"])

    resp = list(set(resp))
    return resp


def get_nn_social_info(request):
    season = helper.get_or_none(request, "season", helper.get_page_season(request))
    notary = helper.get_or_none(request, "notary")
    nn_social_info = {}
    nn_social_data = query.get_nn_social_data(season, notary).values()
    for item in nn_social_data:
        nn_social_info.update(helper.items_row_to_dict(item,'notary'))
    return nn_social_info


def get_coin_social_info(request):
    season = helper.get_or_none(request, "season", helper.get_page_season(request))
    coin = helper.get_or_none(request, "coin")
    coin_social_info = {}
    coin_social_data = query.get_coin_social_data(coin, season).values()
    for item in coin_social_data:
        coin_social_info.update(helper.items_row_to_dict(item,'coin'))
    return coin_social_info




def get_rewards_by_address_info(request):
    season = helper.get_or_none(request, "season").title()
    address = helper.get_or_none(request, "address")
    min_value = helper.get_or_none(request, "min_value")
    min_block = helper.get_or_none(request, "min_block")
    max_block = helper.get_or_none(request, "max_block")
    min_blocktime = helper.get_or_none(request, "min_blocktime")
    max_blocktime = helper.get_or_none(request, "max_blocktime")

    exclude_coinbase = True
    if "exclude_coinbase" in request.GET:
        if request.GET["exclude_coinbase"].lower() == 'false':
            exclude_coinbase = False
                    
    data = query.get_rewards_data(
                    season, address, min_value, min_block, max_block,
                    min_blocktime, max_blocktime, exclude_coinbase
                    ).values()

    resp = {
        "addresses": {},
        "num_addresses": 0,
        "num_claims": 0,
        "sum_claims": 0,
        "first_claim": 999999999999999,
        "last_claim": 0,
        "min_claim": 999999999999999,
        "max_claim": 0,
        "average_claim": 0,
        "claims_per_day": 0,
        "claims_per_month": 0,
        "claims_per_year": 0,
        "claimed_per_day": 0,
        "claimed_per_month": 0,
        "claimed_per_year": 0
    }
    for i in data:
        for address in i["input_addresses"]:
            helper.update_unique(
                resp["addresses"],
                address,
                {
                    "address_age": 0,
                    "num_claims": 0,
                    "sum_claims": 0,
                    "first_claim": 999999999999999,
                    "last_claim": 0,
                    "min_claim": 999999999999999,
                    "max_claim": 0,
                    "average_claim": 0,
                    "claims_per_month": 0,
                    "claims_per_year": 0
                }
            )
            resp["addresses"][address]["num_claims"] += 1
            resp["addresses"][address]["sum_claims"] += i['rewards_value'] / len(i["input_addresses"])

            if i["block_time"] < resp["addresses"][address]["first_claim"]:
                resp["addresses"][address]["first_claim"] = i["block_time"]

            if i["block_time"] > resp["addresses"][address]["last_claim"]:
                resp["addresses"][address]["last_claim"] = i["block_time"]

            if i["rewards_value"] / len(i["input_addresses"]) < resp["addresses"][address]["min_claim"]:
                resp["addresses"][address]["min_claim"] = round(i["rewards_value"] / len(i["input_addresses"]),3)

            if i["rewards_value"] / len(i["input_addresses"]) > resp["addresses"][address]["max_claim"]:
                resp["addresses"][address]["max_claim"] = round(i["rewards_value"] / len(i["input_addresses"]),3)

    addr_count = len(resp["addresses"])
    for address in resp["addresses"]:
        resp["addresses"][address]["address_age"] = resp["addresses"][address]["last_claim"]\
                                                  - resp["addresses"][address]["first_claim"]

        resp["addresses"][address]["average_claim"] = round(resp["addresses"][address]["sum_claims"]\
                                                    / resp["addresses"][address]["num_claims"],3)

        if resp["addresses"][address]["address_age"] > 0:
            claims_per_sec = resp["addresses"][address]["num_claims"]\
                           / resp["addresses"][address]["address_age"]
            resp["addresses"][address]["claims_per_month"] = round(claims_per_sec * SINCE_INTERVALS["month"],3)
            resp["addresses"][address]["claims_per_year"] = round(claims_per_sec * SINCE_INTERVALS["year"],3)

        resp["num_claims"] += 1
        resp["sum_claims"] += resp["addresses"][address]["sum_claims"]
        resp["addresses"][address]["sum_claims"] = round(resp["addresses"][address]["sum_claims"],3)

        if resp["first_claim"] > resp["addresses"][address]["first_claim"]:
            resp["first_claim"] = resp["addresses"][address]["first_claim"]

        if resp["last_claim"] < resp["addresses"][address]["last_claim"]:
            resp["last_claim"] = resp["addresses"][address]["last_claim"]

        if resp["min_claim"] > resp["addresses"][address]["min_claim"]:
            resp["min_claim"] = resp["addresses"][address]["min_claim"]

        if resp["max_claim"] < resp["addresses"][address]["max_claim"]:
            resp["max_claim"] = resp["addresses"][address]["max_claim"]

    resp["num_addresses"] = len(resp["addresses"])
    resp["average_claim"] = round(resp["sum_claims"] / resp["num_claims"],3)

    claim_period = resp["last_claim"] - resp["first_claim"]
    if claim_period > 0:
        claims_per_sec = resp["num_claims"] / claim_period
        claimed_per_sec = resp["sum_claims"] / claim_period
        resp["claims_per_day"] = round(claims_per_sec * SINCE_INTERVALS["day"],3)
        resp["claims_per_month"] = round(claims_per_sec * SINCE_INTERVALS["month"],3)
        resp["claims_per_year"] = round(claims_per_sec * SINCE_INTERVALS["year"],3)
        resp["claimed_per_day"] = round(claimed_per_sec * SINCE_INTERVALS["day"],3)
        resp["claimed_per_month"] = round(claimed_per_sec * SINCE_INTERVALS["month"],3)
        resp["claimed_per_year"] = round(claimed_per_sec * SINCE_INTERVALS["year"],3)

    return resp

def get_notary_seasons():
    ntx_seasons = {}
    pubkeys = get_notary_pubkeys()
    for season in pubkeys:
        for server in pubkeys[season]:
            for notary in pubkeys[season][server]:
                if notary not in ntx_seasons:
                    ntx_seasons.update({notary:[]})
                season = season.replace(".5", "")
                ntx_seasons[notary].append(season)
    for notary in ntx_seasons:
        ntx_seasons[notary] = list(set(ntx_seasons[notary]))
        ntx_seasons[notary].sort()

    return ntx_seasons
