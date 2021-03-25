#!/usr/bin/env python3
from django_filters.rest_framework import FilterSet, NumberFilter
from kmd_ntx_api.models import *

## Custom Filter Sets

class minedFilter(FilterSet):
    min_block = NumberFilter(field_name="block_height", lookup_expr='gte')
    max_block = NumberFilter(field_name="block_height", lookup_expr='lte')
    min_blocktime = NumberFilter(field_name="block_time", lookup_expr='gte')
    max_blocktime = NumberFilter(field_name="block_time", lookup_expr='lte')

    class Meta:
        model = mined
        fields = ['min_block', 'max_block', 'min_blocktime', 'max_blocktime', 
                  'block_height', 'block_time', 'block_datetime', 
                  'value', 'address', 'name', 'txid', 'season']

class ntxFilter(FilterSet):
    min_block = NumberFilter(field_name="block_height", lookup_expr='gte')
    max_block = NumberFilter(field_name="block_height", lookup_expr='lte')
    min_ac_block = NumberFilter(field_name="ac_ntx_height", lookup_expr='gte')
    max_ac_block = NumberFilter(field_name="ac_ntx_height", lookup_expr='lte')
    min_blocktime = NumberFilter(field_name="block_time", lookup_expr='gte')
    max_blocktime = NumberFilter(field_name="block_time", lookup_expr='lte')

    class Meta:
        model = notarised
        fields = ['min_block', 'max_block', 'min_ac_block',
                  'max_ac_block', 'min_blocktime', 'max_blocktime', 
                  'txid', 'chain', 'block_height', 'block_time',
                  'block_datetime', 'block_hash', 'ac_ntx_blockhash',
                  'ac_ntx_height', 'opret', 'season', 'btc_validated']