#!/usr/bin/env python3
import os
import sys
import json
import binascii
import time
import requests
import logging
import logging.handlers
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

def filter_include_timespan(table, start, end):
    return table.objects.filter(block_time__gte=start, block_time__lte=end)

def filter_exclude_timespan(table, start, end):
    return table.objects.exclude(block_time__gte=start, block_time__lte=end)

def filter_include_blocks(table, start, end):
    return table.objects.filter(block_ht__gte=start, block_ht__lte=end)

def filter_exclude_blocks(table, start, end):
    return table.objects.exclude(block_ht__gte=start, block_ht__lte=end)


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

noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'AYA']

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
    prev_block_hash = lil_endian(scriptPubKey_asm[:64])
    try:
        prev_block_ht = int(lil_endian(scriptPubKey_asm[64:72]),16) 
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
    return { "chain":chain, "prevblock":prev_block_ht, "prevhash":prev_block_hash }


third_party_chains = ["AYA", "CHIPS", "EMC2", "GAME", "GIN", 'HUSH3']

antara_chains = ["AXO", "BET", "BOTS", "BTCH", "CCL", "COQUICASH", "CRYPTO", "DEX", "ETOMIC", "HODL", "ILN", "JUMBLR",
                "K64", "KOIN", "KSB", "KV", "MESH", "MGW", "MORTY", "MSHARK", "NINJA", "OOT", "OUR", "PANGEA", "PGT",
                "PIRATE", "REVS", "RFOX", "RICK", "SEC", "SUPERNET", "THC", "VOTE2020", "VRSC", "WLC21", "ZEXO",
                "ZILLA", "STBL"]

ex_antara_chains = ['CHAIN', 'GLXT', 'MCL', 'PRLPAY', 'COMMOD', 'DION',
                   'EQL', 'CEAL', 'BNTN', 'KMDICE', 'DSEC', "WLC"]

all_antara_chains = antara_chains + ex_antara_chains

s3_notaries = ['alien_AR', 'alien_EU', 'alright_AR', 'and1-89_EU', 'blackjok3r_SH',
               'ca333_DEV', 'chainmakers_EU', 'chainmakers_NA', 'chainstrike_SH',
               'chainzilla_SH', 'chmex_EU', 'cipi_AR', 'cipi_NA', 'computergenie_NA',
               'cryptoeconomy_EU', 'd0ct0r_NA', 'decker_AR', 'decker_DEV',
               'dragonhound_NA', 'dwy_EU', 'dwy_SH', 'etszombi_AR', 'etszombi_EU',
               'fullmoon_AR', 'fullmoon_NA', 'fullmoon_SH', 'gt_AR', 'indenodes_AR',
               'indenodes_EU', 'indenodes_NA', 'indenodes_SH', 'infotech_DEV',
               'jeezy_EU', 'karasugoi_NA', 'kolo_DEV', 'komodopioneers_EU',
               'komodopioneers_SH', 'lukechilds_AR', 'lukechilds_NA', 'madmax_AR',
               'madmax_NA', 'metaphilibert_AR', 'metaphilibert_SH', 'node-9_EU',
               'nutellalicka_SH', 'patchkez_SH', 'pbca26_NA', 'peer2cloud_AR',
               'phba2061_EU', 'phm87_SH', 'pirate_AR', 'pirate_EU', 'pirate_NA',
               'pungocloud_SH', 'strob_NA', 'thegaltmines_NA', 'titomane_AR',
               'titomane_EU', 'titomane_SH', 'tonyl_AR', 'voskcoin_EU',
               'webworker01_NA', 'webworker01_SH', 'zatjum_SH']

def wrap_api(resp):
    api_resp = {
        "count":len(resp),
        "results":[resp]
    }
    return api_resp

