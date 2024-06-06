#!/usr/bin/env python3
import time
import random
import datetime
from datetime import datetime as dt
from django.db.models import Max
from kmd_ntx_api.cache_data import get_from_memcache, refresh_cache

import kmd_ntx_api.models as models
from kmd_ntx_api.info import get_epoch_coins_dict
from kmd_ntx_api.const import SINCE_INTERVALS
from kmd_ntx_api.helper import get_or_none, get_page_server
from kmd_ntx_api.cron import days_ago, get_time_since
from kmd_ntx_api.notary_seasons import get_page_season, get_season, get_seasons_info
from kmd_ntx_api.serializers import addressesSerializer, balancesSerializer, \
    coinLastNtxSerializer, coinNtxSeasonSerializer, minedSerializer, \
    minedCountSeasonSerializer, minedCountDailySerializer, nnLtcTxSerializer, \
    notarisedSerializer, notarisedCoinDailySerializer, notarisedCountDailySerializer, \
    scoringEpochsSerializer, coinSocialSerializer, notarisedSerializerLite, \
    notaryLastNtxSerializer, notaryNtxSeasonSerializer, serverNtxSeasonSerializer, \
    kmdSupplySerializer, notarisedTenureSerializer
from kmd_ntx_api.activation import get_activation_commands
from kmd_ntx_api.atomicdex import get_bestorders, get_orderbook
from kmd_ntx_api.query import get_distinct_filters, apply_filters_api, get_mined_data, \
    get_mined_count_season_data, get_notary_last_ntx_data, get_notary_ntx_season_data, \
    get_addresses_data, get_coin_ntx_season_data, get_coin_social_data, get_notarised_tenure_data, \
    get_server_ntx_season_data
from kmd_ntx_api.logger import logger


class TableSettings():
    def __init__(self, data, serializer, request):
        self.data = data
        self.request = request
        self.serializer = serializer
        self.required = {"season": get_season()}
        self.filters = ["season", "server", "notary", "coin"]

        if 'year' in request.GET:
            request.GET['year']
        if 'month' in request.GET:
            request.GET['month']

    def exclude_seasons(self):
        for s in ["Season_1", "Season_2", "Season_5_Testnet", "VOTE2022_Testnet"]:
            self.data = self.data.exclude(season=s)

    def get_distinct(self, exclude=None):
        season = get_page_season(self.request)
        if not exclude:
            exclude = []
        return get_distinct_filters(self.data, self.filters, exclude, season)

    def filter_data(self, table=None):
        self.data = apply_filters_api(self.request, self.serializer, self.data, table)

    def count(self):
        return self.data.count()

    def serialized(self):
        return self.serializer(self.data, many=True).data

    def selected(self):
        selected = {}
        [selected.update({i: get_or_none(self.request, i)}) for i in self.filters]
        return selected


def get_addresses_rows(request):
    logger.calc("get_addresses_rows")
    source = TableSettings(
        data=models.addresses.objects.all(),
        serializer=addressesSerializer,
        request=request
    )
    seasons_info = get_seasons_info()
    source.exclude_seasons()
    source.data = source.data.exclude(coin="BTC")
    distinct = source.get_distinct()
    selected = source.selected()
    source.filter_data()
    source.required = {
        "season": get_season(),
        "server": "Main"
    }
    if 'season' in selected:
        if 'server' in selected:
            distinct["notary"] = seasons_info[selected['season']]['notaries']
    else:
        distinct["notary"] = seasons_info[get_season()]['notaries']
    
    return {
        "distinct": distinct,
        "count": source.count(),
        "filters": source.filters,
        "required": source.required,
        "results": source.serialized(),
        "selected": selected
    }


def get_balances_rows(request):
    source = TableSettings(
        data=models.balances.objects.all(),
        serializer=balancesSerializer,
        request=request
    )
    source.exclude_seasons()
    source.data = source.data.exclude(coin="BTC")
    distinct = source.get_distinct()
    source.filter_data()
    source.required = {
        "season": get_season(),
        "server": "Main"
    }

    return {
        "distinct": distinct,
        "count": source.count(),
        "filters": source.filters,
        "required": source.required,
        "results": source.serialized(),
        "selected": source.selected()
    }


