#!/usr/bin/env python3
import os
import sys
import time
import numpy as np
import logging
import logging.handlers
import datetime
from datetime import datetime as dt

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, \
                                          NumberFilter
from rest_framework import filters, generics, viewsets, permissions, \
                           authentication, mixins
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView

from kmd_ntx_api.serializers import *
from kmd_ntx_api.models import *
from kmd_ntx_api.helper_lib import *
from kmd_ntx_api.info_lib import *
from kmd_ntx_api.query_lib import *

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

logger = logging.getLogger("mylogger")

noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'AYA']

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
                  'ac_ntx_height', 'opret', 'season']

## Source data endpoints

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class MinedViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing mining table data
    """
    queryset = mined.objects.all()
    serializer_class = MinedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = minedFilter
    #filterset_fields =  ['block_height', 'block_time', 'block_datetime',
    #                     'value', 'address', 'name', 'txid', 'season']
    ordering_fields = ['block_height', 'address', 'season', 'name']
    ordering = ['-block_height']

class ntxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised.objects.all()
    serializer_class = NotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ntxFilter
    ordering_fields = ['block_time', 'chain']
    ordering = ['-block_time', 'chain']

class MinedCountSeasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing mining table data
    """
    queryset = mined_count_season.objects.all()
    serializer_class = MinedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary', 'season']
    ordering_fields = ['block_height']
    ordering = ['notary']

class MinedCountDayViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing mining table data
    """
    queryset = mined_count_daily.objects.all()
    serializer_class = MinedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['mined_date', 'notary']
    ordering_fields = ['mined_date','notary']
    ordering = ['-mined_date','notary']

class ntxCountSeasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised_count_season.objects.all()
    serializer_class = NotarisedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['season', 'notary']
    ordering_fields = ['season', 'notary']
    ordering = ['-season', 'notary']

class ntxChainSeasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised_chain_season.objects.all()
    serializer_class = NotarisedChainSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['chain', 'season']
    ordering_fields = ['block_height']
    ordering = ['-block_height']

class ntxCountDateViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised_count_daily.objects.all()
    serializer_class = NotarisedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notarised_date', 'notary']
    ordering_fields = ['notarised_date', 'notary']
    ordering = ['-notarised_date', 'notary']

class ntxChainDateViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised_chain_daily.objects.all()
    serializer_class = NotarisedChainDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notarised_date', 'chain']
    ordering_fields = ['notarised_date', 'chain']
    ordering = ['-notarised_date', 'chain']

class lastNtxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = last_notarised.objects.all()
    serializer_class = LastNotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary', 'chain']
    ordering_fields = ['notary', 'chain']
    ordering = ['notary', 'chain']

class lastBtcNtxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = last_btc_notarised.objects.all()
    serializer_class = LastBtcNotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary']
    ordering_fields = ['notary']
    ordering = ['notary']

class coinsViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = coins.objects.all()
    serializer_class = CoinsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['chain']
    ordering_fields = ['chain']
    ordering = ['chain']

class addressesViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = addresses.objects.all()
    serializer_class = AddressesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['chain', 'notary', 'season']
    ordering_fields = ['chain', 'notary', 'season']
    ordering = ['-season', 'notary', 'chain']

class nn_socialViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing Node Operator social links
    """
    queryset = nn_social.objects.all()
    serializer_class = NNSocialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary', 'season']
    ordering_fields = ['season', 'notary']
    ordering = ['-season', 'notary']

class balancesViewSet(viewsets.ModelViewSet):
    """
    API endpoint Notary balances 
    """
    queryset = balances.objects.all()
    serializer_class = BalancesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['chain', 'notary', 'season', 'node']
    ordering_fields = ['chain', 'notary', 'season']
    ordering = ['-season', 'notary', 'chain']

