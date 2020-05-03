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
    print("Getting AC block heights from electrum")
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

        print("Getting chain data from db")
        chain_data = notarised.objects.exclude(opret="unknown").filter(block_time__gte=1563148800).values('chain').annotate(ntx_count=Count('block_ht'), 
                                                   first_ntx_block=Min('block_ht'), first_ntx_blocktime=Min('block_time'),
                                                   last_ntx_block=Max('block_ht'), last_ntx_blocktime=Max('block_time'))
        ac_block_heights = get_ac_block_heights()

        chain_json = {}
        for item in chain_data:
            chain = item["chain"]
            block_ht = item["last_ntx_block"]
            print("Getting "+chain+" data from db")
            other_chain_data = notarised.objects.filter(chain=chain, block_ht=block_ht).values("prev_block_hash", "prev_block_ht", "opret", "block_hash", "txid")
            chain_json.update({
                chain:{
                    "ntx_count": item["ntx_count"],
                    "kmd_ntx_height": item["last_ntx_block"],
                    "kmd_ntx_blockhash": other_chain_data[0]["block_hash"],
                    "kmd_ntx_txid": other_chain_data[0]["txid"],
                    "lastnotarization": item["last_ntx_blocktime"],
                    "OP_RETURN": other_chain_data[0]["opret"],
                    "ac_ntx_block_hash": other_chain_data[0]["prev_block_hash"],
                    "ac_ntx_height": other_chain_data[0]["prev_block_ht"]
                }
            })
            if chain in ac_block_heights:
                chain_json[chain].update({
                    "ac_block_height": other_chain_data[0]["prev_block_ht"],
                    "ntx_lag": ac_block_heights[chain] - other_chain_data[0]["prev_block_ht"]
                })
            else:
                chain_json[chain].update({
                    "ac_block_height": "no data",
                    "ntx_lag": "no data"
                })

        return Response(chain_json)

class ntx_chain_counts(viewsets.ViewSet):
    """
    API endpoint showing Season 3 notarisations count for each chain. Use notarisations/ntx_chain_counts?chain=[chain_tag] (defaults to KMD)
    """
    serializer_class = ntxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        ntx_data = notarised_chain.objects.values()

        return Response(ntx_data)
'''
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
            notary = request.GET['notary']
        else:
            return Response({"error":"requires ?notary=notary_name parameter, e.g. /notarisations/ntx_notary_counts/?notary=dragonhound_NA"})
        print(int(time.time()))
        ntx_agg_data = notarised.objects.exclude(opret="unknown").filter(block_time__gte=1563148800).values('chain').annotate(max_blk_time=Max('block_time'),
                                                 max_blk_ht=Max('block_ht'), min_blk_time=Min('block_time'), min_blk_ht=Min('block_ht'), max_ac_blk_ht=Max('prev_block_ht')
                                                )
        print(int(time.time()))
        block_data = {}
        for item in ntx_agg_data:
            block_data.update({
                item['chain']:{
                    "max_ac_blk_ht":item["max_ac_blk_ht"],
                    "max_blk_ht":item["max_blk_ht"],
                    "max_blk_time":item["max_blk_time"],
                    "min_blk_ht":item["min_blk_ht"],
                    "min_blk_time":item["min_blk_time"]
                } 
            })

        print(int(time.time()))
        ntx_data = notarised.objects.exclude(opret="unknown").filter(block_time__gte=1563148800).values('txid', 'notaries', 'chain', 'block_time', 'block_ht','prev_block_hash', 'prev_block_ht')
        print(int(time.time()))
        ntx_resp = {}
        for item in ntx_data:
            if notary in item['notaries']:
                chain = item['chain']
                if notary not in ntx_resp:
                    ntx_resp.update({notary:{}})
                if chain not in ntx_resp[notary]:
                    ntx_resp[notary].update({
                        chain:{
                            "notarisations":1,
                            "last_ntx_kmd_block_hash":'',
                            "last_ntx_block_hash":'',
                        }
                    })
                    if chain in block_data:
                        ntx_resp[notary][chain].update({
                            "first_ntx_kmd_block_ht":block_data[chain]["min_blk_ht"],
                            "first_ntx_kmd_block_time":block_data[chain]["min_blk_time"],
                            "last_ntx_kmd_block_ht":block_data[chain]["max_blk_ht"],
                            "last_ntx_kmd_block_time":block_data[chain]["max_blk_time"],
                            "last_ntx_block_ht":block_data[chain]["max_ac_blk_ht"]
                        })
                    else:
                        ntx_resp[notary][chain].update({
                            "first_ntx_kmd_block_ht":"No data",
                            "first_ntx_kmd_block_time":"No data",
                            "last_ntx_kmd_block_ht":"No data",
                            "last_ntx_kmd_block_time":"No data",
                            "last_ntx_block_ht":"No data"
                        })
                else:
                    notarisations = ntx_resp[notary][chain]["notarisations"]+1
                    ntx_resp[notary][chain].update({"notarisations":notarisations})

                if item['block_time'] == ntx_resp[notary][chain]['last_ntx_kmd_block_time']:
                    ntx_resp[notary][chain].update({"last_ntx_kmd_block_hash":item['txid']})
                    ntx_resp[notary][chain].update({"last_ntx_block_hash":item['prev_block_hash']})
                    try:
                        ntx_resp[notary][chain].update({"ntx_lag":ac_block_ht[chain]-item['prev_block_ht']})
                    except:
                        ntx_resp[notary][chain].update({"ntx_lag":"No data"})
        print(int(time.time()))


        return Response(ntx_resp)
'''

class s3_notary_ntx_counts(viewsets.ViewSet):
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
        ntx_data = notarised_count.objects.filter(season="Season_3").values()
        return Response(ntx_data)

class s3_coins_info(viewsets.ViewSet):
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
        ntx_data = notarised_count.objects.filter(season="Season_3").values()
        return Response(ntx_data)

# List chains
# List notaries
# list addresses