def get_coin_last_ntx_rows(request):
    source = TableSettings(
        data=models.coin_last_ntx.objects.all(),
        serializer=coinLastNtxSerializer,
        request=request
    )
    source.exclude_seasons()
    source.filters = ["season", "server"]
    distinct = source.get_distinct()
    source.filter_data()

    return {
        "distinct": distinct,
        "count": source.count(),
        "filters": source.filters,
        "required": source.required,
        "results": source.serialized(),
        "selected": source.selected()
    }


def get_coin_ntx_season_rows(request):
    source = TableSettings(
        data=models.coin_ntx_season.objects.all(),
        serializer=coinNtxSeasonSerializer,
        request=request
    )
    source.exclude_seasons()
    source.filters = ["season"]
    distinct = source.get_distinct()
    source.filter_data()

    data = source.serialized()
    results = [{
        "coin": i["coin"],
        "season": i["season"],
        "ntx_count": i["coin_data"]["ntx_count"],
        "ntx_score": i["coin_data"]["ntx_score"],
        "pct_of_season_ntx_count": i["coin_data"]["pct_of_season_ntx_count"],
        "pct_of_season_ntx_score": i["coin_data"]["pct_of_season_ntx_score"],
        "timestamp": i["timestamp"]
    } for i in data]

    return {
        "distinct": distinct,
        "count": source.count(),
        "filters": source.filters,
        "required": source.required,
        "results": results,
        "selected": source.selected()
    }


def get_mined_rows(request):
    logger.calc("get_mined_rows")
    source = TableSettings(
        data=models.mined.objects.all(),
        serializer=minedSerializer,
        request=request
    )
    today = datetime.date.today()
    source.required = {"season": get_season(), "date": f"{today}"}
    source.filters = ["category", "name", "date"]
    source.exclude_seasons()
    distinct = source.get_distinct(exclude=["date"])
    source.filter_data('mined')
    count = source.count()
    selected = source.selected()
    season = get_season()
    seasons_info = get_seasons_info()

    if 'season' in selected:
        distinct["name"] = seasons_info[selected['season']]['notaries']
    else:
        distinct["name"] = seasons_info[season]['notaries']

    serialized = source.serialized()

    return {
        "distinct": distinct,
        "count": count,
        "filters": source.filters,
        "required": source.required,
        "results": serialized,
        "selected": selected
    }

def get_mined_count_daily_rows(request):
    source = TableSettings(
        data=models.mined_count_daily.objects.all(),
        serializer=minedCountDailySerializer,
        request=request
    )
    today = datetime.date.today()
    source.required = {"mined_date": f"{today}"}
    source.filters = ["mined_date"]
    distinct = source.get_distinct()
    source.filter_data()
    
    return {
        "distinct": distinct,
        "count": source.count(),
        "filters": source.filters,
        "required": source.required,
        "results": source.serialized(),
        "selected": source.selected()
    }

def get_mined_count_season_rows(request):
    source = TableSettings(
        data=models.mined_count_season.objects.all(),
        serializer=minedCountSeasonSerializer,
        request=request
    )
    source.required = {
        "season": get_season()
    }    
    source.filters = ["season", "name"]
    distinct = source.get_distinct()
    source.filter_data()
    
    return {
        "distinct": distinct,
        "count": source.count(),
        "filters": source.filters,
        "required": source.required,
        "results": source.serialized(),
        "selected": source.selected()
    }

def get_nn_ltc_tx_rows(request):
    logger.calc("get_nn_ltc_tx_rows")
    source = TableSettings(
        data=models.nn_ltc_tx.objects.all(),
        serializer=nnLtcTxSerializer,
        request=request
    )
    source.exclude_seasons()
    source.filters = ["season", "notary", "category"]
    distinct = source.get_distinct()
    source.filter_data()
    season = get_season()
    seasons_info = get_seasons_info()
    source.required = {
        "season": get_season(),
        "notary": random.choice(seasons_info[season]['notaries']),
    }
    selected = source.selected()
    if 'season' in selected:
        distinct["notary"] = seasons_info[selected['season']]['notaries']
    else:
        distinct["notary"] = seasons_info[season]['notaries']

    return {
        "distinct": distinct,
        "count": source.count(),
        "filters": source.filters,
        "required": source.required,
        "results": source.serialized(),
        "selected": selected
    }

