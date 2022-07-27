#!/usr/bin/env python3
import time
import random
import datetime
import logging
from datetime import datetime as dt
from django.db.models import Max
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.models as models
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_atomicdex as dex
import kmd_ntx_api.serializers as serializers

logger = logging.getLogger("mylogger")


class TableSettings():
    def __init__(self, data, serializer, request):
        self.data = data
        self.request = request
        self.serializer = serializer
        self.required = {"season": SEASON}
        self.filters = ["season", "server", "notary", "coin"]

        if 'year' in request.GET:
            request.GET['year']
        if 'month' in request.GET:
            request.GET['month']

    def exclude_seasons(self):
        for s in ["Season_1", "Season_2", "Season_5_Testnet", "VOTE2022_Testnet"]:
            self.data = self.data.exclude(season=s)

    def get_distinct(self, exclude=None):
        season = helper.get_page_season(self.request)
        print(self.filters)
        if not exclude:
            exclude = []
        return query.get_distinct_filters(self.data, self.filters, exclude, season)

    def filter_data(self, table=None):
        self.data = query.apply_filters_api(self.request, self.serializer, self.data, table)

    def count(self):
        return self.data.count()

    def serialized(self):
        return self.serializer(self.data, many=True).data

    def selected(self):
        selected = {}
        [selected.update({i: helper.get_or_none(self.request, i)}) for i in self.filters]
        return selected


