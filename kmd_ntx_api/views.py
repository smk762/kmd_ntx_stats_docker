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
        "nn_social":get_nn_social()
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