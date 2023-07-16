from django.urls import path
from kmd_ntx_api import tools_views
from kmd_ntx_api import graph_api

# API GRAPH V2
api_graph_urls = [

    path('api/graph/balances/',
         graph_api.balances_graph,
         name='balances_graph'),

    path('api/graph/daily_ntx/',
         graph_api.daily_ntx_graph,
         name='daily_ntx_graph'),

    path('api/graph/mm2gui/',
         graph_api.mm2gui_piechart,
         name='mm2gui_piechart'),

    path('api/graph/mined_xy_data/',
         graph_api.mined_xy_data,
         name='mined_xy_data'),

    path('api/graph/supply_xy_data/',
         graph_api.supply_xy_data,
         name='supply_xy_data')
]
