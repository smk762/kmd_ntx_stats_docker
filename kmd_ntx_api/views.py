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


third_party_coins = ["AYA", "CHIPS", "EMC2", "GAME", "GIN", 'HUSH3']

antara_coins = ["AXO", "BET", "BOTS", "BTCH", "CCL", "COQUICASH", "CRYPTO", "DEX", "ETOMIC", "HODL", "ILN", "JUMBLR",
                "K64", "KOIN", "KSB", "KV", "MESH", "MGW", "MORTY", "MSHARK", "NINJA", "OOT", "OUR", "PANGEA", "PGT",
                "PIRATE", "REVS", "RFOX", "RICK", "SEC", "SUPERNET", "THC", "VOTE2020", "VRSC", "WLC21", "ZEXO",
                "ZILLA", "STBL"]

ex_antara_coins = ['CHAIN', 'GLXT', 'MCL', 'PRLPAY', 'COMMOD', 'DION',
                   'EQL', 'CEAL', 'BNTN', 'KMDICE', 'DSEC', "WLC"]

all_antara_coins = antara_coins + ex_antara_coins

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

def get_ac_block_heights():
    ac_block_ht = {}
    for chain in antara_coins:
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

class MinedCountViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing mining max and sum data
    """
    queryset = mined_count.objects.all()
    serializer_class = MinedCountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ntxCountList(generics.ListAPIView):
    queryset = notarised_count.objects.all()
    serializer_class = ntxCountSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notary']
    ordering_fields = ['time_stamp']
    ordering = ['-time_stamp']

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

class season3_mining_stats(viewsets.ViewSet):
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
        s3_mined_aggregates = mined.objects.filter(block_time__gte=1563148800).values('name').annotate(
                                                   mined_count=Count('value'), mined_sum=Sum('value'), 
                                                   first_mined_block=Min('block'), first_mined_blocktime=Min('block_time'),
                                                   last_mined_block=Max('block'), last_mined_blocktime=Max('block_time'))
        s3_notary_mined_aggregates = []
        for item in s3_mined_aggregates:
            if item['name'] in s3_notaries:
                s3_notary_mined_aggregates.append(item)

        return Response(s3_notary_mined_aggregates)

class notary_addresses(viewsets.ViewSet):
    """
    API endpoint showing mining max and sum data
    """
    serializer_class = AddressesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notary_name', 'season']
    ordering_fields = ['season', 'notary_name']
    ordering = ['-season']

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        Returns decoded notarisation information from OP_RETURN strings
        """
        notary_addresses = addresses.objects.values('season', 'notary_name', 'notary_id', 'address', 'pubkey')
        return Response(notary_addresses)

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
            notaries_list[item['season']].append(item['notary_name'])
        return Response(notaries_list)

