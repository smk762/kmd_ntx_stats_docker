#!/usr/bin/env python3
from django.contrib.auth.models import User, Group
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework import permissions, viewsets

from kmd_ntx_api.lib_const import *
from kmd_ntx_api.models import *
from kmd_ntx_api.filters import *
from kmd_ntx_api.serializers import *

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


class addressesViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing Notary Addresses
    """
    queryset = addresses.objects.all()
    serializer_class = addressesSerializer
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
    serializer_class = balancesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['chain', 'notary', 'season', 'server']
    ordering_fields = ['chain', 'notary', 'season']
    ordering = ['-season', 'notary', 'chain']


class coinsViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = coins.objects.all()
    serializer_class = coinsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['chain']
    ordering_fields = ['chain']
    ordering = ['chain']



class lastNtxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = last_notarised.objects.all()
    serializer_class = lastNotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary', 'chain', 'season']
    ordering_fields = ['season', 'notary', 'chain']
    ordering = ['season', 'notary', 'chain']


class MinedViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing mining table data
    """
    queryset = mined.objects.all()
    serializer_class = minedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = minedFilter
    ordering_fields = ['block_height', 'address', 'season', 'name']
    ordering = ['-block_height']


class MinedCountDayViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing mining table data
    """
    queryset = mined_count_daily.objects.all()
    serializer_class = minedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['mined_date', 'notary']
    ordering_fields = ['mined_date','notary']
    ordering = ['-mined_date','notary']


class MinedCountSeasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing mining table data
    """
    queryset = mined_count_season.objects.all()
    serializer_class = minedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary', 'season']
    ordering_fields = ['block_height']
    ordering = ['notary']


class nn_socialViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing Node Operator social links
    """
    queryset = nn_social.objects.all()
    serializer_class = nnSocialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary', 'season']
    ordering_fields = ['season', 'notary']
    ordering = ['-season', 'notary']


class ntxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised.objects.all()
    serializer_class = notarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ntxFilter
    ordering_fields = ['block_time', 'chain']
    ordering = ['-block_time', 'chain']


class ntxCountDateViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised_count_daily.objects.all()
    serializer_class = notarisedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notarised_date', 'notary']
    ordering_fields = ['notarised_date', 'notary']
    ordering = ['-notarised_date', 'notary']


class ntxCountSeasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised_count_season.objects.all()
    serializer_class = notarisedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['season', 'notary']
    ordering_fields = ['season', 'notary']
    ordering = ['-season', 'notary']


class ntxChainDateViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised_chain_daily.objects.all()
    serializer_class = notarisedChainDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notarised_date', 'chain']
    ordering_fields = ['notarised_date', 'chain']
    ordering = ['-notarised_date', 'chain']


class ntxChainSeasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised_chain_season.objects.all()
    serializer_class = notarisedChainSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['chain', 'season']
    ordering_fields = ['block_height']
    ordering = ['-block_height']


class ntxTenureViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing chain notarisation tenure
    """
    queryset = notarised_tenure.objects.all()
    serializer_class = ntxTenureSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['chain', 'season']
    ordering_fields = ['chain', 'season']
    ordering = ['-season', 'chain']