def get_ac_block_heights():
    print("Getting AC block heights from electrum")
    ac_block_ht = {}
    for chain in antara_chains:
      try:
        url = 'http://'+chain.lower()+'.explorer.dexstats.info/insight-api-komodo/sync'
        r = requests.get(url)
        ac_block_ht.update({chain:r.json()['blockChainHeight']})
      except Exception as e:
        print(chain+" failed")
        print(e)
    return ac_block_ht

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
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['name']
    ordering_fields = ['block']
    ordering = ['-block']

class MinedCountViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing mining table data
    """
    queryset = mined_count.objects.all()
    serializer_class = MinedCountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notary', 'season']
    ordering_fields = ['block']
    ordering = ['notary']

class ntxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised.objects.all()
    serializer_class = ntxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['chain']
    ordering_fields = ['block_time']
    ordering = ['-block_time']

class ntxCountViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised_count.objects.all()
    serializer_class = ntxCountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['chain']
    ordering_fields = ['block_time']
    ordering = ['-block_time']

class ntxChainCountViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised_chain.objects.all()
    serializer_class = ntxChainCountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['chain']
    ordering_fields = ['block_time']
    ordering = ['-block_time']

class coinsViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = coins.objects.all()
    serializer_class = CoinsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
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
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['chain', 'notary_name', 'season']
    ordering_fields = ['chain', 'notary_name', 'season']
    ordering = ['-season', 'notary_name', 'chain']

class balancesViewSet(viewsets.ModelViewSet):
    """
    API endpoint Notary balances 
    """
    queryset = balances.objects.all()
    serializer_class = BalancesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['chain', 'notary']
    ordering_fields = ['chain', 'notary']
    ordering = ['notary']

class rewardsViewSet(viewsets.ModelViewSet):
    """
    API pending KMD rewards for notaries
    """
    queryset = rewards.objects.all()
    serializer_class = RewardsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notary']
    ordering_fields = ['notary']
    ordering = ['notary']

class s3_notary_balances(viewsets.ViewSet):
    """
    API endpoint showing mining max and sum data
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        Returns decoded notarisation information from OP_RETURN strings
        """
        balances_resp = {}
        s3_notaries = addresses.objects.filter(
                                        season="Season_3.5"
                                        ).order_by(
                                        'notary_name'
                                        ).values(
                                        'notary_name'
                                        )
        notary_list = []

        for item in s3_notaries:
            notary_list.append(item['notary_name'])

        notary_balances = balances.objects.all().order_by(
                                    'notary', 'chain', 'balance'
                                    ).values()
        for item in notary_balances:
            notary = item['notary']
            if notary in notary_list:
                if notary not in balances_resp:
                    balances_resp.update({notary:{}})
                address = item['address']
                chain = item['chain']
                balance = item['balance']
                if chain not in balances_resp[notary]:
                    balances_resp[notary].update({chain:{}})
                balances_resp[notary][chain].update({address:balance})
        api_resp = wrap_api(balances_resp)
        return Response(api_resp)

class decodeOpRetViewSet(viewsets.ViewSet):
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

class s3_mining(viewsets.ViewSet):
    """
    API endpoint showing mining max and sum data
    """
    serializer_class = MinedCountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        Returns decoded notarisation information from OP_RETURN strings
        """
        s3_mined_aggregates = mined.objects.filter(block_time__gte=seasons_info["Season_3"]['start_time']).values('name').annotate(
                                                   mined_count=Count('value'), mined_sum=Sum('value'), 
                                                   first_mined_block=Min('block'), first_mined_blocktime=Min('block_time'),
                                                   last_mined_block=Max('block'), last_mined_blocktime=Max('block_time'))
        s3_addresses = addresses.objects.filter(season="Season_3", chain="KMD").values("notary_name","address")

        s3_notary_addr = {}
        for item in s3_addresses:
            s3_notary_addr.update({item["notary_name"]:item["address"]})

        s3_notary_mined_json = {}
        for item in s3_mined_aggregates:
            if item['name'] in s3_notary_addr:
                s3_notary_mined_json.update({
                    item['name']: {
                        "address": s3_notary_addr[item["name"]],
                        "mined_count": item['mined_count'],
                        "mined_sum": item['mined_sum'],
                        "first_mined_block": item['first_mined_block'],
                        "first_mined_blocktime": item['first_mined_blocktime'],
                        "last_mined_block": item['last_mined_block'],
                        "last_mined_blocktime": item['last_mined_blocktime']                        
                    }   
                })
        api_resp = wrap_api(s3_notary_mined_json)
        return Response(api_resp)

