#!/usr/bin/env python3
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_ntx as ntx
import kmd_ntx_api.serializers as serializers


def notarised_date_api(request):
    season = helper.get_or_none(request, "season")
    server = helper.get_or_none(request, "server")
    coin = helper.get_or_none(request, "coin")
    notary = helper.get_or_none(request, "notary")
    last_24hrs = helper.get_or_none(request, "last_24hrs", False) == 'true'
    data = ntx.get_notarised_date(season, server, coin, notary, last_24hrs)
    serializer = serializers.notarisedSerializer(data, many=True)
    filters = ['season', 'server', 'coin', 'notary']
    return helper.json_resp(serializer.data, filters)



