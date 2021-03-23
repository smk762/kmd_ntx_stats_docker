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
    serializer_class = AddressesSerializer
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
    serializer_class = BalancesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['chain', 'notary', 'season', 'node']
    ordering_fields = ['chain', 'notary', 'season']
    ordering = ['-season', 'notary', 'chain']

class coinsViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = coins.objects.all()
    serializer_class = CoinsSerializer
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
    serializer_class = LastNotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary', 'chain', 'season']
    ordering_fields = ['season', 'notary', 'chain']
    ordering = ['season', 'notary', 'chain']

class lastBtcNtxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = last_btc_notarised.objects.all()
    serializer_class = LastBtcNotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary']
    ordering_fields = ['notary']
    ordering = ['notary']

class MinedViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing mining table data
    """
    queryset = mined.objects.all()
    serializer_class = MinedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = minedFilter
    #filterset_fields =  ['block_height', 'block_time', 'block_datetime',
    #                     'value', 'address', 'name', 'txid', 'season']
    ordering_fields = ['block_height', 'address', 'season', 'name']
    ordering = ['-block_height']

class MinedCountSeasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing mining table data
    """
    queryset = mined_count_season.objects.all()
    serializer_class = MinedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary', 'season']
    ordering_fields = ['block_height']
    ordering = ['notary']

class MinedCountDayViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing mining table data
    """
    queryset = mined_count_daily.objects.all()
    serializer_class = MinedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['mined_date', 'notary']
    ordering_fields = ['mined_date','notary']
    ordering = ['-mined_date','notary']

class nn_socialViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing Node Operator social links
    """
    queryset = nn_social.objects.all()
    serializer_class = NNSocialSerializer
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
    serializer_class = NotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ntxFilter
    ordering_fields = ['block_time', 'chain']
    ordering = ['-block_time', 'chain']

class ntxCountSeasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised_count_season.objects.all()
    serializer_class = NotarisedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['season', 'notary']
    ordering_fields = ['season', 'notary']
    ordering = ['-season', 'notary']

class ntxChainSeasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised_chain_season.objects.all()
    serializer_class = NotarisedChainSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['chain', 'season']
    ordering_fields = ['block_height']
    ordering = ['-block_height']

class ntxCountDateViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised_count_daily.objects.all()
    serializer_class = NotarisedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notarised_date', 'notary']
    ordering_fields = ['notarised_date', 'notary']
    ordering = ['-notarised_date', 'notary']

class ntxChainDateViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised_chain_daily.objects.all()
    serializer_class = NotarisedChainDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notarised_date', 'chain']
    ordering_fields = ['notarised_date', 'chain']
    ordering = ['-notarised_date', 'chain']

class rewardsViewSet(viewsets.ModelViewSet):
    """
    API pending KMD rewards for notaries
    """
    queryset = rewards.objects.all()
    serializer_class = RewardsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notary','address']
    ordering_fields = ['notary','address']
    ordering = ['notary']

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

# Auto filterable views

class addresses_filter(viewsets.ViewSet):
    """
    Returns Notary Node addresses, nested by Name > Season > Chain \n
    Default filter returns current NN Season \n

    """
    serializer_class = AddressesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        api_resp = get_addresses_data(request)
        return Response(api_resp)

class balances_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node balances
    """
    serializer_class = BalancesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_balances_data(request)
        return Response(api_resp)

class coins_filter(viewsets.ViewSet):
    """
    API endpoint showing coininfo from coins and dpow repositories
    """
    serializer_class = CoinsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_coins_data(request)
        return Response(api_resp)

class explorers_filter(viewsets.ViewSet):  # TODO: add coin type filter

    """
    Returns explorers sourced from coins repo
    """    
    serializer_class = ExplorersSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        resp = {}
        coins_data = coins.objects.all().values('chain','explorers')
        for item in coins_data:
            explorers = item['explorers']
            if len(explorers) > 0:
                chains = item['chains']
                resp.update({chain:explorers})
        return Response(resp)

class mined_count_season_filter(viewsets.ViewSet):
    """
    API endpoint showing mined blocks by notary/address (minimum 10 blocks mined)
    """
    serializer_class = MinedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_mined_count_season_data(request)
        return Response(api_resp)

class mined_count_date_filter(viewsets.ViewSet):
    """
    API endpoint showing mined blocks by notary/address (minimum 10 blocks mined) \n
    Defaults to todays date.
    """
    serializer_class = MinedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        api_resp = get_mined_count_daily_data(request)
        return Response(api_resp)

class mined_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks. 
    Use filters or be patient, this is a big dataset.
    """
    serializer_class = MinedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        api_resp = get_mined_data(request)
        return Response(api_resp)

class notarised_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = NotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        api_resp = get_notarised_data(request)
        return Response(api_resp)

class notarised_chain_season_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = NotarisedChainSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_notarised_chain_season_data(request)
        return Response(api_resp)

class notarised_count_season_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = NotarisedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_notarised_count_season_data(request)
        return Response(api_resp)

class notarised_chain_date_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks. \n
    Defaults to filtering by todays date \n
    """
    serializer_class = NotarisedChainDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_notarised_chain_daily_data(request)
        return Response(api_resp)

class notarised_count_date_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks
    """
    serializer_class = NotarisedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_notarised_count_date_data(request)
        return Response(api_resp)

class notary_nodes_filter(viewsets.ViewSet):
    """
    API endpoint listing notary names for each season
    """
    serializer_class = AddressesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['season']
    ordering_fields = ['season', 'notary']
    ordering = ['-season', 'notary']

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        season = get_season(int(time.time()))
        notaries_list = get_notary_list(season)
        api_resp = wrap_api(notaries_list)

        return Response(api_resp)

class notary_rewards_filter(viewsets.ViewSet):
    """
    API endpoint showing notary rewards pending
    """
    serializer_class = RewardsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        api_resp = get_rewards_data(request)
        return Response(api_resp)

class notary_social_filter(viewsets.ViewSet):
    """
    API endpoint showing notary rewards pending
    """
    serializer_class = NNSocialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        nn_social_data = nn_social.objects.all().values()
        return Response(nn_social_data)

class last_ntx_filter(viewsets.ViewSet):
    """
    API endpoint showing notary rewards pending
    """
    serializer_class = LastNotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        last_ntx_data = last_notarised.objects.all().values()
        return Response(last_ntx_data)

class last_btc_ntx_filter(viewsets.ViewSet):
    """
    API endpoint showing notary rewards pending
    """
    serializer_class = LastBtcNotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        last_btc_ntx_data = last_btc_notarised.objects.all().values()
        return Response(last_btc_ntx_data)

class notarised_tenure_filter(viewsets.ViewSet):
    """
    Returns chain notarisation tenure, nested by Season > Chain \n
    Default filter returns current NN Season \n

    """
    serializer_class = ntxTenureSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        api_resp = get_ntx_tenure_data(request)
        return Response(api_resp)

class notarised_tenure_csv(viewsets.ViewSet):
    """
    Returns chain notarisation tenure, nested by Season > Chain \n
    Default filter returns current NN Season \n

    """
    serializer_class = ntxTenureSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        api_resp = get_ntx_tenure_data(request, "csv")
        return Response(api_resp)

