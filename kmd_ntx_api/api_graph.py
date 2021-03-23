#!/usr/bin/env python3
from kmd_ntx_api.serializers import *
from django.contrib.auth.models import User, Group
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, \
                                          NumberFilter
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework import permissions, viewsets, authentication
from kmd_ntx_api.filters import *
from kmd_ntx_api.serializers import *
from kmd_ntx_api.models import *
from kmd_ntx_api.lib_query import * 

# Graphs

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
