#!/usr/bin/env python3
from rest_framework.response import Response
from rest_framework import permissions, viewsets, authentication
from kmd_ntx_api.serializers import addrFromBase58Serializer, addrFromPubkeySerializer, decodeOpRetSerializer
from kmd_ntx_api.lib_info import get_all_coins
from kmd_ntx_api.base_58 import *

# Tool views

class api_addr_from_base58_tool(viewsets.ViewSet):
    serializer_class = addrFromBase58Serializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        Returns address from pubkey using INPUT base 58 params
        """
        missing_params = []
        for x in addrFromBase58Serializer.Meta.fields:
            if x not in request.GET:
                missing_params.append(f"{x}=<{x}>")

        if len(missing_params) > 0:
            params = '&'.join(missing_params)
            error = f"You need to specify params like '?{params}'"
            return Response({"error":f"Missing params: {error}"})

        resp = calc_addr_tool(request.GET["pubkey"], request.GET["pub_addr"],
                             request.GET["script_addr"], request.GET["secret_key"])
        return Response(resp)


class api_address_from_pubkey_tool(viewsets.ViewSet):
    serializer_class = addrFromPubkeySerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        Returns address from pubkey using CONST base 58 params
        """
        resp = get_address_from_pubkey(request)
        return Response(resp)


class api_decode_op_return_tool(viewsets.ViewSet):
    """
    Decodes notarization OP_RETURN strings.
    USAGE: decode_opret/?OP_RETURN=<OP_RETURN>
    """    
    serializer_class = decodeOpRetSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        Returns decoded notarisation information from OP_RETURN strings
        """
        if 'OP_RETURN' in request.GET:
 
            coins_list = get_all_coins() 
            decoded = decode_opret(request.GET['OP_RETURN'], coins_list)
        else:
            decoded = {"error":"needs parm like ?OP_RETURN=fcfc5360a088f031c753b6b63fd76cec9d3e5f5d11d5d0702806b54800000000586123004b4d4400"}
        return Response(decoded)


# TODO: cater for coins without params etc.
def get_address_from_pubkey(request):
    if "coin" in request.GET:
        coin = request.GET["coin"]
    else:
        coin = "KMD"
    if "pubkey" in request.GET:
        if coin in COIN_PARAMS:
            pubkey = request.GET["pubkey"]

            return {
                "coin": coin,
                "pubkey": pubkey,
                "address": calc_addr_from_pubkey(coin, pubkey)
            }

        else:
            return {
                "error": f"{coin} does not have locally defined COIN_PARAMS. If you know what these are, you can try the /api/tools/addr_from_base58 endpoint instead."
            }

    else:
        return {
            "error": "You need to specify a pubkey and coin like '?coin=KMD&pubkey=<YOUR_PUBKEY>'\nIf coin not specified or unknown, will revert to KMD"
        }