class rewardsViewSet(viewsets.ModelViewSet):
    """
    API pending KMD rewards for notaries
    """
    queryset = rewards.objects.all()
    serializer_class = RewardsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary','address']
    ordering_fields = ['notary','address']
    ordering = ['notary']

# simple_lists
class notary_nodes(viewsets.ViewSet):
    """
    API endpoint listing notary names for each season
    """
    serializer_class = AddressesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['season']
    ordering_fields = ['season', 'notary']
    ordering = ['-season', 'notary']

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        season = get_season(int(time.time()))
        notaries_list = get_notary_list(season)
        api_resp = wrap_api(notaries_list)

        return Response(api_resp)

# Auto filterable views

class coins_filter(viewsets.ViewSet):
    """
    API endpoint showing coininfo from coins and dpow repositories
    """
    serializer_class = CoinsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_coins_data(request)
        return Response(api_resp)

class addresses_filter(viewsets.ViewSet):
    """
    Returns Notary Node addresses, nested by Name > Season > Chain \n
    Default filter returns current NN Season \n

    """
    serializer_class = AddressesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        api_resp = get_addresses_data(request)
        return Response(api_resp)

class balances_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node balances
    """
    serializer_class = BalancesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_balances_data(request)
        return Response(api_resp)

class mined_count_season_filter(viewsets.ViewSet):
    """
    API endpoint showing mined blocks by notary/address (minimum 10 blocks mined)
    """
    serializer_class = MinedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_mined_count_season_data(request)
        return Response(api_resp)

class mined_count_date_filter(viewsets.ViewSet):
    """
    API endpoint showing mined blocks by notary/address (minimum 10 blocks mined) \n
    Use a filter such as below - \n
    http://notary.earth:8762/daily/mined_count/?mined_date=2020-05-11&notary=node-9_EU \n
    Defaults to todays date.
    """
    serializer_class = MinedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        api_resp = get_mined_count_daily_data(request)
        return Response(api_resp)

class notarised_chain_season_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = NotarisedChainSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_notarised_chain_season_data(request)
        return Response(api_resp)

class notarised_count_season_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = NotarisedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_notarised_count_season_data(request)
        return Response(api_resp)

class notarised_chain_date_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks. \n
    Use a filter such as below \n
    http://notary.earth:8762/daily/notarised_chain/?notarised_date=2019-07-27 \n
    Defaults to filtering by todays date \n
    """
    serializer_class = NotarisedChainDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_notarised_chain_daily_data(request)
        return Response(api_resp)

class notarised_count_date_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = NotarisedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_notarised_count_date_data(request)
        return Response(api_resp)

class rewards_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = RewardsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_rewards_data(request)
        return Response(api_resp)

def chain_sync_api(request):
    r = requests.get('http://138.201.207.24/show_sync_node_data')
    try:
        return JsonResponse(r.json())
    except:
        return JsonResponse({})

# Tool views
class decode_op_return(viewsets.ViewSet):
    """
    Decodes notarization OP_RETURN strings.
    USAGE: decode_opret/?OP_RETURN=<OP_RETURN>
    """    
    # renderer_classes = [TemplateHTMLRenderer]
    serializer_class = decodeOpRetSerializer
    # template_name = 'rest_framework/horizontal/input.html' 
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        Returns decoded notarisation information from OP_RETURN strings
        """
        if 'OP_RETURN' in request.GET:

            decoded = decode_opret(request.GET['OP_RETURN'])
        else:
            decoded = {}
        return Response(decoded)

class explorers(viewsets.ViewSet):
    """
    Returns explorers sourced from coins repo
    """    
    serializer_class = ExplorersSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        resp = {}
        coins_data = coins.objects.all().values('chain','explorers')
        for item in coins_data:
            explorers = item['explorers']
            if len(explorers) > 0:
                chains = item['chains']
                resp.update({chain:explorers})
        return Response(resp)

# test time filters for daily notary summary (ntx and mining)

# Slow, review. crash err 247. add paginate func?
# Not exposed to API
class mined_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks. 
    Use filters or be patient, this is a big dataset.
    """
    serializer_class = MinedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        api_resp = get_mined_data(request)
        return Response(api_resp)

