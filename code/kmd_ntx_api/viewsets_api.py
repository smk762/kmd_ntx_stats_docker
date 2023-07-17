#!/usr/bin/env python3
from django.contrib.auth.models import User, Group
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework import permissions, viewsets
from rest_framework.pagination import PageNumberPagination

from kmd_ntx_api.models import addresses, balances, notarised, mined, coins, \
    coin_social, notarised_coin_daily, notarised_count_daily, nn_ltc_tx, \
    notary_last_ntx, coin_ntx_season, coin_last_ntx, mined_count_daily, \
    mined_count_season, seednode_version_stats, nn_btc_tx, nn_social, \
    notarised_tenure, rewards_tx, scoring_epochs, server_ntx_season, \
    notary_ntx_season, notary_candidates, notary_vote
from kmd_ntx_api.filters import notarisedFilter, minedFilter, seednodeVersionStatsFilter, \
    notarisedTenureFilter, rewardsFilter
from kmd_ntx_api.serializers import balancesSerializer, notarisedSerializer, \
    coinsSerializer, notarisedCoinDailySerializer, notarisedCountDailySerializer, \
    nnLtcTxSerializer, UserSerializer, GroupSerializer, addressesSerializer, \
    minedSerializer, coinSocialSerializer, notaryLastNtxSerializer, \
    coinLastNtxSerializer, minedCountDailySerializer, minedCountSeasonSerializer, \
    coinNtxSeasonSerializer, seednodeVersionStatsSerializer, nnBtcTxSerializer, \
    nnLtcTxSerializer, nnSocialSerializer, notarisedTenureSerializer, \
    scoringEpochsSerializer, rewardsTxSerializer, notaryNtxSeasonSerializer, \
    notaryVoteSerializer, notaryCandidatesSerializer, serverNtxSeasonSerializer

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
    serializer_class = balancesSerializer
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
    serializer_class = coinsSerializer
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
    serializer_class = coinSocialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['coin', 'season']
    ordering_fields = ['coin']
    ordering = ['coin']

class notaryLastNtxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing last coin notarisation for each notary
    """
    queryset = notary_last_ntx.objects.all()
    serializer_class = notaryLastNtxSerializer
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
    serializer_class = coinLastNtxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['season', 'coin']
    ordering_fields = ['season', 'coin']
    ordering = ['season', 'coin']


class minedViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = mined.objects.all()
    serializer_class = minedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = minedFilter
    ordering_fields = ['block_height', 'address', 'season', 'name']
    ordering = ['-block_height']


class minedCountDailyViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = mined_count_daily.objects.all()
    serializer_class = minedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['mined_date', 'notary']
    ordering_fields = ['mined_date','notary']
    ordering = ['-mined_date','notary']


class minedCountSeasonViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = mined_count_season.objects.all()
    serializer_class = minedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['name', 'season']
    ordering_fields = ['name']
    ordering = ['name']


class mm2VersionStatsViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing mm2 Version Stats table data
    """
    queryset = seednode_version_stats.objects.all()
    serializer_class = seednodeVersionStatsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = MassiveResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = seednodeVersionStatsFilter
    filterset_fields = ['name', 'season', 'version', 'score']
    ordering_fields = ['name', 'season', '-timestamp']
    ordering = ['name', 'season', '-timestamp']


class nnBtcTxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing Node Operator social links
    """
    queryset = nn_btc_tx.objects.all()
    serializer_class = nnBtcTxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary', 'season']
    ordering_fields = ['season', 'notary']
    ordering = ['-season', 'notary']


class nnLtcTxViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = nn_ltc_tx.objects.all()
    serializer_class = nnLtcTxSerializer
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
    serializer_class = nnSocialSerializer
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
    serializer_class = notarisedSerializer
    pagination_class = TableResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = notarisedFilter
    ordering_fields = ['block_time', 'coin']
    ordering = ['-block_time', 'coin']


class notarisedCoinDailyViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = notarised_coin_daily.objects.all()
    serializer_class = notarisedCoinDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notarised_date', 'coin']
    ordering_fields = ['notarised_date', 'coin']
    ordering = ['-notarised_date', 'coin']


class notarisedCountDailyViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = notarised_count_daily.objects.all()
    serializer_class = notarisedCountDailySerializer
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
    serializer_class = notarisedTenureSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = notarisedTenureFilter
    filterset_fields = ['coin', 'season']
    ordering_fields = ['coin', 'season']
    ordering = ['-season', 'coin']


# class notaryVoteViewSet(viewsets.ModelViewSet):


class rewardsTxViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = rewards_tx.objects.all()
    serializer_class = rewardsTxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = rewardsFilter
    ordering_fields = ['block_height','rewards_value']
    ordering = ['-block_height']


class scoringEpochsViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = scoring_epochs.objects.all()
    serializer_class = scoringEpochsSerializer
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
    serializer_class = coinNtxSeasonSerializer
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
    serializer_class = notaryNtxSeasonSerializer
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
    serializer_class = serverNtxSeasonSerializer
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
    serializer_class = notaryVoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['year', 'candidate', 'txid', 'block_height']
    ordering_fields = ['candidate', 'votes', 'block_time']
    ordering = ['-block_time', 'candidate']


class notaryCandidatesViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = notary_candidates.objects.all()
    serializer_class = notaryCandidatesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['year', 'name', 'season']
    ordering_fields = ['year', 'name', 'season']
    ordering = ['year', 'name', 'season']
