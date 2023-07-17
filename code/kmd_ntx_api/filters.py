#!/usr/bin/env python3
from django_filters.rest_framework import FilterSet, NumberFilter, CharFilter
from kmd_ntx_api.models import *
from kmd_ntx_api.serializers import *


## Custom Filter Sets

class minedFilter(FilterSet):
    min_block = NumberFilter(field_name="block_height", lookup_expr='gte')
    max_block = NumberFilter(field_name="block_height", lookup_expr='lte')
    min_blocktime = NumberFilter(field_name="block_time", lookup_expr='gte')
    max_blocktime = NumberFilter(field_name="block_time", lookup_expr='lte')

    class Meta:
        model = mined
        fields = minedSerializer.Meta.fields + ['min_block', 'max_block', 'min_blocktime', 'max_blocktime']


class notarisedFilter(FilterSet):
    min_block = NumberFilter(field_name="block_height", lookup_expr='gte')
    max_block = NumberFilter(field_name="block_height", lookup_expr='lte')
    min_ac_block = NumberFilter(field_name="ac_ntx_height", lookup_expr='gte')
    max_ac_block = NumberFilter(field_name="ac_ntx_height", lookup_expr='lte')
    min_blocktime = NumberFilter(field_name="block_time", lookup_expr='gte')
    max_blocktime = NumberFilter(field_name="block_time", lookup_expr='lte')
    notary = CharFilter(field_name="notaries", lookup_expr='contains')
    address = CharFilter(field_name="notary_addresses", lookup_expr='contains')
    exclude_epoch = CharFilter(field_name="epoch", lookup_expr='contains', exclude=True)

    class Meta:
        model = notarised
        fields = notarisedSerializer.Meta.fields[:]
        fields.remove("notaries")
        fields.remove("notary_addresses")
        fields += ['min_block', 'max_block', 'min_ac_block',
                  'max_ac_block', 'min_blocktime', 'max_blocktime', 
                  'notary', 'address', 'exclude_epoch']


class notarisedTenureFilter(FilterSet):
    gte_official_start = NumberFilter(field_name="official_start_block_time", lookup_expr='gte')
    lte_official_start = NumberFilter(field_name="official_start_block_time", lookup_expr='lte')
    gte_official_end = NumberFilter(field_name="official_end_block_time", lookup_expr='gte')
    lte_official_end = NumberFilter(field_name="official_end_block_time", lookup_expr='lte')

    class Meta:
        model = notarised_tenure
        fields = notarisedTenureSerializer.Meta.fields + ['gte_official_start', 'lte_official_start',
                   'gte_official_end', 'lte_official_end']


class swapsFilter(FilterSet):
    from_time = NumberFilter(field_name="timestamp", lookup_expr='gte')
    to_time = NumberFilter(field_name="timestamp", lookup_expr='lte')
    class Meta:
        model = swaps

        fields = swapsSerializerPub.Meta.fields + ["from_time", "to_time"]


class swapsFailedFilter(FilterSet):
    from_time = NumberFilter(field_name="timestamp", lookup_expr='gte')
    to_time = NumberFilter(field_name="timestamp", lookup_expr='lte')
    class Meta:
        model = swaps_failed
        fields = swapsFailedSerializerPub.Meta.fields + ["from_time", "to_time"]


class rewardsFilter(FilterSet):
    min_block = NumberFilter(field_name="block_height", lookup_expr='gte')
    max_block = NumberFilter(field_name="block_height", lookup_expr='lte')
    min_blocktime = NumberFilter(field_name="block_time", lookup_expr='gte')
    max_blocktime = NumberFilter(field_name="block_time", lookup_expr='lte')
    min_reward = NumberFilter(field_name="rewards_value", lookup_expr='gte')
    max_reward = NumberFilter(field_name="rewards_value", lookup_expr='lte')

    class Meta:
        model = rewards_tx
        fields = rewardsTxSerializer.Meta.fields[:]
        fields += ["min_block", "max_block", "min_blocktime", "max_blocktime",
                   "min_reward", "max_reward"]


class seednodeVersionStatsFilter(FilterSet):
    min_score = NumberFilter(field_name="score", lookup_expr='gte')
    max_score = NumberFilter(field_name="score", lookup_expr='lte')

    class Meta:
        model = seednode_version_stats
        fields = seednodeVersionStatsSerializer.Meta.fields + ['min_score', 'max_score']