def apply_filters(request, serializer, queryset):
    filter_kwargs = {}
    for field in serializer.Meta.fields:
        print(field)
        print(request.GET)
        print(str(request.query_params)+"=-=-")
        print(str(request.query_params.get("name"))+"---")
        print(str(request.query_params.get(field))+"-+-")
        print(field)
        val = request.query_params.get(field, None)
        if val is not None:
            filter_kwargs.update({field:val})    
    print(filter_kwargs)
    queryset = queryset.filter(**filter_kwargs)
    return queryset

def apply_annotation(request, queryset, **kwargs):
    return queryset.annotate(**kwargs)

class filter_mined_count(viewsets.ViewSet):
    """
    API endpoint showing mining max and sum data
    """
    serializer_class = MinedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        Returns decoded notarisation information from OP_RETURN strings
        """
        mined_blocks = mined.objects.all()
        mined_filtered = apply_filters(request, MinedSerializer, mined_blocks)
        mined_values = mined_filtered.values('name')
        mined_aggregates = apply_annotation(request, mined_values, mined_count=Count('value'), mined_sum=Sum('value'), 
                                                   first_mined_block=Min('block'), first_mined_blocktime=Min('block_time'),
                                                   last_mined_block=Max('block'), last_mined_blocktime=Max('block_time'))
        '''
        .values('name').annotate(
                                                   mined_count=Count('value'), mined_sum=Sum('value'), 
                                                   first_mined_block=Min('block'), first_mined_blocktime=Min('block_time'),
                                                   last_mined_block=Max('block'), last_mined_blocktime=Max('block_time'))'''
        known_addresses = addresses.objects.filter(chain="KMD").values("notary_name","address")

        notary_addr = {}
        for item in known_addresses:
            notary_addr.update({item["notary_name"]:item["address"]})

        notary_mined_json = {}
        for item in mined_aggregates:
            if item['name'] in notary_addr:
                notary_mined_json.update({
                    item['name']: {
                        "address": notary_addr[item["name"]],
                        "mined_count": item['mined_count'],
                        "mined_sum": item['mined_sum'],
                        "first_mined_block": item['first_mined_block'],
                        "first_mined_blocktime": item['first_mined_blocktime'],
                        "last_mined_block": item['last_mined_block'],
                        "last_mined_blocktime": item['last_mined_blocktime']                        
                    }   
                })
        api_resp = wrap_api(notary_mined_json)
        return Response(api_resp)

class notary_addresses(viewsets.ViewSet):
    """
    API endpoint showing mining max and sum data
    """
    serializer_class = AddressesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notary_name', 'season', 'chain']
    ordering_fields = ['season', 'notary_name', 'chain']
    ordering = ['-season', 'notary_name', 'chain']

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        Returns notary addresses grouped by season > notary > chain
        """

        notary_addresses = addresses.objects.all().order_by(
                            "-season", "notary_name", "chain"
                            ).values(
                            'season', 'notary_name', 'notary_id', 
                            'chain', 'address', 'pubkey'
                            )
        notary_json = {}
        for item in notary_addresses:
            season = item["season"]
            notary = item["notary_name"]
            notary_id = item["notary_id"]
            pubkey = item["pubkey"]
            chain = item["chain"]
            address = item["address"]
            if season not in notary_json:
                notary_json.update({season:{}})
            if notary not in notary_json[season]:
                notary_json[season].update({notary:{
                    "notary_id":notary_id,
                    "pubkey":pubkey,
                    "addresses":{chain:address}
                }})
            else:
                notary_json[season][notary]["addresses"].update({chain:address})
        api_resp = wrap_api(notary_json)
        return Response(api_resp)

