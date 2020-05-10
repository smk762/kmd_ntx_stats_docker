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

# Queryset manipulation

def apply_filters(request, serializer, queryset):
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
    print(request.GET)  
    print(filter_kwargs) 
    queryset = queryset.filter(**filter_kwargs)
    return queryset

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
    prev_block_hash = lil_endian(scriptPubKey_asm[:64])
    try:
        prev_block_height = int(lil_endian(scriptPubKey_asm[64:72]),16) 
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
    return { "chain":chain, "prevblock":prev_block_height, "prevhash":prev_block_hash }

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
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['name']
    ordering_fields = ['block_height']
    ordering = ['-block_height']

class MinedCountViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing mining table data
    """
    queryset = mined_count.objects.all()
    serializer_class = MinedCountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notary', 'season']
    ordering_fields = ['block_height']
    ordering = ['notary']

class ntxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised.objects.all()
    serializer_class = notarisationSerializer
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
    serializer_class = NotarisedCountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['season', 'notary']
    ordering_fields = ['season', 'notary']
    ordering = ['-season', 'notary']

class ntxChainViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised_chain.objects.all()
    serializer_class = NotarisedChainSerializer
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
    filterset_fields = ['chain', 'owner_name', 'season']
    ordering_fields = ['chain', 'owner_name', 'season']
    ordering = ['-season', 'owner_name', 'chain']

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


# simple_lists
            
class notary_names(viewsets.ViewSet):
    """
    API endpoint listing notary names for each season
    """
    serializer_class = AddressesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['season']
    ordering_fields = ['season', 'owner_name']
    ordering = ['-season']

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        Returns decoded notarisation information from OP_RETURN strings
        """
        notary_addresses = addresses.objects.values('owner_name', 'season')
        notaries_list = {}
        for item in notary_addresses:
            if item['season'].find("Season_3") != -1:
                if "Season_3" not in notaries_list:
                    notaries_list[item['season']] = []
                if item['owner_name'] not in notaries_list[item['season']]:
                    notaries_list["Season_3"].append(item['owner_name'])
            else:
                if item['season'] not in notaries_list:
                    notaries_list[item['season']] = []
                if item['owner_name'] not in notaries_list[item['season']]:
                    notaries_list[item['season']].append(item['owner_name'])

        api_resp = wrap_api(notaries_list)
        return Response(api_resp)

# Auto filterable views

class coins_filter(viewsets.ViewSet):
    """
    API endpoint showing coininfo from coins and dpow repositories
    """
    serializer_class = CoinsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        resp = {}
        data = coins.objects.all()
        data = apply_filters(request, CoinsSerializer, data)
        data = data.order_by('chain')
        data = data.values()
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
    API endpoint showing coininfo from coins and dpow repositories
    """
    serializer_class = AddressesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        resp = {}
        data = addresses.objects.all()
        data = apply_filters(request, AddressesSerializer, data)
        data = data.order_by('owner_name','season', 'chain')
        data = data.values()
        for item in data:
            if item["owner_name"] not in resp:
                resp.update({item["owner_name"]:{}})
            if item["season"] not in resp[item["owner_name"]]:
                resp[item["owner_name"]].update({
                    item["season"]: {
                        "notary_id":item["notary_id"],
                        "pubkey":item["pubkey"],
                        "addresses":{}
                    }
                })

            if item["chain"] not in resp[item["owner_name"]][item["season"]]["addresses"]:
                resp[item["owner_name"]][item["season"]]["addresses"].update({
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
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        resp = {}
        data = balances.objects.all()
        data = apply_filters(request, BalancesSerializer, data)
        data = data.order_by('season','notary', 'chain', 'balance')
        data = data.values()
        for item in data:
            
            season = item['season']
            if season not in resp:
                resp.update({season:{}})

            notary = item['notary']
            if notary not in resp:
                resp[season].update({notary:{}})

            chain = item['chain']
            if chain not in resp[season][notary]:
                resp[season][notary].update({chain:{}})

            address = item['address']
            balance = item['balance']
            resp[season][notary][chain].update({address:balance})

        api_resp = wrap_api(resp)
        return Response(api_resp)

class mined_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = MinedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        resp = {}
        data = mined.objects.all()
        data = apply_filters(request, MinedSerializer, data)
        data = data.order_by('season','name', 'block_height')
        data = data.values()
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

class mined_count_filter(viewsets.ViewSet):
    """
    API endpoint showing mined blocks by notary/address (minimum 10 blocks mined)
    """
    serializer_class = MinedCountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        resp = {}
        data = mined_count.objects.all()
        data = apply_filters(request, MinedCountSerializer, data)
        data = data.order_by('season', 'notary')
        data = data.values()

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

class notarised_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = notarisationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        resp = {}
        data = notarised.objects.all()
        data = apply_filters(request, notarisationSerializer, data)
        data = data.order_by('season', 'chain', '-block_height')
        data = data.values()

        for item in data:
            txid = item['txid']
            chain = item['chain']
            block_hash = item['block_hash']
            block_time = item['block_time']
            block_datetime = item['block_datetime']
            block_height = item['block_height']
            prev_block_hash = item['prev_block_hash']
            prev_block_height = item['prev_block_height']
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
                    "prev_block_hash":prev_block_hash,
                    "prev_block_height":prev_block_height,
                    "opret":opret
                }
            })

        api_resp = wrap_api(resp)
        return Response(api_resp)

class notarised_chain_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = NotarisedChainSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        resp = {}
        data = notarised_chain.objects.all()
        data = apply_filters(request, NotarisedChainSerializer, data)
        data = data.order_by('season', 'chain')
        data = data.values()

        for item in data:
            season = item['season']
            chain = item['chain']
            ntx_lag = item['ntx_lag']
            ntx_count = item['ntx_count']
            block_height = item['block_height']
            kmd_ntx_txid = item['kmd_ntx_txid']
            kmd_ntx_blockhash = item['kmd_ntx_blockhash']
            lastnotarization = item['lastnotarization']
            opret = item['opret']
            ac_ntx_block_hash = item['ac_ntx_block_hash']
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
                    "lastnotarization":lastnotarization,
                    "ac_ntx_block_hash":ac_ntx_block_hash,
                    "ac_ntx_height":ac_ntx_height,
                    "ac_block_height":ac_block_height,
                    "opret":opret,
                    "ntx_lag":ntx_lag
                }
            })


        api_resp = wrap_api(resp)
        return Response(api_resp)

class notarised_count_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = NotarisedCountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        resp = {}
        data = notarised_count.objects.all()
        data = apply_filters(request, NotarisedCountSerializer, data)
        data = data.order_by('season', 'notary')
        data = data.values()

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
                        "count":chain_ntx_counts[chain],
                        "percentage":chain_ntx_pct[chain]
                    }
                })


        api_resp = wrap_api(resp)
        return Response(api_resp)

class rewards_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = RewardsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        address_data = addresses.objects.filter(chain='KMD')
        if 'season' in request.GET:
            address_data = address_data.filter(season__contains=request.GET['season'])
        address_data = address_data.order_by('season','owner_name')
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
        data = apply_filters(request, RewardsSerializer, data)
        data = data.order_by('notary')
        data = data.values()

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

# test time filters for daily notary summary (ntx and mining)