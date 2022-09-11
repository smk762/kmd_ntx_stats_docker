from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from kmd_ntx_api import views_api
from kmd_ntx_api import api_tools
from kmd_ntx_api import api_graph

from kmd_ntx_stats.urls_atomicdex import frontend_atomicdex_urls, api_atomicdex_urls
from kmd_ntx_stats.urls_source import source_router
from kmd_ntx_stats.urls_csv import api_csv_urls
from kmd_ntx_stats.urls_graph import api_graph_urls
from kmd_ntx_stats.urls_info import api_info_urls
from kmd_ntx_stats.urls_status import api_status_urls
from kmd_ntx_stats.urls_table import frontend_table_urls, api_table_urls
from kmd_ntx_stats.urls_wallet import api_wallet_urls
from kmd_ntx_stats.urls_docs import doc_urls
from kmd_ntx_stats.urls_community import frontend_community_urls
from kmd_ntx_stats.urls_page import frontend_page_urls
from kmd_ntx_stats.urls_coin import frontend_coin_urls, api_coins_urls
from kmd_ntx_stats.urls_ntx import frontend_ntx_urls, api_ntx_urls
from kmd_ntx_stats.urls_tool import frontend_tool_urls, api_tool_urls
from kmd_ntx_stats.urls_mining import frontend_mining_urls, api_mining_urls
from kmd_ntx_stats.urls_testnet import frontend_testnet_urls, api_testnet_urls

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

    path('api/info/sidebar_links/',
          views_api.api_sidebar_links,
          name='api_sidebar_links'),

    path('api/info/split_summary_api/',
          views_api.split_summary_api,
          name='split_summary_api'),
    
]

url_lists = [
    frontend_ntx_urls, api_ntx_urls,
    frontend_tool_urls, api_tool_urls,
    frontend_coin_urls, api_coins_urls,
    frontend_table_urls, api_table_urls,
    frontend_mining_urls, api_mining_urls,
    frontend_testnet_urls, api_testnet_urls,
    frontend_atomicdex_urls, api_atomicdex_urls,
    frontend_page_urls,
    frontend_community_urls,
    api_csv_urls, api_graph_urls,
    api_info_urls, api_status_urls,
    api_wallet_urls, doc_urls    
]

for i in url_lists:
  urlpatterns += i

if settings.DEBUG:
    from django.conf.urls.static import static
    import debug_toolbar
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]