from django.urls import path
from kmd_ntx_api import views_mm2
from kmd_ntx_api import api_mm2

# mm2 VIEWS
frontend_mm2_urls = [
    path('mm2/orderbook/',
         views_mm2.orderbook_view,
         name='orderbook_view'),

    path('mm2/bestorders/',
         views_mm2.bestorders_view,
         name='bestorders_view'),

    path('mm2/last_200_swaps/',
         views_mm2.last200_swaps_view,
         name='last200_swaps_view'),

    path('mm2/last_200_failed_swaps/',
         views_mm2.last200_failed_swaps_view,
         name='last200_failed_swaps_view'),
    
    path('mm2/version_by_hour/',
         views_mm2.version_by_hour,
         name='version_by_hour'),
]


# API mm2 V2
api_mm2_urls = [
    path('api/mm2/version_stats/',
         api_mm2.nn_mm2_stats_api,
         name='nn_mm2_stats_api'),

    path('api/mm2/version_stats_by_hour/',
         api_mm2.nn_mm2_stats_by_hour_api,
         name='nn_mm2_stats_by_hour_api'),



    path('api/mm2/orderbook/',
         api_mm2.orderbook_api,
         name='orderbook_api'),

    path('api/mm2/bestorders/',
         api_mm2.bestorders_api,
         name='bestorders_api'),

    path('api/mm2/failed_swap/',
         api_mm2.failed_swap_api,
         name='failed_swap_api'),

    path('api/mm2/last_200_swaps/',
         api_mm2.last_200_swaps_api,
         name='last_200_swaps_api'),

    path('api/mm2/last_200_failed_swaps/',
         api_mm2.last_200_failed_swaps_api,
         name='last_200_failed_swaps_api'),
]
