from django.contrib.auth.models import User, Group
from kmd_ntx_api.models import *
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class AddressesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = addresses
        fields = ['notary_id', 'notary', 'address', 'chain',
                  'pubkey', 'season', 'node']

class CoinsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = coins
        fields = ['chain', 'coins_info', 'electrums', 'electrums_ssl',
                  'explorers', 'dpow', 'dpow_active', 'mm2_compatible']

class RewardsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = rewards
        fields = ['address', 'notary', 'utxo_count', 'eligible_utxo_count',
                  'oldest_utxo_block', 'balance', 'rewards', 'update_time']

class BalancesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = balances
        fields = ['notary', 'chain', 'balance', 'address',
                  'update_time', 'season', 'node']

class LastNotarisedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = last_notarised
        fields = ['notary', 'chain', 'txid',
                  'block_height', 'block_time', 'season']

class LastBtcNotarisedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = last_btc_notarised
        fields = ['notary', 'txid', 'block_height', 'block_time', 'season']

class MinedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = mined
        fields = ['block_height', 'block_time', 'block_datetime',
                  'value', 'address', 'name', 'txid', 'season']

class MinedCountSeasonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = mined_count_season
        fields = ['notary', 'blocks_mined', 'sum_value_mined',
                  'max_value_mined', 'last_mined_block',
                  'last_mined_blocktime', 'time_stamp', 
                  'season']

class MinedCountDailySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = mined_count_daily
        fields = ['mined_date', 'notary', 'blocks_mined', 'sum_value_mined',
                  'time_stamp', 'time_stamp']

class NotarisedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised
        fields = ['txid', 'chain', 'block_height', 'block_time',
                  'block_datetime', 'block_hash', 'ac_ntx_blockhash',
                  'ac_ntx_height', 'opret', 'notaries', 'season']

class NotarisedCountSeasonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_count_season
        fields = ['notary', 'btc_count', 'antara_count', 'third_party_count',
                  'other_count', 'total_ntx_count', 'chain_ntx_counts',
                  'chain_ntx_pct', 'time_stamp', 'season']

class NotarisedChainSeasonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_chain_season
        fields = ['chain', 'ntx_count', 'block_height', 'kmd_ntx_blockhash',
                  'kmd_ntx_txid', 'kmd_ntx_blocktime', 'opret',
                  'ac_ntx_blockhash', 'ac_ntx_height', 'ac_block_height',
                  'ntx_lag', 'season']

class NotarisedCountDailySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_count_daily
        fields = ['notarised_date', 'notary', 'btc_count', 'antara_count',
                  'third_party_count', 'other_count', 'total_ntx_count',
                  'chain_ntx_counts', 'chain_ntx_pct', 'time_stamp', 
                  'season', 'notarised_date']

class NotarisedChainDailySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_chain_daily
        fields = ['notarised_date', 'chain', 'ntx_count']

class NNSocialSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = nn_social
        fields = ['notary', 'twitter', 'youtube', 'discord', 'telegram',
                  'github', 'keybase', 'website', 'icon', 'season']

class decodeOpRetSerializer(serializers.Serializer):
    OP_RETURN = serializers.CharField(
        max_length=1000,
        style={
              'base_template': 'textarea.html',
              'placeholder': 'OP_RETURN',
              'autofocus': True
        },
        required=True
    )
    chain = serializers.CharField()
    notarised_block = serializers.IntegerField()
    notarised_blockhash = serializers.CharField()
    class Meta:
        fields = ['OP_RETURN', 'chain',
                  'notarised_block',
                  'notarised_blockhash']

        