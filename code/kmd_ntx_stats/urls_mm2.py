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
]


# API mm2 V2
api_mm2_urls = [
    path('api/mm2/orderbook/',
          api_mm2.orderbook_api,
          name='orderbook_api'),

    path('api/mm2/bestorders/',
          api_mm2.bestorders_api,
          name='bestorders_api'),
]