class notarised_chains(viewsets.ViewSet):
    """
    API endpoint showing mining max and sum data
    """
    serializer_class = ntxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        Returns decoded notarisation information from OP_RETURN strings
        """
        chain_data = notarised.objects.exclude(opret="unknown").filter(block_time__gte=1563148800).values('chain').annotate(ntx_count=Count('block_ht'), 
                                                   first_ntx_block=Min('block_ht'), first_ntx_blocktime=Min('block_time'),
                                                   last_ntx_block=Max('block_ht'), last_ntx_blocktime=Max('block_time'))

        return Response(chain_data)

class ntx_chain_counts(viewsets.ViewSet):
    """
    API endpoint showing Season 3 notarisations count for each chain. Use notarisations/ntx_chain_counts?chain=[chain_tag] (defaults to KMD)
    """
    serializer_class = ntxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['chain']
    ordering_fields = ['block_time']
    ordering = ['-block_time']

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        if 'chain' in request.GET:
            chain = request.GET['chain']
        else:
            chain = "KMD"
        ntx_data = notarised.objects.exclude(opret="unknown").filter(block_time__gte=1563148800, chain=chain).values('txid', 'chain', 'block_hash', 'block_time', 'block_ht', 'notaries', 'prev_block_hash', 'prev_block_ht', 'opret')
        ntx_counts = {}
        for item in ntx_data:
            chain = item['chain']
            if chain not in ntx_counts:
                ntx_counts.update({chain:{}})
            for notary in item['notaries']:
                if notary not in ntx_counts[chain]:
                    ntx_counts[chain].update({
                        notary: {
                            "count":1,
                            "first_block":99999999999999,
                            "last_block":0,
                            "first_block_time":99999999999999,
                            "last_block_time":0,
                            }
                          })
                else:
                    count = ntx_counts[chain][notary]["count"]+1
                    ntx_counts[chain][notary].update({"count":count})

                if item['block_time'] < ntx_counts[chain][notary]['first_block_time']:
                    ntx_counts[chain][notary].update({"first_block_time":item['block_time']})
                if item['block_time'] > ntx_counts[chain][notary]['last_block_time']:
                    ntx_counts[chain][notary].update({"last_block_time":item['block_time']})

                if item['block_ht'] < ntx_counts[chain][notary]['first_block']:
                    ntx_counts[chain][notary].update({"first_block":item['block_ht']})
                if item['block_ht'] > ntx_counts[chain][notary]['last_block']:
                    ntx_counts[chain][notary].update({"last_block":item['block_ht']})

        return Response(ntx_counts)

class ntx_notary_counts(viewsets.ViewSet):
    """
    API endpoint showing Season 3 notarisations count for each notary for a chain. Use notarisations/ntx_notary_counts?notary=[notary_name] (Required)
    """
    serializer_class = ntxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['chain']
    ordering_fields = ['block_time']
    ordering = ['-block_time']

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        ac_block_ht = get_ac_block_heights()
        if 'notary' in request.GET:
            notary_name = request.GET['notary']
        else:
            return Response({"error":"requires ?notary=notary_name parameter, e.g. /notarisations/ntx_notary_counts/?notary=dragonhound_NA"})

        ntx_data = notarised.objects.exclude(opret="unknown").filter(block_time__gte=1563148800).values('notaries', 'chain', 'block_time', 'block_ht','prev_block_hash', 'prev_block_ht')
        ntx_resp = {}
        for item in ntx_data:
            for notary in item['notaries']:
                if notary == notary_name:
                    chain = item['chain']
                    if notary not in ntx_resp:
                        ntx_resp.update({notary:{}})
                    if chain not in ntx_resp[notary]:
                        ntx_resp[notary].update({
                            chain:{
                                "count":1,
                                "first_block":99999999999999,
                                "last_block":0,
                                "first_block_time":99999999999999,
                                "last_block_time":0,
                                "last_ntx_block_ht":'',
                                "last_ntx_block_hash":'',
                            }
                        })
                    else:
                        count = ntx_resp[notary][chain]["count"]+1
                        ntx_resp[notary][chain].update({"count":count})

                    if item['block_time'] < ntx_resp[notary][chain]['first_block_time']:
                        ntx_resp[notary][chain].update({"first_block_time":item['block_time']})
                    if item['block_time'] > ntx_resp[notary][chain]['last_block_time']:
                        ntx_resp[notary][chain].update({"last_block_time":item['block_time']})
                        ntx_resp[notary][chain].update({"last_ntx_block_ht":item['prev_block_ht']})
                        ntx_resp[notary][chain].update({"last_ntx_block_hash":item['prev_block_hash']})
                        try:
                            ntx_resp[notary][chain].update({"ntx_lag":ac_block_ht[chain]-item['prev_block_ht']})
                        except:
                            ntx_resp[notary][chain].update({"ntx_lag":"No data"})

                    if item['block_ht'] < ntx_resp[notary][chain]['first_block']:
                        ntx_resp[notary][chain].update({"first_block":item['block_ht']})
                    if item['block_ht'] > ntx_resp[notary][chain]['last_block']:
                        ntx_resp[notary][chain].update({"last_block":item['block_ht']})



        return Response(ntx_resp)

# List chains
# List notaries
# list addresses