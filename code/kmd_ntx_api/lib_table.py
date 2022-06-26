import time
from datetime import datetime as dt
from django.db.models import Max
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.serializers as serializers


def get_addresses_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    coin = helper.get_or_none(request, "coin")
    notary = helper.get_or_none(request, "notary")
    address = helper.get_or_none(request, "address")

    if not season and not coin and not notary and not address:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'coin', 'notary', 'address']"
        }

    data = query.get_addresses_data(season, server, coin, notary, address)
    data = data.values()

    resp = []
    for item in data:

        resp.append({
            "season": item['season'],
            "server": item['server'],
            "coin": item['coin'],
            "notary": item['notary'],
            "address": item['address'],
            "pubkey": item['pubkey']
        })

    return resp


def get_balances_table(request, notary=None, coin=None):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    coin = helper.get_or_none(request, "coin", coin)
    notary = helper.get_or_none(request, "notary", notary)
    address = helper.get_or_none(request, "address")

    if not season and not coin and not notary and not address:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'coin', 'notary', 'address']"
        }
    data = query.get_balances_data(season, server, coin, notary, address)
    data = data.values()

    serializer = serializers.balancesSerializer(data, many=True)

    return serializer.data


def get_coin_social_table(request):
    coin = helper.get_or_none(request, "coin")
    season = helper.get_or_none(request, "season")

    data = query.get_coin_social_data(coin, season)
    data = data.order_by('coin').values()

    serializer = serializers.coinSocialSerializer(data, many=True)
    return serializer.data


def get_last_mined_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    name = helper.get_or_none(request, "name")
    address = helper.get_or_none(request, "address")

    if not season and not name and not address:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'name', 'address']"
        }

    data = query.get_mined_data(season, name, address)
    data = data.order_by('season', 'name')
    data = data.values("season", "name", "address")


    data = data.annotate(Max("block_time"), Max("block_height"))

    resp = []
    # name num sum max last
    for item in data:
        season = item['season']
        name = item['name']
        address = item['address']
        last_mined_block = item['block_height__max']
        last_mined_blocktime = item['block_time__max']
        if name != address:
            resp.append({
                "name": name,
                "address": address,
                "last_mined_block": last_mined_block,
                "last_mined_blocktime": last_mined_blocktime,
                "season": season
            })

    return resp


def get_notary_last_ntx_table(request, notary=None):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    coin = helper.get_or_none(request, "coin")
    notary = helper.get_or_none(request, "notary", notary)

    if not notary and not coin:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['notary', 'coin']"
        }

    data = query.get_notary_last_ntx_data(season, server, notary, coin)
    data = data.order_by('season', 'server', 'notary', 'coin').values()

    return data


# 
def get_notary_ntx_24hr_table_data(request, notary=None):
    season = helper.get_or_none(request, "season", SEASON)
    notary = helper.get_or_none(request, "notary", notary)

    if not notary or not season:
        return {
            "error": "You need to specify at least both of the following filter parameters: ['notary', 'season']"
        }
    min_blocktime = int(time.time() - SINCE_INTERVALS['day'])
    data = query.get_notarised_data(season=season, notary=notary, min_blocktime=min_blocktime)
    data = list(data.order_by('coin').values())
    return data


# TODO: Handle where coin not notarised
def get_notary_ntx_season_table_data(request, notary=None):
    season = helper.get_or_none(request, "season", SEASON)
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
        last_ntx = get_notary_last_ntx_table(request, notary)
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
    season = helper.get_or_none(request, "season", SEASON)
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
    season = helper.get_or_none(request, "season", SEASON)
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


def get_notarised_24hrs_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    epoch = helper.get_or_none(request, "epoch")
    coin = helper.get_or_none(request, "coin")
    notary = helper.get_or_none(request, "notary")
    address = helper.get_or_none(request, "address")

    if not season or (not coin and not notary):
        return {
            "error": "You need to specify the following filter parameters: ['season'] and at least one of ['notary','coin']"
        }
    day_ago = int(time.time()) - SINCE_INTERVALS['day']
    data = query.get_notarised_data(
        season, server, epoch, coin, notary, address).filter(block_time__gt=str(day_ago))
    data = data.values()

    serializer = serializers.notarisedSerializer(data, many=True)

    return serializer.data


