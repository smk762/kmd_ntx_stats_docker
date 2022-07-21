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