# TODO: caching only happens on request. Large data like this should update on a loop instead.
def get_notarised_rows(request):
    season = get_page_season(request)
    coin = get_or_none(request, "coin", "DOC")
    date = get_or_none(request, "date", datetime.date.today())
    txid = get_or_none(request, "txid")
    cache_key = f"ntx_count_season_{season}_{coin}_{date}_{txid}"
    data = get_from_memcache(cache_key, expire=900)
    
    if data is None:
        logger.info(request.GET)
        source = TableSettings(
            data=models.notarised.objects.all(),
            serializer=notarisedSerializer,
            request=request
        )
        logger.info("Got source")
        source.exclude_seasons()
        source.data = source.data.filter(scored=True)
        logger.info("Got source.data")
        source.filters = ["season", "coin", "date", "txid"]
        distinct = source.get_distinct(exclude=["date"])
        logger.info("Got source.distinct")
        source.filter_data('notarised')
        logger.info("Got source.filter_data")

        source.required = {
            "season": season,
            "coin": coin,
            "date": f"{date}"
        }
        logger.info(source.required)

        count = source.count()
        if count > 1000:
            source.serializer = notarisedSerializerLite

        data = {
            "distinct": distinct,
            "count": count,
            "filters": source.filters,
            "required": source.required,
            "results": source.serialized(),
            "selected": source.selected()
        }
        refresh_cache(data=data, force=True, key=cache_key, expire=300)
    return data


def get_notarised_coin_daily_rows(request):
    source = TableSettings(
        data=models.notarised_coin_daily.objects.all(),
        serializer=notarisedCoinDailySerializer,
        request=request
    )
    source.exclude_seasons()
    source.filters = ['coin', 'year', 'month']
    distinct = source.get_distinct()
    source.filter_data("notarised_coin_daily")
    source.required = {}

    return {
        "distinct": distinct,
        "count": source.count(),
        "filters": source.filters,
        "required": source.required,
        "results": source.serialized(),
        "selected": source.selected()
    }


def get_notarised_count_daily_rows(request):
    source = TableSettings(
        data=models.notarised_count_daily.objects.all(),
        serializer=notarisedCountDailySerializer,
        request=request
    )
    source.exclude_seasons()
    source.required = {"season": get_season()}
    source.filters = ['season', 'notary', 'year', 'month']
    distinct = source.get_distinct()
    source.filter_data("notarised_count_daily")

    return {
        "distinct": distinct,
        "count": source.count(),
        "filters": source.filters,
        "required": source.required,
        "results": source.serialized(),
        "selected": source.selected()
    }


def get_notary_last_ntx_rows(request, notary=None):
    source = TableSettings(
        data=models.notary_last_ntx.objects.all(),
        serializer=notaryLastNtxSerializer,
        request=request
    )
    if notary:
        source.data.filter(notary=notary)
    source.exclude_seasons()
    distinct = source.get_distinct()
    source.filter_data()
    source.required = {
        "season": get_season(),
        "server": "Main"
    }

    return {
        "distinct": distinct,
        "count": source.count(),
        "filters": source.filters,
        "required": source.required,
        "results": source.serialized(),
        "selected": source.selected()
    }

def get_notary_ntx_season_rows(request):
    source = TableSettings(
        data=models.notary_ntx_season.objects.all(),
        serializer=notaryNtxSeasonSerializer,
        request=request
    )
    source.exclude_seasons()
    source.filters = ["season"]
    distinct = source.get_distinct()
    source.filter_data()

    data = source.serialized()
    results = [{
        "notary": i["notary"],
        "season": i["season"],
        "ntx_count": i["notary_data"]["ntx_count"],
        "ntx_score": i["notary_data"]["ntx_score"],
        "pct_of_season_ntx_count": i["notary_data"]["pct_of_season_ntx_count"],
        "pct_of_season_ntx_score": i["notary_data"]["pct_of_season_ntx_score"],
        "timestamp": i["timestamp"]
    } for i in data]
    
    return {
        "distinct": distinct,
        "count": source.count(),
        "filters": source.filters,
        "required": source.required,
        "results": results,
        "selected": source.selected()
    }


