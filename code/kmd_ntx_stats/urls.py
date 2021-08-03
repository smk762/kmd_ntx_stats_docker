from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from kmd_ntx_api import views_api
from kmd_ntx_api import api_tools
from kmd_ntx_api import api_graph
from kmd_ntx_api import api_stats
from kmd_ntx_stats.urls_source import source_router
from kmd_ntx_stats.urls_status import api_status_urls
from kmd_ntx_stats.urls_stats import api_stats_urls, frontend_stats_urls
from kmd_ntx_stats.urls_graph import api_graph_urls
from kmd_ntx_stats.urls_info import api_info_urls
from kmd_ntx_stats.urls_docs import doc_urls
from kmd_ntx_stats.urls_mm2 import frontend_mm2_urls, api_mm2_urls
from kmd_ntx_stats.urls_table import api_table_urls
from kmd_ntx_stats.urls_community import frontend_community_urls
from kmd_ntx_stats.urls_wallet import api_wallet_urls

from kmd_ntx_stats.urls_page import frontend_page_urls
from kmd_ntx_stats.urls_tool import frontend_tool_urls, api_tool_urls

handler400 = 'kmd_ntx_api.views_error.error_400'
handler403 = 'kmd_ntx_api.views_error.error_403'
handler404 = 'kmd_ntx_api.views_error.error_404'
handler500 = 'kmd_ntx_api.views_error.error_500'
handler502 = 'kmd_ntx_api.views_error.error_502'


# /api/info/{endpoint} will be deprecated
# /api/table/{endpoint} returns full list of data, with filters enforced
# /api/graph/{endpoint} returns data formated with graph specific fileds (labels, colors etc)
# /api/source/{endpoint} returns paginated full list of data
# /api/{category}/{endpoint} returns formated data dict


# Graphs

urlpatterns = [

    path('api/source/',
         include(source_router.urls)),

    path('admin/',
          admin.site.urls),

    path('api-auth/',
         include('rest_framework.urls',
            namespace='rest_framework')),

    # API views (simple)
    # TODO: Deprecate or merge into other url files

    path('api/info/chain_sync/',
          views_api.api_chain_sync,
          name='api_chain_sync'),

    path('api/info/nn_mined_4hrs_count/',
          views_api.nn_mined_4hrs_api,
          name='nn_mined_4hrs_api'),

    path('api/info/sidebar_links/',
          views_api.api_sidebar_links,
          name='api_sidebar_links'),

    path('api/info/split_summary_api/',
          views_api.split_summary_api,
          name='split_summary_api'),
    
    path('api/testnet/totals/',
          views_api.api_testnet_totals,
          name='api_testnet_totals'),

]

urlpatterns += frontend_page_urls
urlpatterns += frontend_tool_urls
urlpatterns += api_graph_urls
urlpatterns += api_info_urls
urlpatterns += api_status_urls
urlpatterns += api_stats_urls
urlpatterns += frontend_stats_urls
urlpatterns += api_table_urls
urlpatterns += api_tool_urls
urlpatterns += api_wallet_urls
urlpatterns += doc_urls
urlpatterns += api_mm2_urls
urlpatterns += frontend_mm2_urls
urlpatterns += frontend_community_urls