class notarised_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = NotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        api_resp = get_notarised_data(request)
        return Response(api_resp)

# PROFILES
def notary_profile_view(request, notary_name=None):
    # contains summary for a specific notary node.
    # Mining Daily / season
    # Ntx daily / season (and score)
    # low balances
    # addresses for each node / chain
    # pending KMD rewards
    # Social info
    # Bio
    # Seasons served
    # Other project involvement
    if notary_name:
        season = get_season(int(time.time()))
        notary_addresses = addresses.objects.filter(notary=notary_name, season=season) \
                           .order_by('chain').values('chain','address')
        coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
        season = get_season(int(time.time()))
        notary_list = get_notary_list(season)

        context = {
            "sidebar_links":get_sidebar_links(notary_list ,coins_data),
            "eco_data_link":get_eco_data_link(),
            "explorers":get_dpow_explorers(),
            "nn_social":get_nn_social(notary_name),
            "nn_health":get_nn_health(),
            "ntx_summary":get_nn_ntx_summary(notary_name),
            "notary_name":notary_name,
            "mining_summary":get_nn_mining_summary(notary_name),
            "notary_addresses":notary_addresses
        }
        return render(request, 'notary_profile.html', context)
    else:
        redirect('dash_view')

def coin_profile_view(request, chain=None):
    # contains summary for a specific dPoW coin.
    # Ntx daily / season (and score)
    # low balances
    # addresses for each node / chain
    # Social info
    # Bio
    if chain:
        season = get_season(int(time.time()))
        balance_data = balances.objects.filter(chain=chain, season=season) \
                                       .order_by('notary') \
                                       .values('notary','address', 'balance')
        max_tick = 0
        for item in balance_data:
            if item['balance'] > max_tick:
                max_tick = float(item['balance'])
        notaries_list = get_notary_list(season)
        coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
        context = {
            "sidebar_links":get_sidebar_links(notaries_list, coins_data),
            "explorers":get_dpow_explorers(),
            "eco_data_link":get_eco_data_link(),
            "coin_social": get_coin_social(chain),
            "nn_health":get_nn_health(),
            "chain_ntx_summary":get_coin_ntx_summary(chain),
            "chain":chain,
            "max_tick": 10**(int(round(np.log10(max_tick))))
        }
        return render(request, 'coin_profile.html', context)
    else:
        redirect('dash_view')

