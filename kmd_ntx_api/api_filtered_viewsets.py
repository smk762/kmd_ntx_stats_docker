#!/usr/bin/env python3

from django_filters.rest_framework import DjangoFilterBackend

from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework import permissions, viewsets

from kmd_ntx_api.serializers import *
from kmd_ntx_api.models import *
from kmd_ntx_api.lib_info import *
from kmd_ntx_api.lib_api_filtered import *


class addresses_filter(viewsets.ViewSet):
    """
    Returns Source Notary Node addresses data \n
    Default filter returns current NN Season \n

    """
    serializer_class = AddressesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        filters = self.serializer_class.Meta.fields
        resp = get_addresses_data_api(request)
        return JsonResponse({
            "count":len(resp),
            "filters":filters,
            "results":resp
            })


class balances_filter(viewsets.ViewSet):
    """
    API endpoint showing notary balances
    """
    serializer_class = BalancesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_balances_data_api(request)
        return JsonResponse({
            "count":len(resp),
            "filters":filters,
            "results":resp
            })

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
        filters = self.serializer_class.Meta.fields
        resp = get_coins_data_api(request)      
        return JsonResponse({
            "count":len(resp),
            "filters":filters,
            "results":resp
            })

class electrums_filter(viewsets.ViewSet):  # TODO: add coin type filter

    """
    Returns explorers sourced from coins repo
    """    
    serializer_class = ElectrumsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        filters = self.serializer_class.Meta.fields
        if 'chain' in request.GET:
            resp = get_electrums_data_api(request.GET["chain"])
        else:
            resp = get_electrums_data_api()
        return JsonResponse({
            "count":len(resp),
            "filters":filters,
            "results":resp
            })

class electrums_ssl_filter(viewsets.ViewSet):  # TODO: add coin type filter

    """
    Returns explorers sourced from coins repo
    """    
    serializer_class = ElectrumsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        filters = self.serializer_class.Meta.fields
        if 'chain' in request.GET:
            resp = get_electrums_ssl_data_api(request.GET["chain"])
        else:
            resp = get_electrums_ssl_data_api()
        return JsonResponse({
            "count":len(resp),
            "filters":filters,
            "results":resp
            })

class explorers_filter(viewsets.ViewSet):  # TODO: add coin type filter

    """
    Returns explorers sourced from coins repo
    """    
    serializer_class = ExplorersSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        filters = self.serializer_class.Meta.fields
        if 'chain' in request.GET:
            resp = get_explorers_data_api(request.GET["chain"])
        else:
            resp = get_explorers_data_api()
        return JsonResponse({
            "count":len(resp),
            "filters":filters,
            "results":resp
            })

class launch_params_filter(viewsets.ViewSet):  # TODO: add coin type filter

    """
    Returns explorers sourced from coins repo
    """    
    serializer_class = LaunchParamsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        filters = self.serializer_class.Meta.fields

        chain = None
        if 'chain' in request.GET:
            chain = request.GET["chain"]
        
        resp = get_launch_params_data_api(chain)
        return JsonResponse({
            "count":len(resp),
            "filters":filters,
            "results":resp
            })

class daemon_cli_filter(viewsets.ViewSet):  # TODO: add coin type filter

    """
    Returns explorers sourced from coins repo
    """    
    serializer_class = DaemonCliSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        filters = self.serializer_class.Meta.fields

        chain = None
        if 'chain' in request.GET:
            chain = request.GET["chain"]
        
        resp = get_daemon_cli_data_api(chain)
        return JsonResponse({
            "count":len(resp),
            "filters":filters,
            "results":resp
            })



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
        filters = self.serializer_class.Meta.fields
        resp = get_mined_count_season_data_api(request)
        api_resp = wrap_api(resp, filters)
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
        filters = self.serializer_class.Meta.fields
        resp = get_mined_count_daily_data_api(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

class notarised_chain_season_filter(viewsets.ViewSet):
    """
    API endpoint showing notary mined blocks
    """
    serializer_class = NotarisedChainSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_notarised_chain_season_data_api(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

class notarised_count_season_filter(viewsets.ViewSet):
    """
    API endpoint showing notary mined blocks
    """
    serializer_class = NotarisedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_notarised_count_season_data_api(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

class notarised_chain_date_filter(viewsets.ViewSet):
    """
    API endpoint showing notary mined blocks. \n
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
        filters = self.serializer_class.Meta.fields
        resp = get_notarised_chain_daily_data_api(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

class notarised_count_date_filter(viewsets.ViewSet):
    """
    API endpoint showing notary mined blocks
    """
    serializer_class = NotarisedCountDailySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_notarised_count_date_data_api(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)


#TODO: Review this - A little different to other filtered viewsets...
class notary_nodes_filter(viewsets.ViewSet):
    """
    API endpoint listing notary names for each season
    """
    serializer_class = NNSocialSerializer
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
        season = get_season()
        if "season" in request.GET:
            season = request.GET["season"]
        notary_list = get_notary_list(season)
        api_resp = wrap_api(notary_list)
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
        filters = self.serializer_class.Meta.fields
        resp = get_rewards_data_api(request)
        api_resp = wrap_api(resp, filters)
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
        filters = self.serializer_class.Meta.fields
        resp = get_nn_social_data_api(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

# TODO: add to lib_api_filtered
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
        last_ntx_data = get_last_notarised_data().values()
        return Response(last_ntx_data)


# TODO: add to lib_api_filtered
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
        last_btc_ntx_data = get_last_btc_notarised_data().values()
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
        filters = self.serializer_class.Meta.fields
        resp = get_notarised_tenure_data_api(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)


class notarised_filter(viewsets.ViewSet):
    """
    Returns chain notarisation tenure, nested by Season > Chain \n
    Default filter returns current NN Season \n

    """
    serializer_class = NotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        
        filters = self.serializer_class.Meta.fields
        resp = get_notarised_data_api(request)

        # TODO: include custom filters in wrap_api resp
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)