def get_addresses_rows(request):
    source = TableSettings(
        data=models.addresses.objects.all(),
        serializer=serializers.addressesSerializer,
        request=request
    )
    source.exclude_seasons()
    source.data = source.data.exclude(coin="BTC")
    distinct = source.get_distinct()
    selected = source.selected()
    source.filter_data()
    source.required = {
        "season": SEASON,
        "server": "Main"
    }
    if 'season' in selected:
        if 'server' in selected:
            distinct["notary"] = SEASONS_INFO[selected['season']]['notaries']
    else:
        distinct["notary"] = SEASONS_INFO[SEASON]['notaries']
    
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
        serializer=serializers.balancesSerializer,
        request=request
    )
    source.exclude_seasons()
    source.data = source.data.exclude(coin="BTC")
    distinct = source.get_distinct()
    source.filter_data()
    source.required = {
        "season": SEASON
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
        serializer=serializers.coinLastNtxSerializer,
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
        serializer=serializers.coinNtxSeasonSerializer,
        request=request
    )
    source.exclude_seasons()
    source.filters = ["season"]
    distinct = source.get_distinct()
    source.filter_data()
    print(source.data)

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
    source = TableSettings(
        data=models.mined.objects.all(),
        serializer=serializers.minedSerializer,
        request=request
    )
    today = datetime.date.today()
    source.required = {"season": SEASON, "date": f"{today}"}
    source.filters = ["category", "name", "date"]
    source.exclude_seasons()
    distinct = source.get_distinct(exclude=["date"])
    source.filter_data('mined')
    count = source.count()
    selected = source.selected()

    if 'season' in selected:
        distinct["name"] = SEASONS_INFO[selected['season']]['notaries']
    else:
        distinct["name"] = SEASONS_INFO[SEASON]['notaries']

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
        serializer=serializers.minedCountDailySerializer,
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
        serializer=serializers.minedCountSeasonSerializer,
        request=request
    )
    source.required = {
        "season": SEASON
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
    source = TableSettings(
        data=models.nn_ltc_tx.objects.all(),
        serializer=serializers.nnLtcTxSerializer,
        request=request
    )
    source.exclude_seasons()
    source.filters = ["season", "notary", "category"]
    distinct = source.get_distinct()
    source.filter_data()
    source.required = {
        "season": SEASON,
        "notary": random.choice(SEASONS_INFO[SEASON]['notaries']),
    }
    selected = source.selected()
    if 'season' in selected:
        distinct["notary"] = SEASONS_INFO[selected['season']]['notaries']
    else:
        distinct["notary"] = SEASONS_INFO[SEASON]['notaries']

    return {
        "distinct": distinct,
        "count": source.count(),
        "filters": source.filters,
        "required": source.required,
        "results": source.serialized(),
        "selected": selected
    }


def get_notarised_rows(request):
    source = TableSettings(
        data=models.notarised.objects.all(),
        serializer=serializers.notarisedSerializer,
        request=request
    )
    source.exclude_seasons()
    source.data = source.data.filter(scored=True)
    source.filters = ["season", "coin", "date"]
    distinct = source.get_distinct(exclude=["date"])
    source.filter_data('notarised')
    count = source.count()
    if count > 1000:
        source.serializer = serializers.notarisedSerializerLite

    today = datetime.date.today()
    source.required = {
        "season": SEASON,
        "coin": "KMD",
        "date": f"{today}"
    }

    return {
        "distinct": distinct,
        "count": count,
        "filters": source.filters,
        "required": source.required,
        "results": source.serialized(),
        "selected": source.selected()
    }


def get_notarised_coin_daily_rows(request):
    source = TableSettings(
        data=models.notarised_coin_daily.objects.all(),
        serializer=serializers.notarisedCoinDailySerializer,
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
        serializer=serializers.notarisedCountDailySerializer,
        request=request
    )
    source.exclude_seasons()
    source.required = {"season": SEASON}
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
        serializer=serializers.notaryLastNtxSerializer,
        request=request
    )
    if notary:
        source.data.filter(notary=notary)
    source.exclude_seasons()
    distinct = source.get_distinct()
    source.filter_data()
    source.required = {
        "season": SEASON,
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
        serializer=serializers.notaryNtxSeasonSerializer,
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


def get_rewards_tx_rows(request):
    source = TableSettings(
        data=models.rewards_tx.objects.all(),
        serializer=serializers.rewardsTxSerializer,
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
        serializer=serializers.serverNtxSeasonSerializer,
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
        serializer=serializers.scoringEpochsSerializer,
        request=request
    )
    source.data = source.data.exclude(server="LTC")
    source.required = {"season": SEASON}
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
    coin = helper.get_or_none(request, "coin")
    season = helper.get_page_season(request)

    data = query.get_coin_social_data(coin, season)
    data = data.order_by('coin').values()

    serializer = serializers.coinSocialSerializer(data, many=True)
    return serializer.data


def get_notary_last_mined_table_api(request):
    season = helper.get_page_season(request)
    season_notary_addresses = query.get_addresses_data(season=season, server="Main", coin="KMD")
    season_notary_addresses = list(season_notary_addresses.values_list("address", flat=True))
    data = query.get_mined_data(season)
    data = data.values("season", "name", "address")
    data = data.annotate(blocktime=Max("block_time"), blockheight=Max("block_height"))

    resp = []
    for item in data:
        if item["address"] in season_notary_addresses:
            resp.append(item)
    return resp


# TODO: Handle where coin not notarised
def get_notary_ntx_season_table_data(request, notary=None):
    season = helper.get_page_season(request)
    notary = helper.get_or_none(request, "notary", notary)

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
                    "since_last_block_time": helper.get_time_since(item['kmd_ntx_blocktime'])[1]
                })

    notary_ntx_summary_table = []
    for coin in notary_summary:
        notary_ntx_summary_table.append(notary_summary[coin])

    api_resp = {
        "ntx_season_data": ntx_season_data,
        "notary_ntx_summary_table": notary_ntx_summary_table,
    }
    return api_resp


# TODO: Handle where coin not notarised
def get_coin_ntx_season_table_data(request, coin=None):
    season = helper.get_page_season(request)
    coin = helper.get_or_none(request, "coin", coin)

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
                    "since_last_block_time": helper.get_time_since(item['kmd_ntx_blocktime'])[1]
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
    name = helper.get_or_none(request, "name")
    address = helper.get_or_none(request, "address")
    day_ago = int(time.time()) - SINCE_INTERVALS['day']
    data = query.get_mined_data(None, name, address).filter(
        block_time__gt=str(day_ago))
    data = data.values()

    serializer = serializers.minedSerializer(data, many=True)

    return serializer.data


