#!/usr/bin/env python3
from django.db.models import Count, Sum, Avg

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

def get_notary_fee_efficiency(season = 'Season_7', datatables=True):    
    data = query.get_nn_ltc_tx_data(season=season)
    consolidate_data = data.filter(category='Consolidate').values('notary', 'txid').annotate(sum_fees=Avg('fees'))
    split_data = data.filter(category='Split').values('notary').annotate(sum_fees=Sum('fees'))
    ntx_data = data.filter(category='NTX').values('notary').annotate(sum_ntx=Count('fees'), sum_fees=Sum('fees'))

    resp = {}
    for i in ntx_data:
        resp.update({
            i["notary"]: {
                'coin': "LTC",
                'ntx_count': i["sum_ntx"],
                'ntx_fees': i["sum_fees"],
            }
        })


    for i in split_data:
        resp[i["notary"]].update({
            'split_fees': i["sum_fees"]
        })
        
    for i in consolidate_data:
        if i["notary"] not in resp:
            resp.update({
                i["notary"]: {}
            })
        if 'consolidate_fees' not in resp[i["notary"]]:
            resp[i["notary"]].update({
                'consolidate_fees': 0
            })

        resp[i["notary"]]['consolidate_fees'] += i["sum_fees"]

    table_resp = []
    for notary in resp:
        if 'ntx_count' not in resp[notary]:
            resp[notary].update({
                'ntx_count': 0
            })
        if 'ntx_fees' not in resp[notary]:
            resp[notary].update({
                'ntx_fees': 0
            })
        if 'consolidate_fees' not in resp[notary]:
            resp[notary].update({
                'consolidate_fees': 0
            })
        if 'split_fees' not in resp[notary]:
            resp[notary].update({
                'split_fees': 0
            })


        sum_fees = sum([resp[notary]['ntx_fees'], resp[notary]['consolidate_fees'], resp[notary]['split_fees']])
        item = {
            'notary': notary,
            'split_fees': resp[notary]['split_fees']/100000000,
            'ntx_fees': resp[notary]['ntx_fees']/100000000,
            'consolidate_fees': resp[notary]['consolidate_fees']/100000000,
            "sum_fees": sum_fees/100000000,
            "ntx_count": resp[notary]["ntx_count"],
            "efficiency": helper.safe_div(sum_fees/30000, resp[notary]["ntx_count"])
        }
        resp[notary].update(item)
        table_resp.append(item)
    
    if datatables:
        return table_resp
    return resp


    # Get sum ntx per notary
    # Get sum fees per notary

