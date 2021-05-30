from django.urls import path
#from kmd_ntx_api import views_stats
from kmd_ntx_api import api_stats

# STATS VIEWS
frontend_stats_urls = [
]

# API STATS V2
api_stats_urls = [

    path('api/swaps/swaps_gui_stats/',
          api_stats.swaps_gui_stats,
          name='swaps_gui_stats'),

    path('api/swaps/swaps_pubkey_stats/',
          api_stats.swaps_pubkey_stats,
          name='swaps_pubkey_stats'),

]