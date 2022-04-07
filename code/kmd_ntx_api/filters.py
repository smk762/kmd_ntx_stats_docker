#!/usr/bin/env python3
from django_filters.rest_framework import FilterSet, NumberFilter, CharFilter
from kmd_ntx_api.lib_const import *
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

class notarisedFilter(FilterSet):
    min_block = NumberFilter(field_name="block_height", lookup_expr='gte')
    max_block = NumberFilter(field_name="block_height", lookup_expr='lte')
    min_ac_block = NumberFilter(field_name="ac_ntx_height", lookup_expr='gte')
    max_ac_block = NumberFilter(field_name="ac_ntx_height", lookup_expr='lte')
    min_blocktime = NumberFilter(field_name="block_time", lookup_expr='gte')
    max_blocktime = NumberFilter(field_name="block_time", lookup_expr='lte')
    notary = CharFilter(field_name="notaries", lookup_expr='contains')

    class Meta:
        model = notarised
        fields = ['min_block', 'max_block', 'min_ac_block',
                  'max_ac_block', 'min_blocktime', 'max_blocktime', 
                  'txid', 'chain', 'block_height', 'block_time',
                  'block_datetime', 'block_hash', 'ac_ntx_blockhash',
                  'ac_ntx_height', 'opret', 'season', 'server', 'epoch',
                  'scored']

class notarisedTenureFilter(FilterSet):
    gte_official_start = NumberFilter(field_name="official_start_block_time", lookup_expr='gte')
    lte_official_start = NumberFilter(field_name="official_start_block_time", lookup_expr='lte')
    gte_official_end = NumberFilter(field_name="official_end_block_time", lookup_expr='gte')
    lte_official_end = NumberFilter(field_name="official_end_block_time", lookup_expr='lte')

    class Meta:
        model = notarised
        fields = ['gte_official_start', 'lte_official_start',
                  'gte_official_end', 'lte_official_end', 'season', 'chain']

class swapsFilter(FilterSet):
    from_time = NumberFilter(field_name="time_stamp", lookup_expr='gte')
    to_time = NumberFilter(field_name="time_stamp", lookup_expr='lte')
    class Meta:
        model = swaps
        fields = ["uuid", "started_at", "taker_coin", "taker_amount", \
                 "taker_gui", "taker_version", "taker_pubkey", "maker_coin", \
                 "maker_amount", "maker_gui", "maker_version", "maker_pubkey"]


class swapsFailedFilter(FilterSet):
    from_time = NumberFilter(field_name="time_stamp", lookup_expr='gte')
    to_time = NumberFilter(field_name="time_stamp", lookup_expr='lte')
    class Meta:
        model = swaps_failed
        fields = ["uuid", "started_at", "taker_coin", "taker_amount", 
                 "taker_error_type", "taker_error_msg", "taker_gui", 
                 "taker_version", "taker_pubkey", "maker_coin", 
                 "maker_amount", "maker_error_type", "maker_error_msg",
                 "maker_gui", "maker_version", "maker_pubkey"]

class rewardsFilter(FilterSet):
    min_block = NumberFilter(field_name="block_height", lookup_expr='gte')
    max_block = NumberFilter(field_name="block_height", lookup_expr='lte')
    min_blocktime = NumberFilter(field_name="block_time", lookup_expr='gte')
    max_blocktime = NumberFilter(field_name="block_time", lookup_expr='lte')
    min_reward = NumberFilter(field_name="rewards_value", lookup_expr='gte')
    max_reward = NumberFilter(field_name="rewards_value", lookup_expr='lte')
    vin_address = CharFilter(field_name="input_addresses", lookup_expr='contains')
    vout_address = CharFilter(field_name="output_addresses", lookup_expr='contains')

    class Meta:
        model = rewards_tx
        fields = [
            "txid", "block_height", "block_time", "rewards_value"
        ]