class s3_notary_addresses(viewsets.ViewSet):
    """
    API endpoint showing mining max and sum data
    """
    serializer_class = AddressesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notary_name', 'season', 'chain']
    ordering_fields = ['season', 'notary_name', 'chain']
    ordering = ['-season', 'notary_name', 'chain']

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        Returns notary addresses grouped by season > notary > chain
        """

        notary_addresses = addresses.objects.all().order_by(
                            "-season", "notary_name", "chain"
                            ).values(
                            'season', 'notary_name', 'notary_id', 
                            'chain', 'address', 'pubkey'
                            )
        notary_json = {}
        for item in notary_addresses:
            season = item["season"]
            if season.find("_3") != -1:
                notary = item["notary_name"]
                notary_id = item["notary_id"]
                pubkey = item["pubkey"]
                chain = item["chain"]
                address = item["address"]
                if season not in notary_json:
                    notary_json.update({season:{}})
                if notary not in notary_json[season]:
                    notary_json[season].update({notary:{
                        "notary_id":notary_id,
                        "pubkey":pubkey,
                        "addresses":{chain:address}
                    }})
                else:
                    notary_json[season][notary]["addresses"].update({chain:address})
        api_resp = wrap_api(notary_json)
        return Response(api_resp)

class notary_names(viewsets.ViewSet):
    """
    API endpoint showing mining max and sum data
    """
    serializer_class = AddressesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['season']
    ordering_fields = ['season', 'notary_name']
    ordering = ['-season']

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        Returns decoded notarisation information from OP_RETURN strings
        """
        notary_addresses = addresses.objects.values('notary_name', 'season')
        notaries_list = {}
        for item in notary_addresses:
            if item['season'] not in notaries_list:
                notaries_list[item['season']] = []
            if item['notary_name'] not in notaries_list[item['season']]:
                notaries_list[item['season']].append(item['notary_name'])
        api_resp = wrap_api(notaries_list)
        return Response(api_resp)
            
