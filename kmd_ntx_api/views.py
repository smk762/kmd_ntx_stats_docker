#!/usr/bin/env python3
import os
import sys
import json
import binascii
import time
import random
import requests
import logging
import logging.handlers
from datetime import datetime as dt
import datetime
from django.db.models import Count, Min, Max, Sum
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django_filters.rest_framework import DjangoFilterBackend
from kmd_ntx_api.serializers import *
from kmd_ntx_api.models import *
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import filters, generics, viewsets, permissions, authentication, mixins
from rest_framework.renderers import TemplateHTMLRenderer
from django_filters import rest_framework as filters

from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet

logger = logging.getLogger("mylogger")

# Need to confirm and fill this in correctly later...
seasons_info = {
    "Season_1": {
            "start_block":1,
            "end_block":1,
            "start_time":1,
            "end_time":1530921600,
            "notaries":[]
        },
    "Season_2": {
            "start_block":1,
            "end_block":1,
            "start_time":1530921600,
            "end_time":1563148799,
            "notaries":[]
        },
    "Season_3": {
            "start_block":1,
            "end_block":1,
            "start_time":1563148800,
            "end_time":1751328000,
            "notaries":[]
        }
}

r = requests.get("https://raw.githubusercontent.com/gcharang/data/master/info/ecosystem.json")
eco_data = r.json()

noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'AYA']

# Queryset manipulation

def get_eco_data_link():
    item = random.choice(eco_data)
    ad = random.choice(item['ads'])
    while ad['frequency'] == "never":
        item = random.choice(eco_data)
        ad = random.choice(item['ads'])
    link = ad['data']['string1']+" <a href="+ad['data']['link']+"> " \
          +ad['data']['anchorText']+"</a> "+ad['data']['string2']
    return link

def get_nn_health():

    coins_data = coins.objects.filter(dpow_active=1).values('chain')
    chains_list = []
    for item in coins_data:
        # ignore BTC, OP RETURN lists ntx to BTC as "KMD"
        if item['chain'] not in chains_list and item['chain'] != 'BTC':
            chains_list.append(item['chain'])

    notaries = addresses.objects.filter(season="Season_3").values('notary')
    notary_list = []
    for item in notaries:
        if item['notary'] not in notary_list:
            notary_list.append(item['notary'])

    timenow = int(time.time())
    day_ago = timenow-60*60*24

    filter_kwargs = {}
    filter_kwargs.update({'block_time__gte':day_ago})  
    filter_kwargs.update({'block_time__lte':timenow})

    ntx_data = notarised.objects.filter(**filter_kwargs)
    ntx_chain_24hr = ntx_data.values('chain') \
                     .annotate(max_ntx_time=Max('block_time'))

    ntx_chains = []
    for item in ntx_chain_24hr:
        ntx_chains.append(item['chain'])
    ntx_chains = list(set(ntx_chains))

    ntx_node_24hr = ntx_data.values('notaries')
    ntx_nodes = []
    for item in ntx_node_24hr:
        ntx_nodes += item['notaries']
    ntx_nodes = list(set(ntx_nodes))


    mining_data = mined.objects.filter(**filter_kwargs) \
                 .values('name') \
                 .annotate(num_mined=Count('name'))
    mining_nodes = []
    for item in mining_data:
        if item['name'] in notary_list:
            mining_nodes.append(item['name'])

    non_mining_nodes = list(set(notary_list)- set(mining_nodes))
    non_ntx_nodes = list(set(notary_list).symmetric_difference(set(ntx_nodes)))
    non_ntx_chains = list(set(chains_list).symmetric_difference(set(ntx_chains)))
    nn_health = {
        "mining_nodes":mining_nodes,
        "non_mining_nodes":non_mining_nodes,
        "mining_nodes_pct":round(len(mining_nodes)/len(notary_list)*100,2),
        "ntx_nodes":ntx_nodes,
        "non_ntx_nodes":non_ntx_nodes,
        "ntx_nodes_pct":round(len(ntx_nodes)/len(notary_list)*100,2),
        "chains_list":chains_list,
        "ntx_chains":ntx_chains,
        "non_ntx_chains":non_ntx_chains,
        "ntx_chains_pct":round(len(ntx_chains)/len(chains_list)*100,2)
    }
    return nn_health

