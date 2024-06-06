#!/usr/bin/env python3
import time
import requests
from django.db.models import Count, Min, Max, Sum
from datetime import datetime, timezone
import datetime as dt


from kmd_ntx_api.const import SINCE_INTERVALS
from kmd_ntx_api.mining import get_mined_data
from kmd_ntx_api.explorers import get_sync
from kmd_ntx_api.ntx import get_notarised_date
from kmd_ntx_api.notary_seasons import get_page_season
from kmd_ntx_api.serializers import balancesSerializer, notarisedSerializer, \
    coinsSerializer, notarisedCoinDailySerializer, notarisedCountDailySerializer, \
    nnLtcTxSerializer
from kmd_ntx_api.cron import get_time_since
from kmd_ntx_api.helper import get_or_none, get_page_server, \
    pad_dec_to_hex, get_mainnet_coins, get_third_party_coins, items_row_to_dict
from kmd_ntx_api.query import get_notarised_data, get_coin_last_ntx_data, \
    get_coin_ntx_season_data, get_coins_data, get_seednode_version_stats_data, \
    get_scoring_epochs_data, get_balances_data, apply_filters_api, \
    get_notarised_coin_daily_data, get_notarised_count_daily_data, \
    get_notarised_coins_data, get_nn_social_data, get_nn_ltc_tx_data, \
    get_coin_social_data
from kmd_ntx_api.query import get_addresses_data, get_coins_data, get_scoring_epochs_data
from kmd_ntx_api.logger import logger, timed
from kmd_ntx_api.memcached import MEMCACHE
from kmd_ntx_api.cache_data import get_from_memcache, refresh_cache


def get_balances(request):
    resp = {}
    data = get_balances_data()
    data = apply_filters_api(request, balancesSerializer, data) \
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


def get_notarised_txid(request):
    txid = get_or_none(request, "txid")
    if not txid:
        return {
            "error": "You need to specify the following filter parameter: ['txid']"
        }
    data = get_notarised_data(txid=request.GET["txid"]).values()
    data = data.values()
    serializer = notarisedSerializer(data, many=True)
    return serializer.data


def get_nn_social_info(request):
    season = get_page_season(request)
    notary = get_or_none(request, "notary")
    nn_social_info = {}
    nn_social_data = get_nn_social_data(season, notary).values()
    for item in nn_social_data:
        nn_social_info.update(items_row_to_dict(item,'notary'))
    return nn_social_info


def get_coin_social_info(request):
    season = get_page_season(request)
    coin = get_or_none(request, "coin")
    coin_social_info = {}
    coin_social_data = get_coin_social_data(coin, season).values()
    for item in coin_social_data:
        coin_social_info.update(items_row_to_dict(item,'coin'))
    return coin_social_info



def get_coins(request, coin=None):
    resp = {}
    coin = get_or_none(request, "coin", coin)
    data = get_coins_data()
    if coin:
        data = data.filter(coin=coin)

    data = apply_filters_api(request, coinsSerializer, data)
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
                "electrums_wss": item["electrums_wss"],
                "lightwallets": item["lightwallets"],
                "mm2_compatible": item["mm2_compatible"],
                "dpow_active": item["dpow_active"]
            },
        })
    return resp


# Only used in testnet.py
def get_coin_addresses(coin, season=None):
    data = get_addresses_data(season, None, coin)
    return data.order_by('notary').values('notary','address')


# Only used in forms.py
def get_mm2_coins_list():
    try:
        data = get_coins_data(None, True)
        data = data.order_by('coin').values('coin')
        return [i["coin"] for i in data]
    except:
        return []


def get_daemon_cli(request):
    coin = get_or_none(request, "coin")

    data = get_coins_data(coin)
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


def get_coin_icons(request):
    coin = get_or_none(request, "coin")

    data = get_coins_data(coin)
    data = data.order_by('coin').values('coin', 'coins_info')

    resp = {}
    for item in data:
        if "icon" in item['coins_info']:
            resp.update({item['coin']:item['coins_info']["icon"]})
    return resp