def get_coin_last_ntx_table(request, coin=None):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
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
    season = helper.get_or_none(request, "season", SEASON)
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
            "time_stamp": item['time_stamp']
        })

    return resp


def get_server_ntx_season_table(request, server=None):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server", server)
    data = query.get_notary_ntx_season_data(season, notary)
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
            "time_stamp": item['time_stamp']
        })

    return resp


def get_coin_ntx_season_table(request, coin=None):
    season = helper.get_or_none(request, "season", SEASON)
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
                "time_stamp": item['time_stamp']
            })

    return resp


def get_notary_ntx_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    epoch = helper.get_or_none(request, "epoch")
    coin = helper.get_or_none(request, "coin")
    notary = helper.get_or_none(request, "notary")

    if not season or not coin or not notary:
        return {
            "error": "You need to specify all of the following filter parameters: ['season', 'coin', 'notary']"
        }
    data = query.get_notarised_data(
        season, server, epoch, coin, notary).order_by('-block_time')
    data = data.values('txid', 'coin', 'block_height',
                       'block_time', 'ac_ntx_height', 'score_value')

    serializer = serializers.notary_ntxSerializer(data, many=True)

    return serializer.data


def get_notarised_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    epoch = helper.get_or_none(request, "epoch")
    coin = helper.get_or_none(request, "coin")
    notary = helper.get_or_none(request, "notary")
    address = helper.get_or_none(request, "address")

    if not season or not server or not coin or not notary:
        return {
            "error": "You need to specify all of the following filter parameters: ['season', 'server', 'coin', 'notary']"
        }
    data = query.get_notarised_data(
        season, server, epoch, coin, notary, address).order_by('-block_time')
    data = data.values()

    serializer = serializers.notarisedSerializer(data, many=True)

    return serializer.data


def get_notarised_tenure_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    coin = helper.get_or_none(request, "coin")

    data = query.get_notarised_tenure_data(season, server, coin)
    data = data.order_by('season', 'server', 'coin').values()

    serializer = serializers.notarisedTenureSerializer(data, many=True)

    return serializer.data


def get_scoring_epochs_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    epoch = helper.get_or_none(request, "epoch")
    coin = helper.get_or_none(request, "coin")
    timestamp = helper.get_or_none(request, "timestamp")

    if not season and not coin and not timestamp:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'coin', 'timestamp']"
        }

    data = query.get_scoring_epochs_data(
        season, server, coin, epoch, timestamp)
    data = data.order_by('season', 'server', 'epoch').values()

    resp = []

    for item in data:
        if item['epoch'].find("_") > -1:
            epoch_id = item['epoch'].split("_")[1]
        else:
            epoch_id = epoch

        if epoch_id not in ["Unofficial", None]:
            
            if item['epoch_end'] > time.time():
                duration = time.time() - item['epoch_start']
            else:
                duration = item['epoch_end'] - item['epoch_start']

            resp.append({
                "season": item['season'],
                "server": item['server'],
                "epoch": epoch_id,
                "epoch_start": dt.fromtimestamp(item['epoch_start']),
                "epoch_end": dt.fromtimestamp(item['epoch_end']),
                "epoch_start_timestamp": item['epoch_start'],
                "epoch_end_timestamp": item['epoch_end'],
                "duration": duration,
                "start_event": item['start_event'],
                "end_event": item['end_event'],
                "epoch_coins": item['epoch_coins'],
                "num_epoch_coins": len(item['epoch_coins']),
                "score_per_ntx": item['score_per_ntx']
            })
    return resp


# UPDATE PENDING
def get_notary_epoch_scores_table(request, notary=None):
    season = helper.get_or_none(request, "season", SEASON)
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
        'server_ntx_count_pct', 'server_ntx_score_pct', 'time_stamp']
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
    season = helper.get_or_none(request, "season", SEASON)
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


def tablize_notarised(resp):
    table_resp = []

    for i in resp:
        table_resp.append({
            "coin": i["coin"],
            "block_height": i["block_height"],
            "ac_ntx_height": i["ac_ntx_height"],
            "txid": i["txid"],
            "notaries": i["notaries"],
            "opret": i["opret"],
            "block_time": i["block_time"]
        })
    return table_resp