def apply_filters(request, serializer, queryset, table=None):
    filter_kwargs = {}
    for field in serializer.Meta.fields:
        print(field)
        val = request.query_params.get(field, None)
        if val is not None:
            filter_kwargs.update({field:val}) 
    if 'from_block' in request.GET:
        filter_kwargs.update({'block_height__gte':request.GET['from_block']})  
    if 'to_block' in request.GET:
        filter_kwargs.update({'block_height__lte':request.GET['to_block']})  
    if 'from_timestamp' in request.GET:
        filter_kwargs.update({'block_time__gte':request.GET['from_timestamp']})  
    if 'to_timestamp' in request.GET:
        filter_kwargs.update({'block_time__lte':request.GET['to_timestamp']})
    if table in ['daily_mined_count']:
        if 'from_date' in request.GET:
            filter_kwargs.update({'mined_date__gte':request.GET['from_date']})  
        if 'to_date' in request.GET:
            filter_kwargs.update({'mined_date__lte':request.GET['to_date']})          
    if table in ['daily_notarised_chain', 'daily_notarised_count']:
        if 'from_date' in request.GET:
            filter_kwargs.update({'notarised_date__gte':request.GET['from_date']})  
        if 'to_date' in request.GET:
            filter_kwargs.update({'notarised_date__lte':request.GET['to_date']})          
    print(request.GET)  
    print("filter_kwargs: "+str(filter_kwargs))
    if len(filter_kwargs) > 0:
        queryset = queryset.filter(**filter_kwargs)
    return queryset

def paginate_wrap(resp, url, field, prev_value, next_value):
    api_resp = {
        "count":len(resp),
        "next":url+"?"+field+"="+next_value,
        "previous":url+"?"+field+"="+prev_value,
        "results":[resp]
    }
    return api_resp

def wrap_api(resp):
    api_resp = {
        "count":len(resp),
        "results":[resp]
    }
    return api_resp

# OP_RETURN functions
def get_ticker(scriptPubKeyBinary):
    chain = ''
    while len(chain) < 1:
        for i in range(len(scriptPubKeyBinary)):
            if chr(scriptPubKeyBinary[i]).encode() == b'\x00':
                j = i+1
                while j < len(scriptPubKeyBinary)-1:
                    chain += chr(scriptPubKeyBinary[j])
                    j += 1
                    if chr(scriptPubKeyBinary[j]).encode() == b'\x00':
                        break
                break
    if chr(scriptPubKeyBinary[-4])+chr(scriptPubKeyBinary[-3])+chr(scriptPubKeyBinary[-2]) =="KMD":
        chain = "KMD"
    return chain

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def decode_opret(scriptPubKey_asm):   
    ac_ntx_blockhash = lil_endian(scriptPubKey_asm[:64])
    try:
        ac_ntx_height = int(lil_endian(scriptPubKey_asm[64:72]),16) 
    except:
        print(scriptPubKey_asm)
        return {"error":scriptPubKey_asm+ " is invalid and can not be decoded."}
    scriptPubKeyBinary = binascii.unhexlify(scriptPubKey_asm[70:])
    chain = get_ticker(scriptPubKeyBinary)
    if chain.endswith("KMD"):
        chain = "KMD"
    if chain == "KMD":
        btc_txid = lil_endian(scriptPubKey_asm[72:136])
    elif chain not in noMoM:
        # not sure about this bit, need another source to validate the data
        try:
            start = 72+len(chain)*2+4
            end = 72+len(chain)*2+4+64
            MoM_hash = lil_endian(scriptPubKey_asm[start:end])
            MoM_depth = int(lil_endian(scriptPubKey_asm[end:]),16)
        except Exception as e:
            logger.debug(e)
    return { "chain":chain, "notarised_block":ac_ntx_height, "notarised_blockhash":ac_ntx_blockhash }

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

class minedFilter(filters.FilterSet):
    min_block = filters.NumberFilter(field_name="block_height", lookup_expr='gte')
    max_block = filters.NumberFilter(field_name="block_height", lookup_expr='lte')
    min_blocktime = filters.NumberFilter(field_name="block_time", lookup_expr='gte')
    max_blocktime = filters.NumberFilter(field_name="block_time", lookup_expr='lte')

    class Meta:
        model = mined
        fields = ['min_block', 'max_block', 'min_blocktime', 'max_blocktime', 
                  'block_height', 'block_time', 'block_datetime', 
                  'value', 'address', 'name', 'txid', 'season']

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