def get_mined_count_season_table(request):
    season = helper.get_page_season(request)
    name = helper.get_or_none(request, "name")
    address = helper.get_or_none(request, "address")

    if not season and not name and not address:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'name', 'address']"
        }

    data = query.get_mined_count_season_data(season, name, address)
    if not name:
        data = data.filter(blocks_mined__gte=10)
    data = data.order_by('season', 'name').values()
    serializer = serializers.minedCountSeasonSerializer(data, many=True)
    return serializer.data




def get_coin_last_ntx_table(request, coin=None):
    season = helper.get_page_season(request)
    server = helper.get_page_server(request)
    coin = helper.get_or_none(request, "coin", coin)

    if not season and not coin:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'coin']"
        }

    data = query.get_notary_last_ntx_data(season, server, None, coin)
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
    season = helper.get_page_season(request)
    notary = helper.get_or_none(request, "notary", notary)
    data = query.get_notary_ntx_season_data(season, notary)
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
    season = helper.get_page_season(request)
    if not server: server = helper.get_page_server(request)
    data = query.get_server_ntx_season_data(season, server)
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
    season = helper.get_page_season(request)
    coin = helper.get_or_none(request, "coin", coin)
    data = query.get_coin_ntx_season_data(season, coin)
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
    season = helper.get_page_season(request)
    server = helper.get_page_server(request)
    coin = helper.get_or_none(request, "coin")

    data = query.get_notarised_tenure_data(season, server, coin)
    data = data.order_by('season', 'server', 'coin').values()

    serializer = serializers.notarisedTenureSerializer(data, many=True)

    return serializer.data




# UPDATE PENDING
def get_notary_epoch_scores_table(request, notary=None):
    season = helper.get_page_season(request)
    notary = helper.get_or_none(request, "notary", notary)

    epoch_coins_dict = info.get_epoch_coins_dict(season)

    notary_ntx_season_data = query.get_notary_ntx_season_data(
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


def get_split_stats_table(request):
    season = helper.get_page_season(request)
    notary = helper.get_or_none(request, "notary")

    category = "Split"

    if not season:
        return {
            "error": "You need to specify the following filter parameter: ['season']"
        }
    data = query.get_nn_btc_tx_data(season, notary, category)
    data = data.order_by('-block_height', 'address').values()
    split_summary = {}
    for item in data:
        notary = item["notary"]
        if notary != 'non-NN':
            if notary not in split_summary:
                split_summary.update({
                    notary: {
                        "split_count": 0,
                        "last_split_block": 0,
                        "last_split_time": 0,
                        "sum_split_utxos": 0,
                        "average_split_utxos": 0,
                        "sum_fees": 0,
                        "txids": []
                    }
                })

            fees = int(item["fees"])/100000000
            num_outputs = int(item["num_outputs"])
            split_summary[notary].update({
                "split_count": split_summary[notary]["split_count"]+1,
                "sum_split_utxos": split_summary[notary]["sum_split_utxos"]+num_outputs,
                "sum_fees": split_summary[notary]["sum_fees"]+fees
            })

            split_summary[notary]["txids"].append(item["txid"])

            if item["block_height"] > split_summary[notary]["last_split_time"]:
                split_summary[notary].update({
                    "last_split_block": int(item["block_height"]),
                    "last_split_time": int(item["block_time"])
                })

    for notary in split_summary:
        split_summary[notary].update({
            "average_split_utxos": split_summary[notary]["sum_split_utxos"]/split_summary[notary]["split_count"]
        })

    resp = []
    for notary in split_summary:
        row = {
            "notary": notary,
            "season": season
        }
        row.update(split_summary[notary])
        resp.append(row)
    return resp


## AtomicDEX Related

def get_coin_activation_table(request):
    selected_platform = helper.get_or_none(request, 'platform')
    json_data = dex.get_activation_commands(request)["commands"]

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
    bestorders = dex.get_bestorders(request)["result"]
    
    for _coin in bestorders:
        rows.append({
            "coin": _coin,
            "price": bestorders[_coin][0]["price"],
            "maxvolume": bestorders[_coin][0]["maxvolume"],
            "min_volume": bestorders[_coin][0]["min_volume"],
        })

    return rows

def get_orderbook_table(request):
    orderbook = dex.get_orderbook(request)

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