class s3_notary_names(viewsets.ViewSet):
    """
    API endpoint showing mining max and sum data
    """
    serializer_class = AddressesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['season']
    ordering_fields = ['season', 'notary_name']
    ordering = ['-season']

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        Returns decoded notarisation information from OP_RETURN strings
        """
        notary_addresses = addresses.objects.values('notary_name', 'season')
        notaries_list = {}
        for item in notary_addresses:
            if item['season'].find("Season_3") != -1:
                if item['season'] not in notaries_list:
                    notaries_list[item['season']] = []
                if item['notary_name'] not in notaries_list[item['season']]:
                    notaries_list[item['season']].append(item['notary_name'])
        api_resp = wrap_api(notaries_list)
        return Response(api_resp)

class s3_chain_notarisation(viewsets.ViewSet):
    """
    API endpoint showing Season 3 notarisations count for each chain. Use notarisations/ntx_chain_counts?chain=[chain_tag] (defaults to KMD)
    """
    serializer_class = ntxChainCountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        ntx_data = notarised_chain.objects.values(
                                         'chain','ntx_count','kmd_ntx_height','kmd_ntx_blockhash',
                                         'kmd_ntx_txid','lastnotarization','opret','ac_ntx_block_hash',
                                         'ac_ntx_height','ac_block_height','ntx_lag')
        ntx_json = {}
        for item in ntx_data:
            ntx_json.update({
                item['chain']: {
                    "ntx_count": item['ntx_count'],
                    "kmd_ntx_height": item['kmd_ntx_height'],
                    "kmd_ntx_blockhash": item['kmd_ntx_blockhash'],
                    "kmd_ntx_txid": item['kmd_ntx_txid'],
                    "lastnotarization": item['lastnotarization'],
                    "opret": item['opret'],
                    "ac_ntx_block_hash": item['ac_ntx_block_hash'],
                    "ac_ntx_height": item['ac_ntx_height'],
                    "ac_block_height": item['ac_block_height'],
                    "ntx_lag": item['ntx_lag']
                }
            })
        api_resp = wrap_api(ntx_json)
        return Response(api_resp)

class s3_notarisation(viewsets.ViewSet):
    """
    API endpoint showing Season 3 notarisations count for each chain. Use notarisations/ntx_chain_counts?chain=[chain_tag] (defaults to KMD)
    """
    serializer_class = ntxCountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        ntx_data = notarised_count.objects.filter(season="Season_3").order_by('notary').values(
                                                 'notary','btc_count','antara_count','third_party_count',
                                                 'other_count','total_ntx_count','chain_ntx_counts',
                                                 'chain_ntx_pct','time_stamp')
        api_resp = wrap_api(ntx_data)
        return Response(api_resp)

class s3_dpow_coins(viewsets.ViewSet):
    """
    API endpoint showing Season 3 notarisations count for each chain. Use notarisations/ntx_chain_counts?chain=[chain_tag] (defaults to KMD)
    """
    serializer_class = CoinsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        coins_resp = {}
        coins_data = coins.objects.exclude(dpow={}).values()
        for item in coins_data:
            coins_resp.update({
                item["chain"]:{
                    "coins_info":item["coins_info"],
                    "dpow":item["dpow"],
                    "explorers":item["explorers"],
                    "electrums":item["electrums"],
                    "electrums_ssl":item["electrums_ssl"]
                }
            })
        api_resp = wrap_api(coins_resp)
        return Response(api_resp)

class mm2_coins(viewsets.ViewSet):
    """
    API endpoint showing Season 3 notarisations count for each chain. Use notarisations/ntx_chain_counts?chain=[chain_tag] (defaults to KMD)
    """
    serializer_class = CoinsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        coins_resp = {}
        coins_data = coins.objects.values()
        for item in coins_data:
            if 'mm2' in item["coins_info"]:
                if item["coins_info"]['mm2'] == 1:
                    coins_resp.update({
                        item["chain"]:{
                            "coins_info":item["coins_info"],
                            "dpow":item["dpow"],
                            "explorers":item["explorers"],
                            "electrums":item["electrums"],
                            "electrums_ssl":item["electrums_ssl"]
                        }
                    })
        api_resp = wrap_api(coins_resp)
        return Response(api_resp)

class coin_electrums(viewsets.ViewSet):
    """
    API endpoint showing Season 3 notarisations count for each chain. Use notarisations/ntx_chain_counts?chain=[chain_tag] (defaults to KMD)
    """
    serializer_class = CoinsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        coins_resp = {}
        coins_data = coins.objects.exclude(electrums=[], electrums_ssl=[], ).values()
        for item in coins_data:
            if 'mm2' in item["coins_info"]:
                if item["coins_info"]['mm2'] == 1:
                    coins_resp.update({
                        item["chain"]:{
                            "coins_info":item["coins_info"],
                            "dpow":item["dpow"],
                            "explorers":item["explorers"],
                            "electrums":item["electrums"],
                            "electrums_ssl":item["electrums_ssl"]
                        }
                    })

        api_resp = wrap_api(coins_resp)
        return Response(api_resp)

class coin_explorers(viewsets.ViewSet):
    """
    API endpoint showing Season 3 notarisations count for each chain. Use notarisations/ntx_chain_counts?chain=[chain_tag] (defaults to KMD)
    """
    serializer_class = CoinsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        coins_resp = {}
        coins_data = coins.objects.exclude(explorers=[]).values()
        for item in coins_data:
            if 'mm2' in item["coins_info"]:
                if item["coins_info"]['mm2'] == 1:
                    coins_resp.update({
                        item["chain"]:{
                            "coins_info":item["coins_info"],
                            "dpow":item["dpow"],
                            "explorers":item["explorers"],
                            "electrums":item["electrums"],
                            "electrums_ssl":item["electrums_ssl"]
                        }
                    })

        api_resp = wrap_api(coins_resp)
        return Response(api_resp)

# list balances (via electrum incl. 3P)
# calc notary ntx percentage
# daily notary summary (ntx and mining)