def funding(request):
    # add extraa views for per chain or per notary
    low_nn_balances = get_low_nn_balances()
    last_balances_update = day_hr_min_sec(int(time.time()) - low_nn_balances['time'])
    human_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())

    chain_low_balance_notary_counts = {}
    notary_low_balance_chain_counts = {}

    ok_balance_notaries = []
    ok_balance_chains = []
    no_data_chains = list(low_nn_balances['sources']['failed'].keys())

    low_balance_data = low_nn_balances['low_balances']
    low_nn_balances['low_balance_chains'].sort()
    low_nn_balances['low_balance_notaries'].sort()

    season = get_season(int(time.time()))
    notaries_list = get_notary_list(season)

    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    chain_list = get_dpow_coins_list()

    num_chains = len(chain_list)
    num_notaries = len(notaries_list)
    num_addresses = num_notaries*num_chains

    # count addresses with low / sufficient balance
    num_low_balance_addresses = 0
    for notary in low_balance_data:
        for chain in low_balance_data[notary]:
            num_low_balance_addresses += 1
    num_ok_balance_addresses = num_addresses-num_low_balance_addresses            

    for chain in chain_list:
        chain_low_balance_notary_counts.update({chain:0})
        if chain not in low_nn_balances['low_balance_chains'] and chain not in no_data_chains:
            ok_balance_chains.append(chain)

    for notary in notaries_list:
        notary_low_balance_chain_counts.update({notary:0})
        if notary in low_balance_data:
            notary_low_balance_chain_counts.update({notary:len(low_balance_data[notary])})
            for chain in low_balance_data[notary]:
                if chain == 'KMD_3P':
                    val = chain_low_balance_notary_counts["KMD"] + 1
                    chain_low_balance_notary_counts.update({"KMD":val})
                else:
                    val = chain_low_balance_notary_counts[chain] + 1
                    chain_low_balance_notary_counts.update({chain:val})
        if notary not in low_nn_balances['low_balance_notaries']:
            ok_balance_notaries.append(notary)

    chain_balance_graph_data = prepare_chain_balance_graph_data(notary_low_balance_chain_counts)
    notary_balance_graph_data = prepare_notary_balance_graph_data(chain_low_balance_notary_counts)

    chains_funded_pct = round(len(ok_balance_chains)/len(chain_list)*100,2)
    notaries_funded_pct = round(len(ok_balance_notaries)/len(notaries_list)*100,2)
    addresses_funded_pct = round((num_addresses-num_low_balance_addresses)/num_addresses*100,2)

    context = {
        "chains_funded_pct":chains_funded_pct,
        "notaries_funded_pct":notaries_funded_pct,
        "addresses_funded_pct":addresses_funded_pct,
        "num_ok_balance_addresses":num_ok_balance_addresses,
        "num_low_balance_addresses":num_low_balance_addresses,
        "num_addresses":num_addresses,
        "chain_balance_graph_data":chain_balance_graph_data,
        "notary_balance_graph_data":notary_balance_graph_data,
        "chain_low_balance_notary_counts":chain_low_balance_notary_counts,
        "notary_low_balance_chain_counts":notary_low_balance_chain_counts,
        "low_balance_notaries":low_nn_balances['low_balance_notaries'],
        "low_balance_chains":low_nn_balances['low_balance_chains'],
        "ok_balance_notaries":ok_balance_notaries,
        "ok_balance_chains":ok_balance_chains,
        "no_data_chains":no_data_chains,
        "chain_list":chain_list,
        "notaries_list":notaries_list,
        "last_balances_update":last_balances_update,
        "sidebar_links":get_sidebar_links(notaries_list ,coins_data),
        "explorers":get_dpow_explorers(),
        "low_nn_balances":low_nn_balances['low_balances'],
        "notary_funding":get_notary_funding(),
        "bot_balance_deltas":get_bot_balance_deltas(),
        "eco_data_link":get_eco_data_link(),
        "nn_health":get_nn_health()
    }
    return render(request, 'notary_funding.html', context)

def coin_funding(request):
    pass

def notary_funding(request):
    pass

def funds_sent(request):
    season = get_season(int(time.time()))
    notaries_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    funding_data = funding_transactions.objects.filter(season=season).values()

    funding_totals = {"fees":{}}
    now = int(time.time())
    for item in funding_data:
        tx_time = day_hr_min_sec(now - item['block_time'])
        item.update({"time": tx_time})
        if item["notary"] not in ["unknown", "funding bot"]:
            if item["notary"] not in funding_totals:
                funding_totals.update({item["notary"]:{}})

            if item["chain"] not in funding_totals[item["notary"]]:
                funding_totals[item["notary"]].update({item["chain"]:-item["amount"]})
            else:
                val = funding_totals[item["notary"]][item["chain"]]-item["amount"]
                funding_totals[item["notary"]].update({item["chain"]:val})

            if item["chain"] not in funding_totals["fees"]:
                funding_totals["fees"].update({item["chain"]:-item["fee"]})
            else:
                val = funding_totals["fees"][item["chain"]]-item["fee"]
                funding_totals["fees"].update({item["chain"]:val})

    context = {
        "sidebar_links":get_sidebar_links(notaries_list, coins_data),
        "explorers":get_dpow_explorers(),
        "eco_data_link":get_eco_data_link(),
        "funding_data":funding_data,
        "funding_totals":funding_totals,
    }  
    return render(request, 'funding_sent.html', context)

