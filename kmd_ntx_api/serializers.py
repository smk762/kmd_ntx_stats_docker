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
        fields = ['address', 'notary', 'utxo_count', 'eligible_utxo_count', 'oldest_utxo_block', 'balance', 'rewards', 'update_time']

class BalancesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = balances
        fields = ['notary', 'chain', 'balance', 'address', 'update_time']

class MinedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = mined
        fields = ['block', 'block_time', 'value', 'address', 'name', 'txid']

class ntxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised
        fields = ['txid', 'chain', 'block_ht', 'block_time', 'block_hash', 'prev_block_hash', 'prev_block_ht', 'opret', 'notaries']

class MinedCountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = mined_count
        fields = ['notary', 'season', 'blocks_mined', 'sum_value_mined', 'max_value_mined', 'last_mined_blocktime', 'last_mined_block', 'time_stamp']

class ntxCountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_count
        fields = ['notary', 'btc_count', 'antara_count', 'third_party_count', 'total_ntx_count', 'json_count', 'time_stamp']

class decodeOpRetSerializer(serializers.Serializer):
    OP_RETURN = serializers.CharField(max_length=1000, style={'base_template': 'textarea.html', 'placeholder': 'OP_RETURN', 'autofocus': True}, required=True)
    chain = serializers.CharField()
    prevblock = serializers.IntegerField()
    prevhash = serializers.CharField()
    class Meta:
        fields = ['OP_RETURN', 'chain', 'prevblock', 'prevhash']

        