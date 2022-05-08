#!/usr/bin/env python3
from django.contrib.auth.models import User, Group
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework import permissions, viewsets
from rest_framework.pagination import PageNumberPagination

from kmd_ntx_api.models import *
from kmd_ntx_api.filters import *
import kmd_ntx_api.filters as filters
import kmd_ntx_api.serializers as serializers


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 200
    page_size_query_param = 'page_size'
    max_page_size = 10000

class TableResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500

class MassiveResultsSetPagination(PageNumberPagination):
    page_size = 10000
    page_size_query_param = 'page_size'
    max_page_size = 10000


## Source data endpoints
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class addressesViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing Notary Addresses
    """
    queryset = addresses.objects.all()
    serializer_class = serializers.addressesSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['coin', 'notary', 'season', 'server']
    ordering_fields = ['coin', 'notary', 'season', 'server']
    ordering = ['-season', 'server', 'notary', 'coin']


class balancesViewSet(viewsets.ModelViewSet):
    """
    API endpoint Notary balances 
    """
    queryset = balances.objects.all()
    serializer_class = serializers.balancesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['coin', 'notary', 'season', 'server']
    ordering_fields = ['coin', 'notary', 'season']
    ordering = ['-season', 'notary', 'coin']


# class coinSync(viewsets.ModelViewSet):


class coinsViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing coins table data
    """
    queryset = coins.objects.all()
    serializer_class = serializers.coinsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['coin']
    ordering_fields = ['coin']
    ordering = ['coin']


class coinSocialViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = coin_social.objects.all()
    serializer_class = serializers.coinSocialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['coin', 'season']
    ordering_fields = ['coin']
    ordering = ['coin']


# class fundingTransactionsViewSet(viewsets.ModelViewSet):


class notaryLastNtxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing last coin notarisation for each notary
    """
    queryset = notary_last_ntx.objects.all()
    serializer_class = serializers.notaryLastNtxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['season', 'notary', 'coin']
    ordering_fields = ['season', 'notary', 'coin']
    ordering = ['season', 'notary', 'coin']


class coinLastNtxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing last notarisation for each coin
    """
    queryset = coin_last_ntx.objects.all()
    serializer_class = serializers.coinLastNtxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['season', 'coin']
    ordering_fields = ['season', 'coin']
    ordering = ['season', 'coin']


class minedViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = mined.objects.all()
    serializer_class = serializers.minedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = filters.minedFilter
    ordering_fields = ['block_height', 'address', 'season', 'name']
    ordering = ['-block_height']


class minedCountDailyViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = mined_count_daily.objects.all()
    serializer_class = serializers.minedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['mined_date', 'notary']
    ordering_fields = ['mined_date','notary']
    ordering = ['-mined_date','notary']


class minedCountSeasonViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = mined_count_season.objects.all()
    serializer_class = serializers.minedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['name', 'season']
    ordering_fields = ['name']
    ordering = ['name']


class mm2VersionStatsViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing mm2 Version Stats table data
    """
    queryset = mm2_version_stats.objects.all()
    serializer_class = serializers.mm2VersionStatsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['name', 'season', 'version']
    ordering_fields = ['-timestamp']
    ordering = ['name', 'season']


class nnBtcTxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing Node Operator social links
    """
    queryset = nn_btc_tx.objects.all()
    serializer_class = serializers.nnBtcTxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary', 'season']
    ordering_fields = ['season', 'notary']
    ordering = ['-season', 'notary']


class nnLtcTxViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = nn_ltc_tx.objects.all()
    serializer_class = serializers.nnLtcTxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary', 'season']
    ordering_fields = ['season', 'notary']
    ordering = ['-season', 'notary']


class nnSocialViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing Node Operator social links
    """
    queryset = nn_social.objects.all()
    serializer_class = serializers.nnSocialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary', 'season']
    ordering_fields = ['season', 'notary']
    ordering = ['-season', 'notary']


class notarisedViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised.objects.all()
    serializer_class = serializers.notarisedSerializer
    pagination_class = TableResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = filters.notarisedFilter
    ordering_fields = ['block_time', 'coin']
    ordering = ['-block_time', 'coin']


class notarisedCoinDailyViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = notarised_coin_daily.objects.all()
    serializer_class = serializers.notarisedCoinDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notarised_date', 'coin']
    ordering_fields = ['notarised_date', 'coin']
    ordering = ['-notarised_date', 'coin']


class notarisedCountDailyViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = notarised_count_daily.objects.all()
    serializer_class = serializers.notarisedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notarised_date', 'notary']
    ordering_fields = ['notarised_date', 'notary']
    ordering = ['-notarised_date', 'notary']


class notarisedTenureViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing coin notarisation tenure
    """
    queryset = notarised_tenure.objects.all()
    serializer_class = serializers.notarisedTenureSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['coin', 'season']
    ordering_fields = ['coin', 'season']
    ordering = ['-season', 'coin']


# class notaryVoteViewSet(viewsets.ModelViewSet):


class rewardsTxViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = rewards_tx.objects.all()
    serializer_class = serializers.rewardsTxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = filters.rewardsFilter
    ordering_fields = ['block_height','rewards_value']
    ordering = ['-block_height']


class scoringEpochsViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = scoring_epochs.objects.all()
    serializer_class = serializers.scoringEpochsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['season','server']
    ordering_fields = ['season','server', 'epoch']
    ordering = ['-season', 'epoch', 'server']


class coinNtxSeasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing coin ntx season stats
    """
    queryset = coin_ntx_season.objects.all()
    serializer_class = serializers.coinNtxSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['season', 'coin']
    ordering_fields = ['season', 'coin']
    ordering = ['-season', 'coin']


class notaryNtxSeasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notary ntx season stats
    """
    queryset = notary_ntx_season.objects.all()
    serializer_class = serializers.notaryNtxSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['season', 'notary']
    ordering_fields = ['season', 'notary']
    ordering = ['-season', 'notary']


class serverNtxSeasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing server ntx season stats
    """
    queryset = server_ntx_season.objects.all()
    serializer_class = serializers.serverNtxSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['season', 'server']
    ordering_fields = ['season', 'server']
    ordering = ['-season', 'server']


# class swapsViewSet(viewsets.ModelViewSet):


# class swapsFailedViewSet(viewsets.ModelViewSet):


class notaryVoteViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = notary_vote.objects.all()
    serializer_class = serializers.notaryVoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['year', 'candidate']
    ordering_fields = ['candidate', 'votes', 'block_time']
    ordering = ['-block_time', 'candidate']