def chain_sync(request):
    season = get_season(int(time.time()))
    notaries_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    context = {
        "sidebar_links":get_sidebar_links(notaries_list, coins_data),
        "explorers":get_dpow_explorers(),
        "eco_data_link":get_eco_data_link(),
    }
    r = requests.get('http://138.201.207.24/show_sync_node_data')
    try:
        chain_sync_data = r.json()
        sync_data_keys = list(chain_sync_data.keys())
        chain_count = 0
        sync_count = 0
        for chain in sync_data_keys:
            if chain == 'last_updated':
                last_data_update = day_hr_min_sec(
                    int(time.time()) - int(chain_sync_data['last_updated'])
                )
                chain_sync_data.update({
                    "last_data_update": last_data_update
                })
            elif chain.find('last') == -1:
                chain_count += 1
                if "last_sync_blockhash" in chain_sync_data[chain]:
                    if chain_sync_data[chain]["last_sync_blockhash"] == chain_sync_data[chain]["last_sync_dexhash"]:
                        sync_count += 1
                if 'last_sync_timestamp' in chain_sync_data[chain] :
                    last_sync_update = day_hr_min_sec(
                        int(time.time()) - int(chain_sync_data[chain]['last_sync_timestamp'])
                    )
                else:
                    last_sync_update = "-"
                chain_sync_data[chain].update({
                    "last_sync_update": last_sync_update
                })
        sync_pct = round(sync_count/chain_count*100,3)
        context.update({
            "chain_sync_data":chain_sync_data,
            "sync_count":sync_count,
            "sync_pct":sync_pct,
            "chain_count":chain_count
        })
    except Exception as e:
        print(e)
        messages.error(request, 'Sync Node API not Responding!')    
    return render(request, 'chain_sync.html', context)

## DASHBOARD        
def dash_view(request, dash_name=None):
    # Table Views
    gets = ''
    html = 'dash_index.html'
    if dash_name:
        if dash_name.find('table') != -1:
            if dash_name == 'balances_table':
                html = 'tables/balances.html'
            elif dash_name == 'addresses_table':
                html = 'tables/addresses.html'
            elif dash_name == 'rewards_table':
                html = 'tables/rewards.html'
            elif dash_name == 'mining_table':
                html = 'tables/mining.html'
            elif dash_name == 'mining_season_table':
                html = 'tables/mining_season.html'
            elif dash_name == 'mining_daily_table':
                html = 'tables/mining_daily.html'
            elif dash_name == 'ntx_table':
                html = 'tables/ntx.html'
            elif dash_name == 'ntx_chain_season_table':
                html = 'tables/ntx_chain_season.html'
            elif dash_name == 'ntx_chain_daily_table':
                html = 'tables/ntx_chain_daily.html'
            elif dash_name == 'ntx_node_season_table':
                html = 'tables/ntx_node_season.html'
            elif dash_name == 'ntx_node_daily_table':
                html = 'tables/ntx_node_daily.html'
        # Table Views
        elif dash_name.find('graph') != -1:
            getlist = []
            for k in request.GET:
                getlist.append(k+"="+request.GET[k])
            gets = '&'.join(getlist)
            if dash_name == 'balances_graph':
                html = 'graphs/balances.html'
            if dash_name == 'daily_ntx_graph':
                html = 'graphs/daily_ntx_graph.html'
            if dash_name == 'daily_mining_graph':
                html = 'graphs/mined.html'
            if dash_name == 'season_ntx_graph':
                html = 'graphs/daily_ntx_graph.html'
            if dash_name == 'season_mining_graph':
                html = 'graphs/daily_ntx_graph.html'
    season = get_season(int(time.time()))
    notaries_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    context = {
        "gets":gets,
        "sidebar_links":get_sidebar_links(notaries_list ,coins_data),
        "eco_data_link":get_eco_data_link(),
        "nn_health":get_nn_health(),
        "nn_social":get_nn_social()
    }
    return render(request, html, context)

