#!/usr/bin/env python3
import time
import csv
from django.views.generic import View
from django.http import HttpResponse
import kmd_ntx_api.serializers as serializers
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_helper as helper

def mined_csv(request):
    season = helper.get_page_season(request)
    name = helper.get_or_none(request, "name")
    address = helper.get_or_none(request, "address")

    min_block = helper.get_or_none(request, "min_block")
    max_block = helper.get_or_none(request, "max_block")
    min_blocktime = helper.get_or_none(request, "min_blocktime")
    max_blocktime = helper.get_or_none(request, "max_blocktime")

    fn_suffix = '_'.join([i for i in [name, address, season] if i])
    data = query.get_mined_data(season, name, address, min_block, max_block, min_blocktime, max_blocktime)
    data = data.order_by('-block_time').values()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="KMD_mining_{fn_suffix}.csv"'
    serializer = serializers.minedSerializer(data, many=True)
    header = serializers.minedSerializer.Meta.fields
    
    writer = csv.DictWriter(response, fieldnames=header)
    writer.writeheader()
    for row in serializer.data:
        writer.writerow(row)
    
    return response
