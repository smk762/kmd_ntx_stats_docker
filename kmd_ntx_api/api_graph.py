#!/usr/bin/env python3
import time

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework import permissions, viewsets

from kmd_ntx_api.serializers import BalancesSerializer, NotarisedCountDailySerializer
from kmd_ntx_api.lib_query import get_balances_graph_data, get_daily_ntx_graph_data
from kmd_ntx_api.lib_helper import get_season

# Graphs

class balances_graph(viewsets.ViewSet):

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['chain', 'notary', 'season']

    ordering_fields = ['chain', 'notary', 'season']
    ordering = ['-season', 'notary', 'chain']

    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 
    serializer_class = BalancesSerializer

    def create(self, validated_data):
        return Task(id=None, **validated_data)
   
    def get(self, request, format = None): 
        if "season" in request.GET:
            season = request.GET["season"]
        else:
            season = "Season_4"
        filter_kwargs = {'season':season}

        for field in BalancesSerializer.Meta.fields:
            val = request.query_params.get(field, None)

            if val is not None:
                filter_kwargs.update({field:val}) 

        data = get_balances_graph_data(request, filter_kwargs)

        return Response(data) 

class daily_ntx_graph(viewsets.ViewSet):

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notarised_date', 'notary']

    ordering_fields = ['notarised_date', 'notary']
    ordering = ['-notarised_date', 'notary']

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = NotarisedCountDailySerializer

    def create(self, validated_data):
        return Task(id=None, **validated_data)
   
    def get(self, request, format = None): 
        if "season" in request.GET:
            season = request.GET["season"]
        else:
            season = "Season_4"
        filter_kwargs = {'season':season}

        for field in NotarisedCountDailySerializer.Meta.fields:
            val = request.query_params.get(field, None)

            if val is not None:
                filter_kwargs.update({field:val}) 

        data = get_daily_ntx_graph_data(request, filter_kwargs)

        return Response(data) 