def get_kmd_supply_rows(request):
    source = TableSettings(
        data=models.kmd_supply.objects.all().order_by('block_height'),
        serializer=kmdSupplySerializer,
        request=request
    )
    today = datetime.date.today()
    source.required = {"date": f"{today}"}
    source.filters = ["date"]
    distinct = source.get_distinct(exclude=["date"])
    source.filter_data('rewards_tx')
    
    return {
        "distinct": distinct,
        "count": source.count(),
        "filters": source.filters,
        "required": source.required,
        "results": source.serialized(),
        "selected": source.selected()
    }


def get_server_ntx_season_rows(request):
    source = TableSettings(
        data=models.server_ntx_season.objects.all(),
        serializer=serverNtxSeasonSerializer,
        request=request
    )
    source.exclude_seasons()
    source.filters = ["season"]
    distinct = source.get_distinct()
    source.filter_data()

    data = source.serialized()
    results = [{
        "server": i["server"],
        "season": i["season"],
        "ntx_count": i["server_data"]["ntx_count"],
        "ntx_score": i["server_data"]["ntx_score"],
        "pct_of_season_ntx_count": i["server_data"]["pct_of_season_ntx_count"],
        "pct_of_season_ntx_score": i["server_data"]["pct_of_season_ntx_score"],
        "timestamp": i["timestamp"]
    } for i in data]

    return {
        "distinct": distinct,
        "count": source.count(),
        "filters": source.filters,
        "required": source.required,
        "results": results,
        "selected": source.selected()
    }

def get_scoring_epochs_rows(request):
    source = TableSettings(
        data=models.scoring_epochs.objects.all(),
        serializer=scoringEpochsSerializer,
        request=request
    )
    source.data = source.data.exclude(server="LTC")
    source.required = {"season": get_season()}
    source.filters = ["season"]
    distinct = source.get_distinct()
    source.filter_data('scoring_epochs')
    
    return {
        "distinct": distinct,
        "count": source.count(),
        "filters": source.filters,
        "required": source.required,
        "results": source.serialized(),
        "selected": source.selected()
    }


def get_coin_social_table(request):
    coin = get_or_none(request, "coin")
    season = get_page_season(request)

    data = get_coin_social_data(coin, season)
    data = data.order_by('coin').values()

    serializer = coinSocialSerializer(data, many=True)
    return serializer.data


def get_notary_last_mined_table_api(request):
    season = get_page_season(request)
    season_notary_addresses = get_addresses_data(season=season, server="Main", coin="KMD")
    season_notary_addresses = list(season_notary_addresses.values_list("address", flat=True))
    data = get_mined_data(season)
    data = data.values("season", "name", "address")
    data = data.annotate(blocktime=Max("block_time"), blockheight=Max("block_height"))

    resp = []
    for item in data:
        if item["address"] in season_notary_addresses:
            resp.append(item)
    return resp


