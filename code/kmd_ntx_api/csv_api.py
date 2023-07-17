#!/usr/bin/env python3
import csv
from django.http import HttpResponse
from kmd_ntx_api.helper import get_or_none
from kmd_ntx_api.notary_seasons import get_page_season
from kmd_ntx_api.query import get_mined_data
from kmd_ntx_api.serializers import minedSerializer

def mined_csv(request):
    season = get_page_season(request)
    name = get_or_none(request, "name")
    address = get_or_none(request, "address")

    min_block = get_or_none(request, "min_block")
    max_block = get_or_none(request, "max_block")
    min_blocktime = get_or_none(request, "min_blocktime")
    max_blocktime = get_or_none(request, "max_blocktime")

    fn_suffix = '_'.join([i for i in [name, address, season] if i])
    data = get_mined_data(season, name, address, min_block, max_block, min_blocktime, max_blocktime)
    data = data.order_by('-block_time').values()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="KMD_mining_{fn_suffix}.csv"'
    serializer = minedSerializer(data, many=True)
    header = minedSerializer.Meta.fields
    
    writer = csv.DictWriter(response, fieldnames=header)
    writer.writeheader()
    for row in serializer.data:
        writer.writerow(row)
    
    return response