## DASHBOARD GRAPHS

class balances_graph(viewsets.ViewSet): 
    authentication_classes = [] 
    permission_classes = [] 
    serializer_class = BalancesSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['chain', 'notary', 'season']
    ordering_fields = ['chain', 'notary', 'season']
    ordering = ['-season', 'notary', 'chain']

    def create(self, validated_data):
        return Task(id=None, **validated_data)
   
    def get(self, request, format = None): 
        season = get_season(int(time.time()))
        filter_kwargs = {'season':season}
        for field in BalancesSerializer.Meta.fields:
            val = request.query_params.get(field, None)
            if val is not None:
                filter_kwargs.update({field:val}) 

        if 'chain' in request.GET:
            filter_kwargs.update({'chain':request.GET['chain']})
        elif 'notary' in request.GET:
            filter_kwargs.update({'notary':request.GET['notary']})
        else:
            filter_kwargs.update({'chain':'BTC'})

        data = balances.objects.filter(**filter_kwargs).values('notary', 'chain', 'balance')
        notary_list = []                                                                          
        chain_list = []
        balances_dict = {}
        for item in data:
            if item['notary'] not in notary_list:
                notary_list.append(item['notary'])
            if item['chain'] not in chain_list:
                chain_list.append(item['chain'])
            if item['notary'] not in balances_dict:
                balances_dict.update({item['notary']:{}})
            if item['chain'] not in balances_dict[item['notary']]:
                balances_dict[item['notary']].update({item['chain']:item['balance']})
            else:
                bal = balances_dict[item['notary']][item['chain']] + item['balance']
                balances_dict[item['notary']].update({item['chain']:bal})

        chain_list.sort()
        notary_list.sort()
        notary_list = region_sort(notary_list)

        bg_color = []
        border_color = []

        third_chains = []
        main_chains = []
        coins_data = coins.objects.filter(dpow_active=1).values('chain','dpow')
        for item in coins_data:
            if item['dpow']['server'] == "dPoW-mainnet":
                main_chains.append(item['chain'])
            if item['dpow']['server'] == "dPoW-3P":
                third_chains.append(item['chain'])

        if len(chain_list) == 1:
            chain = chain_list[0]
            labels = notary_list
            chartLabel = chain+ " Notary Balances"
            for notary in notary_list:
                if notary.endswith("_AR"):
                    bg_color.append('#DC0333')
                elif notary.endswith("_EU"):
                    bg_color.append('#2FEA8B')
                elif notary.endswith("_NA"):
                    bg_color.append('#B541EA')
                elif notary.endswith("_SH"):
                    bg_color.append('#00E2FF')
                else:
                    bg_color.append('#F7931A')
                border_color.append('#000')
        else:
            notary = notary_list[0]
            labels = chain_list
            chartLabel = notary+ " Notary Balances"
            for chain in chain_list:
                if chain in third_chains:
                    bg_color.append('#b541ea')
                elif chain in main_chains:
                    bg_color.append('#2fea8b')
                else:
                    bg_color.append('#f7931a')
                border_color.append('#000')

        chartdata = []
        for notary in notary_list:
            for chain in chain_list:
                chartdata.append(balances_dict[notary][chain])
        
        data = { 
            "labels":labels, 
            "chartLabel":chartLabel, 
            "chartdata":chartdata, 
            "bg_color":bg_color, 
            "border_color":border_color, 
        } 
        return Response(data) 

