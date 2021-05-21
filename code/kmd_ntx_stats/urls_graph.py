from django.urls import path
from kmd_ntx_api import views_tool
from kmd_ntx_api import api_graph

# API GRAPH V2
api_graph_urls = [

    path('api/graph/balances/',
          api_graph.balances_graph,
          name='balances_graph'),

    path('api/graph/daily_ntx/',
          api_graph.daily_ntx_graph,
          name='daily_ntx_graph'),


]