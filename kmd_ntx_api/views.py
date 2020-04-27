from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from kmd_ntx_api.serializers import *
from kmd_ntx_api.models import *
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response

def get_cursor():
    conn = psycopg2.connect(
      host='localhost',
      user='postgres',
      password='postgres',
      port = "7654",
      database='postgres'
    )
    cursor = conn.cursor()
    return cursor

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

@api_view()
def hello_world(request):
    return Response({"message": "Hello, world!"})
