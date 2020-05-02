#!/usr/bin/env python3
import os
import sys
import json
import binascii
import time
import logging
import logging.handlers
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
    filterset_fields = ['name']
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['block']
    ordering = ['block']


class ntxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised.objects.all()
    serializer_class = ntxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['chain']
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['block_time']
    ordering = ['block_time']

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
    ordering = ['time_stamp']

class ntxCountViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations count data
    """
    queryset = notarised_count.objects.all()
    serializer_class = ntxCountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['notary']
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['time_stamp']
    ordering = ['time_stamp']

class decodeOpRetViewSet(viewsets.ViewSet):
    """
    Decodes notarization OP_RETURN strings.
    USAGE: decode_opret/?OP_RETURN=<OP_RETURN>
    """    
    # renderer_classes = [TemplateHTMLRenderer]
    # template_name = 'decode_opret.html' 
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