class ntxFilter(filters.FilterSet):
    min_block = filters.NumberFilter(field_name="block_height", lookup_expr='gte')
    max_block = filters.NumberFilter(field_name="block_height", lookup_expr='lte')
    min_ac_block = filters.NumberFilter(field_name="ac_ntx_height", lookup_expr='gte')
    max_ac_block = filters.NumberFilter(field_name="ac_ntx_height", lookup_expr='lte')
    min_blocktime = filters.NumberFilter(field_name="block_time", lookup_expr='gte')
    max_blocktime = filters.NumberFilter(field_name="block_time", lookup_expr='lte')

    class Meta:
        model = notarised
        fields = ['min_block', 'max_block', 'min_ac_block',
                  'max_ac_block', 'min_blocktime', 'max_blocktime', 
                  'txid', 'chain', 'block_height', 'block_time',
                  'block_datetime', 'block_hash', 'ac_ntx_blockhash',
                  'ac_ntx_height', 'opret', 'season']

class ntxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised.objects.all()
    serializer_class = NotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ntxFilter
    #filterset_fields = ['txid', 'chain', 'block_height', 'block_time', 'block_datetime', 
    #                    'block_hash', 'ac_ntx_blockhash', 'ac_ntx_height',
    #                    'opret', 'season']
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

