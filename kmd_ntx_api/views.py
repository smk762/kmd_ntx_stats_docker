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
from django.core.serializers import json

from kmd_ntx_api.serializers import *
from kmd_ntx_api.models import *
from kmd_ntx_api.helper_lib import *
from kmd_ntx_api.info_lib import *
from kmd_ntx_api.query_lib import *

json_serializer = json.Serializer()

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

logger = logging.getLogger("mylogger")


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
    filterset_fields = ['notary', 'chain', 'season']
    ordering_fields = ['season', 'notary', 'chain']
    ordering = ['season', 'notary', 'chain']

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
    season = get_season(int(time.time()))
    notaries_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')

    context = {
        "sidebar_links":get_sidebar_links(notaries_list ,coins_data),
        "eco_data_link":get_eco_data_link(),
        "nn_health":get_nn_health()
    }
    if notary_name:
        notary_addresses = addresses.objects.filter(notary=notary_name, season=season) \
                           .order_by('chain').values('chain','address')

        coins_data = coins.objects.filter(dpow_active=1).values('chain','dpow')
        balances_data = balances.objects.filter(
                                        season=season, notary=notary_name
                                    ).order_by(
                                        '-season','notary', 'chain', 'balance'
                                    ).values()
        coin_notariser_ranks = get_coin_notariser_ranks(season)
        region = get_notary_region(notary_name)
        notary_ntx_counts = coin_notariser_ranks[region][notary_name]
        season_nn_chain_ntx_data = get_season_nn_chain_ntx_data(season)
        notarisation_scores = get_notarisation_scores(season, coin_notariser_ranks)
        region_score_stats = get_region_score_stats(notarisation_scores)
        region_notarisation_scores = notarisation_scores[region]
        notary_score = notarisation_scores[region][notary_name]['score']
        rank = get_region_rank(region_notarisation_scores, notary_score)
        notary_balances_graph_data = get_notary_balances_graph_data(coins_data, balances_data)
        notary_balances_table_data = get_notary_balances_table_data(coins_data, balances_data)
        

        context.update({
            "explorers":get_dpow_explorers(),
            "nn_social":get_nn_social(notary_name),
            "ntx_summary":get_nn_ntx_summary(notary_name),
            "season_nn_chain_ntx_data":season_nn_chain_ntx_data,
            "rank":rank,
            "notary_name":notary_name,
            "notary_balances_graph_data":notary_balances_graph_data,
            "notary_balances_table_data":notary_balances_table_data,
            "region_score_stats":region_score_stats,
            #"notary_ntx_counts":notary_ntx_counts,
            "mining_summary":get_nn_mining_summary(notary_name),
            "notary_addresses":notary_addresses
        })
        return render(request, 'notary_profile.html', context)
    else:
        context.update({
            "nn_social":get_nn_social(),
            "nn_info":get_nn_info()
        })
        return render(request, 'notary_profile_index.html', context)

def coin_profile_view(request, chain=None):
    # contains summary for a specific dPoW coin.
    # Ntx daily / season (and score)
    # low balances
    # addresses for each node / chain
    # Social info
    # Bio
    season = get_season(int(time.time()))
    notaries_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')

    context = {
        "sidebar_links":get_sidebar_links(notaries_list, coins_data)
    }
    if chain:
        balance_data = balances.objects.filter(chain=chain, season=season) \
                                   .order_by('notary') \
                                   .values('notary','address', 'balance')

        max_tick = 0
        for item in balance_data:
            if item['balance'] > max_tick:
                max_tick = float(item['balance'])
        if max_tick > 0:
            10**(int(round(np.log10(max_tick))))
        else:
            max_tick = 10
        coin_notariser_ranks = get_coin_notariser_ranks(season)
        top_region_notarisers = get_top_region_notarisers(coin_notariser_ranks)
        if chain == "KMD":
            top_coin_notarisers = get_top_coin_notarisers(top_region_notarisers, "BTC")
            chain_ntx_summary = get_coin_ntx_summary("BTC")
        else:
            top_coin_notarisers = get_top_coin_notarisers(top_region_notarisers, chain)
            chain_ntx_summary = get_coin_ntx_summary(chain)
        season_chain_ntx_data = get_season_chain_ntx_data(season)

        context.update({
            "chain":chain,
            "explorers":get_dpow_explorers(),
            "eco_data_link":get_eco_data_link(),
            "max_tick": max_tick,
            "coin_social": get_coin_social(chain),
            "chain_ntx_summary": chain_ntx_summary,
            "top_coin_notarisers":top_coin_notarisers
        })            

        return render(request, 'coin_profile.html', context)
    else:
        context.update({ 
            "coin_social": get_coin_social(),
            "coin_info":get_coin_info()
        })
        return render(request, 'coin_profile_index.html', context)

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
            if chain in chain_list:
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
                if chain in chain_list:
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
    return render(request, 'funding.html', context)