def get_epoch_coins_dict(season):
    epoch_coins_dict = {}
    epoch_coins_queryset = get_scoring_epochs_data(season).values()
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


def get_all_coins():
    resp = []
    data = get_coins_data()
    for item in data:
        resp.append(item.coin)
    return resp


def get_notary_icons(request):
    notary_social = get_nn_social_info(request)
    resp = {}
    for notary in notary_social:
        resp.update({notary:notary_social[notary]["icon"]})
    return resp


def get_notarised_coins(request):
    season = get_page_season(request)
    server = get_page_server(request)
    epoch = get_or_none(request, "epoch")
    data = get_notarised_coins_data(season, server, epoch)
    data = data.distinct('coin')
    resp = []
    for item in data.values():
        resp.append(item["coin"])
    return resp


def get_notarised_servers(request):
    season = get_page_season(request)
    data = get_notarised_coins_data(season)
    data = data.distinct('server')
    resp = []
    for item in data.values():
        resp.append(item["server"])
    return resp


def get_base_58_coin_params(request):
    coin = get_or_none(request, "coin")

    data = get_coins_data(coin)
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



def get_notarised_coin_daily(request):

    if "notarised_date" in request.GET:
        date_today = [int(x) for x in request.GET["notarised_date"].split("-")]
        notarised_date = dt.date(date_today[0], date_today[1], date_today[2])
    else:
        notarised_date = dt.date.today()

    resp = {str(notarised_date):{}}
    data = get_notarised_coin_daily_data(notarised_date)
    data = apply_filters_api(request, notarisedCoinDailySerializer, data, 'daily_notarised_coin')
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
    data = get_notarised_count_daily_data(notarised_date)
    data = apply_filters_api(request, notarisedCountDailySerializer, data, 'daily_notarised_count')
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
                    "timestamp": item['timestamp'],
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


