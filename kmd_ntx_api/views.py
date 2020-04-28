from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from kmd_ntx_api.serializers import *
from kmd_ntx_api.models import *
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response

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
    queryset = User.objects.all().order_by('-date_joined')
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
    queryset = mined.objects.all().order_by('block')
    serializer_class = MinedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None

class ntxViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations table data
    """
    queryset = notarised.objects.all().order_by('block_ht')
    serializer_class = ntxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class MinedCountViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing mining max and sum data
    """
    q = mined_count.objects.all().order_by("-timestamp").first()
    queryset = mined_count.objects.filter(timestamp=q.timestamp)
    serializer_class = MinedCountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None


class ntxCountViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations count data
    """
    q = notarised_count.objects.all().order_by("-timestamp").first()
    queryset = notarised_count.objects.filter(timestamp=q.timestamp)
    serializer_class = ntxCountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None

class ntxChainsCountViewSet(viewsets.ModelViewSet):
    """
    API endpoint showing notarisations count data
    """
    q = notarised_count.objects.all().order_by("-timestamp").first()
    queryset = notarised_count.objects.filter(timestamp=q.timestamp)
    serializer_class = ntxChainsCountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None
'''
class lastMined(APIView):
    """
    List timestamp of each Notary's most recent mined KMD block.

    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        """
        Return last mined timestamp of all Notaries.
        """
        nn_last_mined = {}
        for nn in s3_notaries:
            q = mined.objects.filter(name=nn).order_by('-block').first()
            nn_last_mined.update({nn:q.blocktime})
        usernames = [user.username for user in User.objects.all()]
        return Response(usernames)
'''
@api_view()
def hello_world(request):
    return Response({"message": "Hello, world!"})