def mining_24hrs(request):
    season = get_season(int(time.time()))
    notary_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    mined_24hrs = mined.objects.filter(
        block_time__gt=str(int(time.time()-24*60*60))
        ).values()

    context = {
        "sidebar_links":get_sidebar_links(notary_list ,coins_data),
        "eco_data_link":get_eco_data_link(),
        "mined_24hrs":mined_24hrs,
        "explorers":get_dpow_explorers(),
        "season":season.replace("_"," ")
    }
    return render(request, 'mining_24hrs.html', context)

def mining_24hrs_api(request):
    mined_24hrs = mined.objects.filter(
        block_time__gt=str(int(time.time()-24*60*60))
        ).values()
    serializer = MinedSerializer(mined_24hrs, many=True)
    return JsonResponse({'data': serializer.data})

def nn_mined_4hrs_api(request):
    mined_4hrs = mined.objects.filter(
        block_time__gt=str(int(time.time()-4*60*60))
        ).values()
    serializer = MinedSerializer(mined_4hrs, many=True)
    season = get_season(int(time.time()))
    notary_list = get_notary_list(season)
    mined_counts_4hr = {}
    for nn in notary_list:
        mined_counts_4hr.update({nn:0})
    for item in serializer.data:
        nn = item['name']
        if nn in mined_counts_4hr:
            count = mined_counts_4hr[nn] + 1
            mined_counts_4hr.update({nn:count})
        else:
            mined_counts_4hr.update({nn:1})
    return JsonResponse(mined_counts_4hr)

def nn_mined_last_api(request):
    season = get_season(int(time.time()))
    mined_last = mined.objects.filter(season=season).values("name").annotate(Max("block_time"),Max("block_height"))
    notary_list = get_notary_list(season)
    mined_last_dict = {}
    for item in mined_last:
        if item["name"] in notary_list:
            mined_last_dict.update({
                item["name"]:{
                    "blocktime":item["block_time__max"],
                    "blockheight":item["block_height__max"],
                }
            })

    return JsonResponse(mined_last_dict)

def ntx_24hrs(request):
    season = get_season(int(time.time()))
    notary_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    ntx_24hrs = notarised.objects.filter(
        block_time__gt=str(int(time.time()-24*60*60))
        ).values()

    context = {
        "sidebar_links":get_sidebar_links(notary_list ,coins_data),
        "eco_data_link":get_eco_data_link(),
        "ntx_24hrs":ntx_24hrs,
        "explorers":get_dpow_explorers(),
        "season":season.replace("_"," ")
    }
    return render(request, 'ntx_24hrs.html', context)

def ntx_24hrs_api(request):
    ntx_24hrs = notarised.objects.filter(
        block_time__gt=str(int(time.time()-24*60*60))
        ).values()
    serializer = NotarisedSerializer(ntx_24hrs, many=True)
    return JsonResponse({'data': serializer.data})

def mining_overview(request):
    season = get_season(int(time.time()))
    notary_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')

    context = {
        "sidebar_links":get_sidebar_links(notary_list ,coins_data),
        "eco_data_link":get_eco_data_link(),
        "explorers":get_dpow_explorers(),
        "season":season.replace("_"," ")
    }
    return render(request, 'mining_overview.html', context)

def btc_ntx(request):
    season = get_season(int(time.time()))
    notary_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    btc_ntx = notarised_btc.objects.filter(
                            season=season).values()

    context = {
        "sidebar_links":get_sidebar_links(notary_list ,coins_data),
        "eco_data_link":get_eco_data_link(),
        "explorers":get_dpow_explorers(),
        "btc_ntx":btc_ntx,
        "season":season.replace("_"," ")
    }
    return render(request, 'btc_ntx.html', context)

def btc_ntx_all(request):
    season = get_season(int(time.time()))
    notary_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    btc_ntx = notarised.objects.filter(
                            season=season, chain='BTC').values()

    context = {
        "sidebar_links":get_sidebar_links(notary_list ,coins_data),
        "eco_data_link":get_eco_data_link(),
        "explorers":get_dpow_explorers(),
        "btc_ntx":btc_ntx,
        "season":season.replace("_"," ")
    }
    return render(request, 'btc_ntx_all.html', context)

def ntx_scoreboard_24hrs(request):
    season = get_season(int(time.time()))
    notaries_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')

    context = {
        "daily_stats_sorted":get_daily_stats_sorted(notaries_list),
        "sidebar_links":get_sidebar_links(notaries_list ,coins_data),
        "eco_data_link":get_eco_data_link(),
        "nn_social":get_nn_social()
    }
    return render(request, 'ntx_scoreboard_24hrs.html', context)