class daily_ntx_graph(viewsets.ViewSet): 
    queryset = notarised_count_daily.objects.all()
    serializer_class = NotarisedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notarised_date', 'notary']
    ordering_fields = ['notarised_date', 'notary']
    ordering = ['-notarised_date', 'notary']

    def create(self, validated_data):
        return Task(id=None, **validated_data)
   
    def get(self, request, format = None): 
        season = get_season(int(time.time()))
        filter_kwargs = {'season':season}
        for field in NotarisedCountDailySerializer.Meta.fields:
            val = request.query_params.get(field, None)
            if val is not None:
                filter_kwargs.update({field:val}) 
        
        notary_list = []                                                                         
        chain_list = []
        ntx_dict = {}

        if 'notarised_date' in request.GET:
            filter_kwargs.update({'notarised_date':request.GET['notarised_date']})
        else:
            today = datetime.date.today()
            filter_kwargs.update({'notarised_date':today})
        if 'notary' in request.GET:
            filter_kwargs.update({'notary':request.GET['notary']})
        elif 'chain' not in request.GET:
            filter_kwargs.update({'notary':'alien_AR'})

        data = notarised_count_daily.objects.filter(**filter_kwargs) \
                    .values('notary', 'notarised_date','chain_ntx_counts')

        for item in data:
            if item['notary'] not in notary_list:
                notary_list.append(item['notary'])
            chain_list += list(item['chain_ntx_counts'].keys())
            ntx_dict.update({item['notary']:item['chain_ntx_counts']})

        if 'chain' in request.GET:
            chain_list = [request.GET['chain']]
        else:
            chain_list = list(set(chain_list))
            chain_list.sort()

        notary_list.sort()
        notary_list = region_sort(notary_list)
        bg_color = []
        border_color = []
        third_chains = []
        main_chains = []
        coins_data = coins.objects.filter(dpow_active=1).values('chain','dpow')
        for item in coins_data:
            if item['dpow']['server'] == "dPoW-mainnet":
                main_chains.append(item['chain'])
            if item['dpow']['server'] == "dPoW-3P":
                third_chains.append(item['chain'])

        if len(chain_list) == 1:
            chain = chain_list[0]
            labels = notary_list
            chartLabel = chain+ " Notarisations"
            for notary in notary_list:
                if notary.endswith("_AR"):
                    bg_color.append('#DC0333')
                elif notary.endswith("_EU"):
                    bg_color.append('#2FEA8B')
                elif notary.endswith("_NA"):
                    bg_color.append('#B541EA')
                elif notary.endswith("_SH"):
                    bg_color.append('#00E2FF')
                else:
                    bg_color.append('#F7931A')
                border_color.append('#000')
        else:
            notary = notary_list[0]
            labels = chain_list
            chartLabel = notary+ " Notarisations"
            for chain in chain_list:
                if chain in third_chains:
                    bg_color.append('#00E2FF')
                elif chain in main_chains:
                    bg_color.append('#2FEA8B')
                else:
                    bg_color.append('#B541EA')
                border_color.append('#000')

        chartdata = []
        for notary in notary_list:
            for chain in chain_list:
                print("---------------")
                print("notary: "+notary)
                print("chain: "+chain)
                if chain in ntx_dict[notary]:
                    chartdata.append(ntx_dict[notary][chain])
                else:
                    chartdata.append(0)
        

        data = { 
            "labels":labels, 
            "chartLabel":chartLabel, 
            "chartdata":chartdata, 
            "bg_color":bg_color, 
            "border_color":border_color, 
        } 
        return Response(data) 

# sync lag graph
# daily ntx category stack graph
# monitor and detect suspicious NN fund exits. To other NN addr is ok, ntx is ok.
# date range mining/ntx for nn/chain

# NOTARY Profile:
# time since ntx graph

# COINS PROFILE (tabbed? changes ajax sources?)
# top section:
# -
# graphs: daily/season chain ntx, notary chain balances
# tables: daily/season chain ntx, notary chain balances