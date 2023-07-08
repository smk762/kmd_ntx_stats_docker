from django.urls import path
from kmd_ntx_api import views_stats

# API GRAPH V2
frontend_stats_urls = [

    path('stats/rewards_scatterplot/',
         views_stats.rewards_scatterplot_view,
         name='rewards_scatterplot_view'),

    path('stats/production_graph/',
         views_stats.block_production_view,
         name='block_production_view')
]
api_stats_urls = [

]