def ntx_scoreboard(request):
    season = get_season(int(time.time()))
    notary_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
 
    coin_notariser_ranks = get_coin_notariser_ranks(season)
    notarisation_scores = get_notarisation_scores(season, coin_notariser_ranks)
    region_score_stats = get_region_score_stats(notarisation_scores)

    context = {
        "sidebar_links":get_sidebar_links(notary_list ,coins_data),
        "eco_data_link":get_eco_data_link(),
        "notarisation_scores":notarisation_scores,
        "region_score_stats":region_score_stats,
        "nn_social":get_nn_social()
    }
    return render(request, 'ntx_scoreboard.html', context)


def ntx_tenure(request):
    season = get_season(int(time.time()))
    notary_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    tenure_data = notarised_tenure.objects.all().values()
    context = {
        "sidebar_links":get_sidebar_links(notary_list ,coins_data),
        "tenure_data":tenure_data,
        "eco_data_link":get_eco_data_link()
    }
    return render(request, 'ntx_tenure.html', context)
        
def chains_last_ntx(request):
    season = get_season(int(time.time()))
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    notary_list = get_notary_list(season)

    season_chain_ntx_data = get_season_chain_ntx_data(season)

    context = {
        "sidebar_links":get_sidebar_links(notary_list ,coins_data),
        "eco_data_link":get_eco_data_link(),
        "explorers":get_dpow_explorers(),
        "season_chain_ntx_data":season_chain_ntx_data
    }

    return render(request, 'last_notarised.html', context)

def funds_sent(request):
    season = get_season(int(time.time()))
    notaries_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    funding_data = funding_transactions.objects.filter(season=season).values()
    funding_totals = get_funding_totals(funding_data)

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
    context = get_chain_sync_data(request)
    notaries_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')

    context.update({
        "sidebar_links":get_sidebar_links(notaries_list, coins_data),
        "explorers":get_dpow_explorers(),
        "eco_data_link":get_eco_data_link()
        })
    return render(request, 'chain_sync.html', context)

def faucet(request):
    season = get_season(int(time.time()))
    notaries_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    context = {
        "sidebar_links":get_sidebar_links(notaries_list, coins_data),
        "explorers":get_dpow_explorers(),
        "eco_data_link":get_eco_data_link()
        }
    if request.method == 'POST':
        if 'coin' in request.POST:
            coin = request.POST['coin'].strip()
        if 'address' in request.POST:
            address = request.POST['address'].strip()
        url = f'https://faucet.komodo.live/faucet/{coin}/{address}'
        print(url)
        r = requests.get(url)
        try:
            resp = r.json()
            messages.success(request, resp["Result"]["Message"])
            if resp['Status'] == "Success":
                context.update({"result":coin+"_success"})
            elif resp['Status'] == "Error":
                context.update({"result":"disqualified"})
            else:
                context.update({"result":"fail"})
        except Exception as e:
            messages.success(request, f"Something went wrong... {e}")
            context.update({"result":"fail"})

    return render(request, 'faucet.html', context)


## DASHBOARD        
def dash_view(request, dash_name=None):
    # Table Views
    context = {}
    gets = ''
    html = 'dash_index.html'
    season = get_season(int(time.time()))
    notaries_list = get_notary_list(season)
    coins_list = get_dpow_coins_list()
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
    else:
        coin_notariser_ranks = get_coin_notariser_ranks(season)
        ntx_24hr = notarised.objects.filter(
            block_time__gt=str(int(time.time()-24*60*60))
            ).count()
        try:
            mined_24hr = mined.objects.filter(
                block_time__gt=str(int(time.time()-24*60*60))
                ).values('season').annotate(sum_mined=Sum('value'))[0]['sum_mined']
        except:
            # no records returned
            mined_24hr = 0
        biggest_block = mined.objects.filter(season=season).order_by('-value').first()
        notarisation_scores = get_notarisation_scores(season, coin_notariser_ranks)
        region_score_stats = get_region_score_stats(notarisation_scores)
        context.update({
            "ntx_24hr":ntx_24hr,
            "mined_24hr":mined_24hr,
            "biggest_block":biggest_block,
            "notarisation_scores":notarisation_scores,
            "region_score_stats":region_score_stats,
            "show_ticker":True
        })
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    server_chains = get_server_chains(coins_data)
    context.update({
        "gets":gets,
        "sidebar_links":get_sidebar_links(notaries_list ,coins_data),
        "eco_data_link":get_eco_data_link(),
        "nn_health":get_nn_health(),
        "server_chains":server_chains,
        "coins_list":coins_list,
        "notaries_list":notaries_list,
        "daily_stats_sorted":get_daily_stats_sorted(notaries_list),
        "nn_social":get_nn_social(),

    })
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

        data = get_balances_graph_data(request, filter_kwargs)

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

        data = get_daily_ntx_graph_data(request)

        return Response(data) 


