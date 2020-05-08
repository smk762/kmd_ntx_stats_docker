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
        fields = ['notary_id', 'notary_name', 'address', 'chain', 'pubkey', 'season']

class CoinsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = coins
        fields = ['chain', 'coins_info', 'electrums', 'electrums_ssl', 'explorers', 'dpow']

class RewardsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = rewards
        fields = ['address', 'notary', 'utxo_count', 'eligible_utxo_count',
                  'oldest_utxo_block', 'balance', 'rewards', 'update_time']

class BalancesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = balances
        fields = ['notary', 'chain', 'balance', 'address', 'update_time']

class MinedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = mined
        fields = ['block', 'block_time', 'value', 'address', 'name', 'txid', 'season']

class MinedCountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = mined_count
        fields = ['notary', 'blocks_mined', 'sum_value_mined',
                  'max_value_mined', 'last_mined_block',
                  'last_mined_blocktime', 'time_stamp', 'time_stamp',
                  'season']

class ntxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised
        fields = ['txid', 'chain', 'block_ht', 'block_time', 'block_hash',
                  'prev_block_hash', 'prev_block_ht', 'opret', 'notaries']

class ntxCountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_count
        fields = ['notary', 'btc_count', 'antara_count', 'third_party_count',
                  'other_count', 'total_ntx_count', 'chain_ntx_counts',
                  'chain_ntx_pct', 'time_stamp', 'season']


class ntxChainCountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_chain
        fields = ['chain', 'ntx_count', 'kmd_ntx_height', 'kmd_ntx_blockhash',
                  'kmd_ntx_txid', 'lastnotarization', 'opret', 'ac_ntx_block_hash',
                  'ac_ntx_height', 'ac_block_height', 'ntx_lag']

class decodeOpRetSerializer(serializers.Serializer):
    OP_RETURN = serializers.CharField(max_length=1000,
                                        style={
                                                'base_template': 'textarea.html',
                                                'placeholder': 'OP_RETURN',
                                                'autofocus': True
                                            },
                                        required=True)
    chain = serializers.CharField()
    prevblock = serializers.IntegerField()
    prevhash = serializers.CharField()
    class Meta:
        fields = ['OP_RETURN', 'chain', 'prevblock', 'prevhash']

        