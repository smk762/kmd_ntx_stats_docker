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

    path('api/graph/mm2gui/',
         api_graph.mm2gui_piechart,
         name='mm2gui_piechart'),

    path('api/graph/rewards_xy_data/',
         api_graph.rewards_xy_data,
         name='rewards_xy_data'),

    path('api/graph/mined_xy_data/',
         api_graph.mined_xy_data,
         name='mined_xy_data'),

    path('api/graph/production_xy_data/',
         api_graph.production_xy_data,
         name='production_xy_data'),

    path('api/graph/supply_xy_data/',
         api_graph.supply_xy_data,
         name='supply_xy_data')
]
