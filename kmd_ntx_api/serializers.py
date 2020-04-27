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

class MinedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = mined
        fields = ['block', 'value', 'address', 'name']

class ntxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised
        fields = ['block_ht', 'chain', 'txid', 'notaries']

class MinedCountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = mined_count
        fields = ['notary', 'sum_mined', 'max_mined', 'timestamp']

class ntxCountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_count
        fields = ['notary', 'btc_count', 'antara_count', 'third_party_count', 'total_ntx_count', 'timestamp']

class ntxChainsCountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_count
        fields = ['notary', 'json_count', 'timestamp']