# Functions only used in profiles.py
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
    coin_ntx_last = get_coin_last_ntx_data(season, server, coin).values()
    coin_ntx_season = get_coin_ntx_season_data(season).values()
    block_tip = get_sync("KMD")["height"]

    for item in coin_ntx_season:
        if item["coin"] == coin:
            coin_ntx_summary.update({
                "ntx_season_count": item["coin_data"]['ntx_count'],
                "ntx_season_score": item["coin_data"]['ntx_score']
            })

    # season ntx stats
    if len(coin_ntx_last) > 0:
        time_since_last_ntx = get_time_since(
                    coin_ntx_last[0]['kmd_ntx_blocktime']
                )[1]
        coin_ntx_summary.update({
            'ntx_24hr_count': get_notarised_date(season, server, coin, None, True).count(),
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


# Functions for API endpoints
def get_mined_between_blocks(request):
    min_block = 0
    max_block = 9999999
    if "min_block" in request.GET:
        min_block = int(request.GET["min_block"])
    if "max_block" in request.GET:
        max_block = int(request.GET["max_block"])
    return get_mined_data(
            min_block=min_block,
            max_block=max_block
        ).aggregate(
            sum_mined=Sum('value'),
            blocks_mined=Count('value'),
            max_block=Max('block_height'),
            min_block=Min('block_height'),
            max_blocktime=Max('block_time'),
            min_blocktime=Min('block_time')
        )


def get_mined_between_blocktimes(request):
    min_blocktime = 0
    max_blocktime = 9999999999
    if "min_blocktime" in request.GET:
        min_blocktime = int(request.GET["min_blocktime"])
    if "max_blocktime" in request.GET:
        max_blocktime = int(request.GET["max_blocktime"])
    return get_mined_data(
            min_blocktime=min_blocktime,
            max_blocktime=max_blocktime
        ).aggregate(
            sum_mined=Sum('value'),
            blocks_mined=Count('value'),
            max_block=Max('block_height'),
            min_block=Min('block_height'),
            max_blocktime=Max('block_time'),
            min_blocktime=Min('block_time')
        )


def get_coin_prefixes(request, coin=None):
    coin = get_or_none(request, "coin", coin)
    data = get_coins_data(coin)
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

@timed
def get_dpow_server_coins_info(
    request=None, season=None,
    server=None, epoch=None,
    coin=None, timestamp=None
):
    data = None
    cache_key = None
    logger.calc("get_dpow_server_coins_info")
    if request is not None:
        season = get_page_season(request)
        server = get_page_server(request)
        epoch = get_or_none(request, "epoch")
        coin = get_or_none(request, "coin")
        timestamp = get_or_none(request, "timestamp")
    else:
        cache_key = f"dpow_server_coins_info_{season}_{server}"

    if not season or not server:
        return {
            "error": "You need to specify both of the following filter parameters: ['season', 'server']"
        }
    if cache_key is not None:
        data = get_from_memcache(cache_key)

    if data is None:
        data = get_scoring_epochs_data(season, server, coin, epoch, timestamp)
        data = data.values('epoch_coins')
        logger.info(data)
        logger.info("#################################")

        resp = []
        for item in data:
            resp += item['epoch_coins']

        resp = list(set(resp))
        resp.sort()
        if epoch is None and coin is None and timestamp is None:
            logger.calc(f"adding {cache_key} to memcache")
            refresh_cache(key=cache_key, data=resp, expire=86400)
        return resp
    return data


def get_launch_params(request):
    coin = get_or_none(request, "coin")

    data = get_coins_data(coin)
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


def get_notary_nodes_info(request):
    season = get_page_season(request)
    if not season:
        return {
            "error": "You need to specify the following filter parameter: ['season']"
        }
    data = get_nn_social_data(season).values('notary')

    resp = []
    for item in data:
        resp.append(item['notary'])

    resp = list(set(resp))
    resp.sort()
    return resp


def get_notary_ltc_transactions(request):
    season = get_page_season(request)
    notary = get_or_none(request, "notary")
    category = get_or_none(request, "category")
    address = get_or_none(request, "address")

    if not season or not notary:
        return {
            "error": "You need to specify the following filter parameter: ['season', 'notary']"
        }

    resp = {
        "season": season,
        "notary": notary,
    }
    txid_list = []
    data = get_nn_ltc_tx_data(season, notary, category, address).values()

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


def get_notary_ltc_txid(request):
    txid = get_or_none(request, "txid")

    if not txid:
        return {
            "error": "You need to specify the following filter parameter: ['txid']"
        }
    data = get_nn_ltc_tx_data(None, None, None, None, txid)
    data = data.values()

    serializer = nnLtcTxSerializer(data, many=True)

    return serializer.data


def get_ltc_txid_list(request):
    logger.calc("ltc_txid_list")
    season = get_page_season(request)
    notary = get_or_none(request, "notary")
    category = get_or_none(request, "category")
    address = get_or_none(request, "address")

    if (not season or not notary) and (not season or not address):
        return {
            "error": "You need to specify the following filter parameters: ['season', 'notary'] or ['season', 'address']"
        }

    data = get_nn_ltc_tx_data(season, notary, category, address).values('txid')

    resp = []
    for item in data:
        resp.append(item["txid"])

    resp = list(set(resp))
    return resp


def get_notarisation_txid_list(request):
    season = get_page_season(request)
    server = get_page_server(request)
    epoch = get_or_none(request, "epoch")
    coin = get_or_none(request, "coin")
    notary = get_or_none(request, "notary")

    if coin in ["BTC", "LTC", "KMD"]:
        server = coin

    if not season or not server or not coin:
        return {
            "error": "You need to specify the following filter parameters: ['season', 'server', 'coin']"
        }

    data = get_notarised_data(season, server, epoch, coin, notary).values('txid')

    resp = []
    for item in data:
        resp.append(item["txid"])

    resp = list(set(resp))
    return resp