class balancesViewSet(viewsets.ModelViewSet):
    """
    API endpoint Notary balances 
    """
    queryset = balances.objects.all()
    serializer_class = BalancesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['chain', 'notary', 'season']
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
        Returns decoded notarisation information from OP_RETURN strings
        """
        resp = {}
        data = addresses.objects.all()
        data = apply_filters(request, AddressesSerializer, data) \
               .order_by('season', 'notary') \
               .values('notary', 'season')

        notaries_list = {}
        for item in data:
            if item['season'].find("Season_3") != -1:
                if "Season_3" not in notaries_list:
                    notaries_list["Season_3"] = []
                if item['notary'] not in notaries_list["Season_3"]:
                    notaries_list["Season_3"].append(item['notary'])
            else:
                if item['season'] not in notaries_list:
                    notaries_list[item['season']] = []
                if item['notary'] not in notaries_list[item['season']]:
                    notaries_list[item['season']].append(item['notary'])

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
        resp = {}
        data = coins.objects.all()
        data = apply_filters(request, CoinsSerializer, data) \
                .order_by('chain') \
                .values()
        for item in data:
            resp.update({
                item["chain"]:{
                    "coins_info":item["coins_info"],
                    "dpow":item["dpow"],
                    "explorers":item["explorers"],
                    "electrums":item["electrums"],
                    "electrums_ssl":item["electrums_ssl"],
                    "mm2_compatible":item["mm2_compatible"],
                    "dpow_active":item["dpow_active"]
                },
            })
        api_resp = wrap_api(resp)
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
        resp = {}
        data = addresses.objects.all()
        full_count = data.count()
        data = apply_filters(request, AddressesSerializer, data)
        if data.count() == full_count:
            data = addresses.objects.filter(season='Season_3')
        data = data.order_by('notary','season', 'chain').values()
        for item in data:
            if item["notary"] not in resp: 
                resp.update({item["notary"]:{}})
            if item["season"] not in resp[item["notary"]]:
                resp[item["notary"]].update({
                    item["season"]: {
                        "notary_id":item["notary_id"],
                        "pubkey":item["pubkey"],
                        "addresses":{}
                    }
                })

            if item["chain"] not in resp[item["notary"]][item["season"]]["addresses"]:
                resp[item["notary"]][item["season"]]["addresses"].update({
                    item["chain"]: item['address']
                })
        api_resp = wrap_api(resp)
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
        resp = {}
        data = balances.objects.all()
        data = apply_filters(request, BalancesSerializer, data)
        if len(data) == len(balances.objects.all()):
            data = balances.objects.filter(season='Season_3') 
        data = data.order_by('-season','notary', 'chain', 'balance').values()
        for item in data:
            
            season = item['season']
            if season not in resp:
                resp.update({season:{}})

            notary = item['notary']
            if notary not in resp[season]:
                resp[season].update({notary:{}})

            chain = item['chain']
            if chain not in resp[season][notary]:
                resp[season][notary].update({chain:{}})

            address = item['address']
            balance = item['balance']
            resp[season][notary][chain].update({address:balance})

        api_resp = wrap_api(resp)
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
        resp = {}
        data = mined_count_season.objects.all()
        data = apply_filters(request, MinedCountSeasonSerializer, data)
        if len(data) == len(mined_count_season.objects.all()):
            yesterday = int(time.time()-60*60*24)
            data = mined_count_season.objects.filter(season='Season_3')
        data = data.order_by('season', 'notary').values()

        for item in data:
            blocks_mined = item['blocks_mined']
            if blocks_mined > 10:
                notary = item['notary']
                sum_value_mined = item['sum_value_mined']
                max_value_mined = item['max_value_mined']
                last_mined_block = item['last_mined_block']
                last_mined_blocktime = item['last_mined_blocktime']
                time_stamp = item['time_stamp']
                season = item['season']

                if season not in resp:
                    resp.update({season:{}})

                resp[season].update({
                    notary:{
                        "blocks_mined":blocks_mined,
                        "sum_value_mined":sum_value_mined,
                        "max_value_mined":max_value_mined,
                        "last_mined_block":last_mined_block,
                        "last_mined_blocktime":last_mined_blocktime,
                        "time_stamp":time_stamp
                    }
                })

        api_resp = wrap_api(resp)
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
        resp = {}
        data = mined_count_daily.objects.all()
        data = apply_filters(request, MinedCountDailySerializer, data, 'daily_mined_count')
        # default filter if none set.
        if len(data) == len(mined_count_daily.objects.all()) or len(data) == 0:
            today = datetime.date.today()
            data = mined_count_daily.objects.filter(mined_date=str(today))
        data = data.order_by('mined_date', 'notary').values()

        for item in data:
            blocks_mined = item['blocks_mined']
            notary = item['notary']
            sum_value_mined = item['sum_value_mined']
            time_stamp = item['time_stamp']
            mined_date = str(item['mined_date'])

            if mined_date not in resp:
                resp.update({mined_date:{}})

            resp[mined_date].update({
                notary:{
                    "blocks_mined":blocks_mined,
                    "sum_value_mined":sum_value_mined,
                    "time_stamp":time_stamp
                }
            })
        delta = datetime.timedelta(days=1)
        yesterday = item['mined_date']-delta
        tomorrow = item['mined_date']+delta
        url = request.build_absolute_uri('/mined_stats/daily/')
        api_resp = paginate_wrap(resp, url, "mined_date",
                             str(yesterday), str(tomorrow))
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
        resp = {}
        data = notarised_chain_season.objects.all()
        data = apply_filters(request, NotarisedChainSeasonSerializer, data) \
                .order_by('-season', 'chain') \
                .values()

        for item in data:
            season = item['season']
            chain = item['chain']
            ntx_lag = item['ntx_lag']
            ntx_count = item['ntx_count']
            block_height = item['block_height']
            kmd_ntx_txid = item['kmd_ntx_txid']
            kmd_ntx_blockhash = item['kmd_ntx_blockhash']
            kmd_ntx_blocktime = item['kmd_ntx_blocktime']
            opret = item['opret']
            ac_ntx_blockhash = item['ac_ntx_blockhash']
            ac_ntx_height = item['ac_ntx_height']
            ac_block_height = item['ac_block_height']

            if season not in resp:
                resp.update({season:{}})

            resp[season].update({
                chain:{
                    "ntx_count":ntx_count,
                    "kmd_ntx_height":block_height,
                    "kmd_ntx_blockhash":kmd_ntx_blockhash,
                    "kmd_ntx_txid":kmd_ntx_txid,
                    "kmd_ntx_blocktime":kmd_ntx_blocktime,
                    "ac_ntx_blockhash":ac_ntx_blockhash,
                    "ac_ntx_height":ac_ntx_height,
                    "ac_block_height":ac_block_height,
                    "opret":opret,
                    "ntx_lag":ntx_lag
                }
            })


        api_resp = wrap_api(resp)
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
        resp = {}
        data = notarised_count_season.objects.all()
        data = apply_filters(request, NotarisedCountSeasonSerializer, data)
        # default filter if none set.
        if len(data) == notarised_count_season.objects.count() or len(data) == 0:
            data = notarised_count_season.objects.filter(season='Season_3')

        data = data.order_by('season', 'notary').values()

        for item in data:
            season = item['season']
            notary = item['notary']
            btc_count = item['btc_count']
            antara_count = item['antara_count']
            third_party_count = item['third_party_count']
            other_count = item['other_count']
            total_ntx_count = item['total_ntx_count']
            chain_ntx_counts = item['chain_ntx_counts']
            chain_ntx_pct = item['chain_ntx_pct']
            time_stamp = item['time_stamp']

            if season not in resp:
                resp.update({season:{}})

            resp[season].update({
                notary:{
                    "btc_count":btc_count,
                    "antara_count":antara_count,
                    "third_party_count":third_party_count,
                    "other_count":other_count,
                    "total_ntx_count":total_ntx_count,
                    "time_stamp":time_stamp,
                    "chains":{}
                }
            })
            for chain in chain_ntx_counts:
                resp[season][notary]["chains"].update({
                    chain:{
                        "count":chain_ntx_counts[chain]
                    }
                })
            for chain in chain_ntx_pct:
                resp[season][notary]["chains"][chain].update({
                    "percentage":chain_ntx_pct[chain]
                }),


        api_resp = wrap_api(resp)
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
        resp = {}
        data = notarised_chain_daily.objects.all()
        data = apply_filters(request, NotarisedChainDailySerializer, data, 'daily_notarised_chain')
        # default filter if none set.
        if len(data) == len(notarised_chain_daily.objects.all()):
            today = datetime.date.today()
            data = notarised_chain_daily.objects.filter(notarised_date=str(today))
        data = data.order_by('notarised_date', 'chain').values()
        if len(data) > 0:
            for item in data:
                notarised_date = str(item['notarised_date'])
                chain = item['chain']
                ntx_count = item['ntx_count']

                if notarised_date not in resp:
                    resp.update({notarised_date:{}})

                resp[notarised_date].update({
                    chain:ntx_count
                })


            delta = datetime.timedelta(days=1)
            yesterday = item['notarised_date']-delta
            tomorrow = item['notarised_date']+delta
        else:
            today = datetime.date.today()
            delta = datetime.timedelta(days=1)
            yesterday = today-delta
            tomorrow = today+delta
        url = request.build_absolute_uri('/chain_stats/daily/')
        api_resp = paginate_wrap(resp, url, "notarised_date",
                             str(yesterday), str(tomorrow))
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
        resp = {}
        data = notarised_count_daily.objects.all()
        print("applying filters")
        data = apply_filters(request, NotarisedCountDailySerializer, data, 'daily_notarised_count')
        # default filter if none set.
        if len(data) == len(notarised_count_daily.objects.all()):
            today = datetime.date.today()
            data = notarised_count_daily.objects.filter(notarised_date=today)
        data = data.order_by('notarised_date', 'notary').values()
        if len(data) > 0:
            for item in data:
                notarised_date = str(item['notarised_date'])
                notary = item['notary']
                btc_count = item['btc_count']
                antara_count = item['antara_count']
                third_party_count = item['third_party_count']
                other_count = item['other_count']
                total_ntx_count = item['total_ntx_count']
                chain_ntx_counts = item['chain_ntx_counts']
                chain_ntx_pct = item['chain_ntx_pct']
                time_stamp = item['time_stamp']

                if notarised_date not in resp:
                    resp.update({notarised_date:{}})

                resp[notarised_date].update({
                    notary:{
                        "btc_count":btc_count,
                        "antara_count":antara_count,
                        "third_party_count":third_party_count,
                        "other_count":other_count,
                        "total_ntx_count":total_ntx_count,
                        "time_stamp":time_stamp,
                        "chains":{}
                    }
                })
                for chain in chain_ntx_counts:
                    resp[notarised_date][notary]["chains"].update({
                        chain:{
                            "count":chain_ntx_counts[chain],
                            "percentage":chain_ntx_pct[chain]
                        }
                    })

            delta = datetime.timedelta(days=1)
            yesterday = item['notarised_date']-delta
            tomorrow = item['notarised_date']+delta
        else:
            today = datetime.date.today()
            delta = datetime.timedelta(days=1)
            yesterday = today-delta
            tomorrow = today+delta

        url = request.build_absolute_uri('/notary_stats/daily/')
        api_resp = paginate_wrap(resp, url, "notarised_date",
                             str(yesterday), str(tomorrow))
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
        address_data = addresses.objects.filter(chain='KMD')
        if 'season' in request.GET:
            address_data = address_data.filter(season__contains=request.GET['season'])
        address_data = address_data.order_by('season','notary')
        address_data = address_data.values('address', 'season')


        address_season = {}
        for item in address_data:
            if item['address'] not in address_season:
                if item['season'].find("Season_3") == -1:
                    address_season.update({item['address']:item['season']})
                else:
                    address_season.update({item['address']:'Season_3'})


        resp = {}
        data = rewards.objects.all()
        data = apply_filters(request, RewardsSerializer, data) \
                .order_by('notary') \
                .values()

        for item in data:
            address = item['address']
            if address in address_season:
                season = address_season[address]
                notary = item['notary']
                utxo_count = item['utxo_count']
                eligible_utxo_count = item['eligible_utxo_count']
                oldest_utxo_block = item['oldest_utxo_block']
                balance = item['balance']
                pending_rewards = item['rewards']
                update_time = item['update_time']

                if season not in resp:
                    resp.update({season:{}})
                if notary not in resp[season]:
                    resp[season].update({notary:{}})

                resp[season][notary].update({
                    address:{
                        "utxo_count":utxo_count,
                        "eligible_utxo_count":eligible_utxo_count,
                        "oldest_utxo_block":oldest_utxo_block,
                        "balance":balance,
                        "rewards":pending_rewards,
                        "update_time":update_time,
                    }
                })


        api_resp = wrap_api(resp)
        return Response(api_resp)

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
        print(request.query_params)
        if 'OP_RETURN' in request.GET:

            print(request.GET['OP_RETURN'])
            decoded = decode_opret(request.GET['OP_RETURN'])
        else:
            decoded = {}
        print("DECODED: "+str(decoded)) 
        print("DECODED: "+str(type(decoded)))
        return Response(decoded)



# test time filters for daily notary summary (ntx and mining)

# Slow, review. crash err 247. add paginate func?

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
        resp = {}
        data = mined.objects.all()
        print("data len: "+str(len(data)))
        data = apply_filters(request, MinedSerializer, data)
        print("data len after filter: "+str(len(data)))
        if len(data) == len(mined.objects.all()):
            yesterday = int(time.time() -60*60*24)
            data = mined.objects.filter(block_time__gte=yesterday)
            print("data len since yesterday: "+str(len(data))) \
                .order_by('season','name', 'block_height') \
                .values()
        for item in data:
            name = item['name']
            address = item['address']
            #ignore unknown addresses
            if name != address:
                season = item['season']
                block_height = item['block_height']
                if season not in resp:
                    resp.update({season:{}})
                if name not in resp[season]:
                    resp[season].update({name:{}})
                resp[season][name].update({
                    block_height:{
                        "block_time":item['block_time'],
                        "block_datetime":item['block_datetime'],
                        "value":item['value'],
                        "address":address,
                        "txid":item['txid']
                    }
                })

        api_resp = wrap_api(resp)
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
        resp = {}
        data = notarised.objects.all()
        print("data len: "+str(len(data)))
        data = apply_filters(request, NotarisedSerializer, data)
        print("data len after filter: "+str(len(data)))
        if len(data) == len(notarised.objects.all()):
            yesterday = int(time.time()-60*60*24)
            data = notarised.objects.filter(block_time__gte=yesterday)
            print("data len default filter: "+str(len(data))) \
                .order_by('season', 'chain', '-block_height') \
                .values()

        for item in data:
            txid = item['txid']
            chain = item['chain']
            block_hash = item['block_hash']
            block_time = item['block_time']
            block_datetime = item['block_datetime']
            block_height = item['block_height']
            ac_ntx_blockhash = item['ac_ntx_blockhash']
            ac_ntx_height = item['ac_ntx_height']
            season = item['season']
            opret = item['opret']

            if season not in resp:
                resp.update({season:{}})

            if chain not in resp[season]:
                resp[season].update({chain:{}})

            resp[season][chain].update({
                block_height:{
                    "block_hash":block_hash,
                    "block_time":block_time,
                    "block_datetime":block_datetime,
                    "txid":txid,
                    "ac_ntx_blockhash":ac_ntx_blockhash,
                    "ac_ntx_height":ac_ntx_height,
                    "opret":opret
                }
            })

        api_resp = wrap_api(resp)
        return Response(api_resp)


## DASHBOARD        
def dash_view(request, dash_name=None):
    if dash_name == 'balances_table':
        html = 'tables/balances.html'
    else:
        html = 'base2.html'
    nn_health = get_nn_health()
    context = {
        "eco_data_link":get_eco_data_link(),
        "nn_health":nn_health
    }
    return render(request, html, context)

## DASHBOARD TABLES
def balances_table(request):
    pass