# TODO: Handle where coin not notarised
def get_notary_ntx_season_table_data(request, notary=None):
    logger.merge("get_notary_ntx_season_table_data")
    season = get_page_season(request)
    notary = get_or_none(request, "notary", notary)

    if not notary or not season:
        return {
            "error": "You need to specify at least both of the following filter parameters: ['notary', 'season']"
        }

    ntx_season_data = get_notary_ntx_season_table(request, notary)

    notary_summary = {}
    for item in ntx_season_data:
        notary = item["notary"]

        for server in item["server_data"]:
            for coin in item["server_data"][server]["coins"]:
                if notary not in notary_summary:
                    notary_summary.update({notary: {}})

                notary_summary[notary].update({
                    coin: {
                        "season": season,
                        "server": server,
                        "notary": notary,
                        "coin": coin,
                        "coin_ntx_count": item["server_data"][server]["coins"][coin]["ntx_count"],
                        "coin_ntx_score": item["server_data"][server]["coins"][coin]["ntx_score"]
                    }
                })

        for coin in item["coin_data"]:
            if coin in notary_summary[notary]:
                notary_summary[notary][coin].update({
                    "coin_ntx_count_pct": item["coin_data"][coin]["pct_of_coin_ntx_count"],
                    "coin_ntx_score_pct": item["coin_data"][coin]["pct_of_coin_ntx_score"]
                })

    for notary in notary_summary:
        last_ntx = get_notary_last_ntx_rows(request, notary)["results"]
        for item in last_ntx:
            coin = item['coin']
            if coin in notary_summary[notary]:
                notary_summary[notary][coin].update({
                    "last_ntx_blockheight": item['kmd_ntx_blockheight'],
                    "last_ntx_blocktime": item['kmd_ntx_blocktime'],
                    "last_ntx_blockhash": item['kmd_ntx_blockhash'],
                    "last_ntx_txid": item['kmd_ntx_txid'],
                    "opret": item['opret'],
                    "since_last_block_time": get_time_since(item['kmd_ntx_blocktime'])[1]
                })

    notary_ntx_summary_table = []
    for coin in notary_summary:
        notary_ntx_summary_table.append(notary_summary[coin])

    api_resp = {
        "ntx_season_data": ntx_season_data,
        "notary_ntx_summary_table": notary_ntx_summary_table,
    }
    logger.merge("g0t_notary_ntx_season_table_data")
    return api_resp


# TODO: Handle where coin not notarised
def get_coin_ntx_season_table_data(request, coin=None):
    season = get_page_season(request)
    coin = get_or_none(request, "coin", coin)

    if not coin or not season:
        return {
            "error": "You need to specify at least both of the following filter parameters: ['coin', 'season']"
        }

    ntx_season_data = get_coin_ntx_season_table(request, coin)

    coin_summary = {}
    for item in ntx_season_data:
        coin = item["coin"]
        server = item["server"]
        for notary in item["notary_data"]:
            if coin not in coin_summary:
                coin_summary.update({coin: {}})

            coin_summary[coin].update({
                notary: {
                    "season": season,
                    "server": server,
                    "notary": notary,
                    "coin": coin,
                    "notary_ntx_count": item["notary_data"][notary]["ntx_count"],
                    "notary_ntx_score": item["notary_data"][notary]["ntx_score"]
                }
            })

        for notary in item["notary_data"]:
            if notary in coin_summary[coin]:
                coin_summary[coin][notary].update({
                    "coin_ntx_count_pct": item["notary_data"][notary]["pct_of_coin_ntx_count"],
                    "coin_ntx_score_pct": item["notary_data"][notary]["pct_of_coin_ntx_score"]
                })

    for coin in coin_summary:
        last_ntx = get_coin_last_ntx_table(request, coin)
        for item in last_ntx:
            notary = item['notary']
            if notary in coin_summary[coin]:
                coin_summary[coin][notary].update({
                    "last_ntx_blockheight": item['kmd_ntx_height'],
                    "last_ntx_blocktime": item['kmd_ntx_blocktime'],
                    "last_ntx_blockhash": item['kmd_ntx_blockhash'],
                    "last_ntx_txid": item['kmd_ntx_txid'],
                    "opret": item['opret'],
                    "since_last_block_time": get_time_since(item['kmd_ntx_blocktime'])[1]
                })

    coin_ntx_summary_table = []
    for coin in coin_summary:
        coin_ntx_summary_table.append(coin_summary[coin])

    api_resp = {
        "ntx_season_data": ntx_season_data,
        "coin_ntx_summary_table": coin_ntx_summary_table,
    }
    return api_resp


def get_mined_24hrs_table(request):
    name = get_or_none(request, "name")
    address = get_or_none(request, "address")
    data = get_mined_data(None, name, address).filter(
        block_time__gt=str(days_ago(1)))
    data = data.values()

    serializer = minedSerializer(data, many=True)

    return serializer.data


