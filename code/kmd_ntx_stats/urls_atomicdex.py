from django.urls import path
from kmd_ntx_api import atomicdex_views
from kmd_ntx_api import atomicdex_views_unlisted
from kmd_ntx_api import atomicdex_api

# AtomicDEX VIEWS
frontend_atomicdex_urls = [

    path('atomicdex/activation_commands/',
         atomicdex_views.activation_commands_view,
         name='activation_commands_view'),

    path('atomicdex/batch_activation_form/',
         atomicdex_views.batch_activation_form_view,
         name='batch_activation_form_view'),

    path('atomicdex/bestorders/',
         atomicdex_views.bestorders_view,
         name='bestorders_view'),

    path('atomicdex/electrum_status/',
         atomicdex_views.electrum_status_view,
         name='electrum_status_view'),

    path('atomicdex/last_200_swaps/',
         atomicdex_views.last_200_swaps_view,
         name='last_200_swaps_view'),

    path('atomicdex/gui_stats/',
          atomicdex_views_unlisted.gui_stats_view,
          name='gui_stats_view'),

    path('atomicdex/last_200_failed_swaps/',
         atomicdex_views_unlisted.last_200_failed_swaps_view,
         name='last_200_failed_swaps_view'),
    
    path('atomicdex/makerbot_config_form/',
          atomicdex_views.makerbot_config_form_view,
          name='makerbot_config_form_view'),

    path('atomicdex/orderbook/',
         atomicdex_views.orderbook_view,
         name='orderbook_view'),

]

# AtomicDEX API V2
api_atomicdex_urls = [

    path('api/atomicdex/seednode_version_date_table/',
         atomicdex_api.seednode_version_date_table_api,
         name='seednode_version_date_table_api'),

    path('api/atomicdex/seednode_version_month_table/',
         atomicdex_api.seednode_version_month_table_api,
         name='seednode_version_month_table_api'),

    path('api/atomicdex/seednode_version_score_total/',
         atomicdex_api.seednode_version_score_total_api,
         name='seednode_version_score_total_api'),

    path('api/atomicdex/activation_commands/',
          atomicdex_api.activation_commands_api,
          name='activation_commands_api'),

    path('api/atomicdex/coin_activation_commands/',
          atomicdex_api.coin_activation_commands_api,
          name='coin_activation_commands_api'),

    path('api/atomicdex/orderbook/',
         atomicdex_api.orderbook_api,
         name='orderbook_api'),

    path('api/table/orderbook/',
         atomicdex_api.orderbook_table_api,
         name='orderbook_table_api'),

    path('api/atomicdex/bestorders/',
         atomicdex_api.bestorders_api,
         name='bestorders_api'),

    path('api/atomicdex/failed_swap/',
         atomicdex_api.failed_swap_api,
         name='failed_swap_api'),

    path('api/atomicdex/last_200_swaps/',
         atomicdex_api.last_200_swaps_api,
         name='last_200_swaps_api'),

    path('api/atomicdex/last_200_failed_swaps/',
         atomicdex_api.last_200_failed_swaps_api,
         name='last_200_failed_swaps_api'),

    path('api/private/atomicdex/last_200_failed_swaps/',
         atomicdex_api.last_200_failed_swaps_private_api,
         name='last_200_failed_swaps_private_api'),

    path('api/atomicdex/swaps_gui_stats/',
          atomicdex_api.swaps_gui_stats_api,
          name='swaps_gui_stats_api')

]