# Notary BTC TXID API Endpoints

def nn_btc_txid(request):
    if 'txid' in request.GET:
        resp = get_btc_txid_single(request.GET['txid'])
    else:
        resp = {"error":"You need to specify a TXID like '/nn_btc_txid?txid=86e23d8415737f1f6a723d1996f3e373e77d7e16a7ae8548b4928eb019237321'"}
    return JsonResponse(resp)

def address_btc_txids(request):
    if 'address' in request.GET and 'category' in request.GET:
        resp = get_btc_txid_address(request.GET['address'], request.GET['category'])
    elif 'address' in request.GET:
        resp = get_btc_txid_address(request.GET['address'])
    else:
        resp = {"error":"You need to specify an ADDRESS like '/address_btc_txids?address=1LtvR7B1zmvqKUeJkuaWYzSK2on8dS4u1h'. Category param is optional, e.g. '/address_btc_txids?address=1LtvR7B1zmvqKUeJkuaWYzSK2on8dS4u1h&category=NTX'"}
    return JsonResponse(resp)

def notary_btc_txids(request):
    if 'notary' in request.GET and 'category' in request.GET:
        resp = get_btc_txid_notary(request.GET['notary'], request.GET['category'])
    elif 'notary' in request.GET:
        resp = get_btc_txid_notary(request.GET['notary'])
    elif 'category' in request.GET:
        resp = get_btc_txid_notary(None, request.GET['category'])
    else:
        resp = {"error":"You need to specify a NOTARY or CATEGORY like '/nn_btc_txid?notary=dragonhound_NA' or '/nn_btc_txid?notary=dragonhound_NA&category=NTX'"}
    return JsonResponse(resp)

def nn_btc_txid_list(request):
    if 'season' in request.GET and 'notary' in request.GET:
        resp = get_btc_txid_list(request.GET['notary'], request.GET['season'])
    elif 'notary' in request.GET:
        resp = get_btc_txid_list(request.GET['notary'])
    elif 'season' in request.GET:
        resp = get_btc_txid_list(None, request.GET['season'])
    else:
        resp = get_btc_txid_list()
    distinct = len(list(set(resp['results'][0])))
    resp.update({"distinct":distinct})
    return JsonResponse(resp)

def nn_btc_txid_other(request):
    resp = get_btc_txid_data("other")
    return JsonResponse(resp)

def nn_btc_txid_ntx(request):
    resp = get_btc_txid_data("NTX")
    return JsonResponse(resp)

def nn_btc_txid_spam(request):
    resp = get_btc_txid_data("SPAM")
    return JsonResponse(resp)

def nn_btc_txid_raw(request):
    resp = get_btc_txid_data()
    return JsonResponse(resp)

def nn_btc_txid_splits(request):
    resp = get_btc_txid_data("splits")
    return JsonResponse(resp)

def split_summary_api(request):
    resp = get_split_stats()
    return JsonResponse(resp)

def split_summary_table(request):
    resp = get_split_stats_table()
    return JsonResponse(resp)

# TESTNET

def api_testnet_raw(request):
    resp = get_api_testnet(request, "raw")
    return JsonResponse(resp)

def api_testnet_raw_24hr(request):
    resp = get_api_testnet(request, "raw_24hr")
    return JsonResponse(resp)

def api_testnet_totals(request):
    resp = get_api_testnet(request, "totals")
    return JsonResponse(resp)


def testnet_ntx_scoreboard(request):
    season = get_season(int(time.time()))
    notary_list = get_notary_list(season)
    coins_data = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
 
    testnet_ntx_counts = get_api_testnet(request, "totals")["results"][0]
    num_notaries = len(testnet_ntx_counts)

    combined_total = 0
    combined_total_24hr = 0
    for notary in testnet_ntx_counts:
        combined_total += testnet_ntx_counts[notary]["Total"]
        combined_total_24hr += testnet_ntx_counts[notary]["24hr_Total"]
    average_score = combined_total/num_notaries
    average_score_24hr = combined_total_24hr/num_notaries

    context = {
        "sidebar_links":get_sidebar_links(notary_list ,coins_data),
        "eco_data_link":get_eco_data_link(),
        "average_score":average_score,
        "average_score_24hr":average_score_24hr,
        "testnet_ntx_counts":testnet_ntx_counts
    }
    return render(request, 'testnet_scoreboard.html', context)

# TOOLS

def api_address_from_pubkey(request):
    resp = get_address_from_pubkey(request)
    return JsonResponse(resp)

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