def get_mined_count_season_table(request):
    season = get_page_season(request)
    name = get_or_none(request, "name")
    address = get_or_none(request, "address")

    if not season and not name and not address:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'name', 'address']"
        }

    data = get_mined_count_season_data(season, name, address)
    if not name:
        data = data.filter(blocks_mined__gte=10)
    data = data.order_by('season', 'name').values()
    serializer = minedCountSeasonSerializer(data, many=True)
    return serializer.data




def get_coin_last_ntx_table(request, coin=None):
    season = get_page_season(request)
    server = get_page_server(request)
    coin = get_or_none(request, "coin", coin)

    if not season and not coin:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'coin']"
        }

    data = get_notary_last_ntx_data(season, server, None, coin)
    data = data.order_by('season', 'server', 'notary').values()

    resp = []
    for item in data:
        resp.append({
            "season": item['season'],
            "server": item['server'],
            "notary": item['notary'],
            "kmd_ntx_height": item['kmd_ntx_blockheight'],
            "kmd_ntx_blockhash": item['kmd_ntx_blockhash'],
            "kmd_ntx_txid": item['kmd_ntx_txid'],
            "kmd_ntx_blocktime": item['kmd_ntx_blocktime'],
            "ac_ntx_blockhash": item['ac_ntx_blockhash'],
            "ac_ntx_blockheight": item['ac_ntx_height'],
            "opret": item['opret']
        })

    return resp


def get_notary_ntx_season_table(request, notary=None):
    season = get_page_season(request)
    notary = get_or_none(request, "notary", notary)
    data = get_notary_ntx_season_data(season, notary)
    data = data.order_by('notary').values()

    resp = []
    for item in data:
        resp.append({
            "season": item['season'],
            "notary": item['notary'],
            "master_server_count": item["notary_data"]["servers"]["KMD"]['ntx_count'],
            "main_server_count": item["notary_data"]["servers"]["Main"]['ntx_count'],
            "third_party_server_count": item["notary_data"]["servers"]["Third_Party"]['ntx_count'],
            "total_ntx_count": item["notary_data"]['ntx_count'],
            "total_ntx_score": float(item["notary_data"]['ntx_score']),
            "coin_data": item["notary_data"]['coins'],
            "server_data": item["notary_data"]['servers'],
            "timestamp": item['timestamp']
        })

    return resp


def get_server_ntx_season_table(request, server=None):
    season = get_page_season(request)
    if not server: server = get_page_server(request)
    data = get_server_ntx_season_data(season, server)
    data = data.order_by('server').values()

    resp = []
    for item in data:
        resp.append({
            "season": item['season'],
            "server": item['server'],
            "master_server_count": item["server_data"]["servers"]["KMD"]['ntx_count'],
            "main_server_count": item["server_data"]["servers"]["Main"]['ntx_count'],
            "third_party_server_count": item["server_data"]["servers"]["Third_Party"]['ntx_count'],
            "total_ntx_count": item["server_data"]['ntx_count'],
            "total_ntx_score": float(item["server_data"]['ntx_score']),
            "coins_data": item["server_data"]['coins'],
            "notary_data": item["server_data"]['notaries'],
            "timestamp": item['timestamp']
        })

    return resp

def get_coin_ntx_season_table(request, coin=None):
    season = get_page_season(request)
    coin = get_or_none(request, "coin", coin)
    data = get_coin_ntx_season_data(season, coin)
    data = data.order_by('coin').values()
    resp = []
    for item in data:
        coin_data = item["coin_data"]
        if item['coin'] in ["KMD", "LTC", "BTC"]:
            server = item['coin']
        elif len(list(coin_data['servers'].keys())) > 0:
            server = list(coin_data['servers'].keys())[0]

            resp.append({
                "season": item['season'],
                "server": server,
                "coin": item['coin'],
                "total_ntx_count": coin_data['ntx_count'],
                "total_ntx_score": float(item["coin_data"]['ntx_score']),
                "pct_of_season_ntx_count": coin_data['pct_of_season_ntx_count'],
                "pct_of_season_ntx_score": coin_data['pct_of_season_ntx_score'],
                "notary_data": item["coin_data"]['notaries'],
                "server_data": item["coin_data"]['servers'],
                "timestamp": item['timestamp']
            })

    return resp




