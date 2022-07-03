#!/usr/bin/env python3

from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.serializers as serializers

def get_notarised_date(season=None, server=None, coin=None, notary=None, last_24hrs=True):
    if last_24hrs:
        day_ago = int(time.time()) - SINCE_INTERVALS['day']
    else:
        # TODO: apply rounding to day
        day_ago = int(time.time()) - SINCE_INTERVALS['day']
    return query.get_notarised_data(season, server, None, coin, notary).filter(block_time__gt=str(day_ago)).order_by('-block_time')


def get_ntx_tenure_table(request):
    tenure_data = query.get_notarised_tenure_data().values()
    data = []
    for item in tenure_data:
        start_time = item["official_start_block_time"]
        end_time = item["official_end_block_time"]
        now = time.time()
        if end_time > now:
            end_time = now
        ntx_days = (end_time - start_time) / 86400
        item.update({
            "ntx_days": ntx_days
        })
        data.append(item)
    return data


############################### Notarised Table ###############################


def get_notarised_rows(request, last_24hrs=True):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    epoch = helper.get_or_none(request, "epoch")
    coin = helper.get_or_none(request, "coin")
    notary = helper.get_or_none(request, "notary")
    address = helper.get_or_none(request, "address")
    txid = helper.get_or_none(request, "txid")
    min_blocktime = helper.get_or_none(request, "min_blocktime")
    max_blocktime = helper.get_or_none(request, "max_blocktime")

    if last_24hrs:
        min_blocktime = int(time.time() - SINCE_INTERVALS['day']) 

    data = query.get_notarised_data(season=season, server=server, txid=txid,
                                    epoch=epoch, coin=coin, notary=notary,
                                    address=address, min_blocktime=min_blocktime,
                                    max_blocktime=max_blocktime)
    if data.count() > 5000:
        return {"error": "too many results, try another filter..."}
    data = data.order_by('coin', '-block_time').values()
    serializer = serializers.notarisedSerializer(data, many=True)
    return serializer.data


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