def get_notarised_tenure_table(request):
    season = get_page_season(request)
    server = get_page_server(request)
    coin = get_or_none(request, "coin")

    data = get_notarised_tenure_data(season, server, coin)
    data = data.order_by('season', 'server', 'coin').values()

    serializer = notarisedTenureSerializer(data, many=True)

    return serializer.data




# UPDATE PENDING
def get_notary_epoch_scores_table(request, notary=None):
    season = get_page_season(request)
    notary = get_or_none(request, "notary", notary)

    epoch_coins_dict = get_epoch_coins_dict(season)

    notary_ntx_season_data = get_notary_ntx_season_data(
        season, notary).values()

    rows = []
    totals = {
        "counts": {},
        "scores": {}
    }

    total_scores = {}
    for item in notary_ntx_season_data:
        notary = item["notary"]
        totals["counts"].update({
            notary: item["notary_data"]["ntx_count"]
        })
        totals["scores"].update({
            notary: item["notary_data"]["ntx_score"]
        })
        '''
        ['id', 'season', 'notary', 'master_server_count', 'main_server_count',
        'third_party_server_count', 'other_server_count', 'total_ntx_count',
        'total_ntx_score', 'coin_ntx_counts', 'coin_ntx_scores', 'coin_ntx_count_pct',
        'coin_ntx_score_pct', 'coin_last_ntx', 'server_ntx_counts', 'server_ntx_scores',
        'server_ntx_count_pct', 'server_ntx_score_pct', 'timestamp']
        '''
        server_data = item["notary_data"]["servers"]
        for server in server_data:
            if server not in ['Unofficial', 'LTC']:
                for epoch in server_data[server]['epochs']:
                    if epoch != 'Unofficial':

                        for coin in server_data[server]['epochs'][epoch]["coins"]:

                            if epoch.find("_") > -1:
                                epoch_id = epoch.split("_")[1]
                            else:
                                epoch_id = epoch
                            row = {
                                "notary": notary,
                                "season": season.replace("_", " "),
                                "server": server,
                                "epoch": epoch_id,
                                "coin": coin,
                                "score_per_ntx": server_data[server]['epochs'][epoch]["score_per_ntx"],
                                "epoch_coin_count": server_data[server]['epochs'][epoch]["coins"][coin]["ntx_count"],
                                "epoch_coin_score": server_data[server]['epochs'][epoch]["coins"][coin]["ntx_score"],
                                "epoch_coin_count_self_pct": server_data[server]['epochs'][epoch]["coins"][coin]["pct_of_notary_ntx_count"],
                                "epoch_coin_score_self_pct": server_data[server]['epochs'][epoch]["coins"][coin]["pct_of_notary_ntx_score"],
                            }

                            rows.append(row)
    return rows, totals


## AtomicDEX Related

def get_coin_activation_table(request):
    selected_platform = get_or_none(request, 'platform')
    json_data = get_activation_commands(request)["commands"]

    table_data = []
    for platform in json_data:
        if platform == selected_platform or selected_platform is None:
            for coin in json_data[platform]:
                table_data.append({
                    "platform": platform,
                    "coin": coin,
                    "command": json_data[platform][coin]
                })
    return table_data


def get_bestorders_table(request):
    rows = []
    bestorders = get_bestorders(request)["result"]
    
    for _coin in bestorders:
        rows.append({
            "coin": _coin,
            "price": bestorders[_coin][0]["price"],
            "maxvolume": bestorders[_coin][0]["maxvolume"],
            "min_volume": bestorders[_coin][0]["min_volume"],
        })

    return rows

def get_orderbook_table(request):
    orderbook = get_orderbook(request)

    base = request.GET["base"]
    rel = request.GET["rel"]

    orders = []
    if "bids" in orderbook:

        for bid in orderbook["bids"]:
            price = bid["price"]
            maxvolume = bid["maxvolume"]
            min_volume = bid["min_volume"]
            orders.append({
                "type": 'bid',
                "base": base,
                "rel": rel,
                "price": price,
                "maxvolume": maxvolume,
                "min_volume": min_volume,
                "total": float(maxvolume)/float(price)
            })

    if "asks" in orderbook:

        for ask in orderbook["asks"]:
            price = ask["price"]
            maxvolume = ask["maxvolume"]
            min_volume = ask["min_volume"]
            orders.append({
                "type": 'ask',
                "base": base,
                "rel": rel,
                "price": price,
                "maxvolume": maxvolume,
                "min_volume": min_volume,
                "total": float(maxvolume)*float(price)
            })

    return orders


def get_dex_stats_table(gui_stats):
    return {
        "os": get_dex_os_stats_table(gui_stats),
        "ui": get_dex_ui_stats_table(gui_stats),
        "version": get_dex_version_stats_table(gui_stats)
    }

def get_dex_os_stats_table(gui_stats):
    os_stats = {}
    for i in ["maker_dict", "taker_dict"]:
        j = i.split("_")[0]
        os_stats.update({j: []})
        for os in gui_stats[i]["os"]:
            os_stats[j].append({
                "os": os,
                "num_swaps": gui_stats[i]["os"][os]["num_swaps"],
                "num_pubkeys": len(gui_stats[i]["os"][os]["pubkeys"]),
                "global_swap_pct": gui_stats[i]["os"][os]["global_swap_pct"],
                "global_pubkey_pct": gui_stats[i]["os"][os]["global_pubkey_pct"]
            })
    return os_stats


def get_dex_ui_stats_table(gui_stats):
    ui_stats = {}
    for i in ["maker_dict", "taker_dict"]:
        j = i.split("_")[0]
        ui_stats.update({j: []})
        for os in gui_stats[i]["os"]:
            for ui in gui_stats[i]["os"][os]["ui"]:

                ui_stats[j].append({
                    "os": os,
                    "ui": ui,
                    "num_swaps": gui_stats[i]["os"][os]["ui"][ui]["num_swaps"],
                    "num_pubkeys": len(gui_stats[i]["os"][os]["ui"][ui]["pubkeys"]),
                    "os_swap_pct": gui_stats[i]["os"][os]["ui"][ui]["os_swap_pct"],
                    "os_pubkey_pct": gui_stats[i]["os"][os]["ui"][ui]["os_pubkey_pct"],
                    "global_swap_pct": gui_stats[i]["os"][os]["ui"][ui]["global_swap_pct"],
                    "global_pubkey_pct": gui_stats[i]["os"][os]["ui"][ui]["global_pubkey_pct"]
                })
    return ui_stats


def get_dex_version_stats_table(gui_stats):
    ui_stats = {}
    for i in ["maker_dict", "taker_dict"]:
        j = i.split("_")[0]
        ui_stats.update({j: []})
        for os in gui_stats[i]["os"]:
            for ui in gui_stats[i]["os"][os]["ui"]:
                for v in gui_stats[i]["os"][os]["ui"][ui]["versions"]:
                    ui_stats[j].append({
                        "os": os,
                        "ui": ui,
                        "version": v,
                        "num_swaps": gui_stats[i]["os"][os]["ui"][ui]["versions"][v]["num_swaps"],
                        "num_pubkeys": len(gui_stats[i]["os"][os]["ui"][ui]["versions"][v]["pubkeys"]),
                        "ui_swap_pct": gui_stats[i]["os"][os]["ui"][ui]["versions"][v]["ui_swap_pct"],
                        "ui_pubkey_pct": gui_stats[i]["os"][os]["ui"][ui]["versions"][v]["ui_pubkey_pct"],
                        "num_swaps": gui_stats[i]["os"][os]["ui"][ui]["versions"][v]["num_swaps"],
                        "os_swap_pct": gui_stats[i]["os"][os]["ui"][ui]["versions"][v]["os_swap_pct"],
                        "os_pubkey_pct": gui_stats[i]["os"][os]["ui"][ui]["versions"][v]["os_pubkey_pct"],
                        "global_swap_pct": gui_stats[i]["os"][os]["ui"][ui]["versions"][v]["global_swap_pct"],
                        "global_pubkey_pct": gui_stats[i]["os"][os]["ui"][ui]["versions"][v]["global_pubkey_pct"]
                    })
    return ui_stats
