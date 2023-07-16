from django.urls import path
from code.kmd_ntx_api import page_views

frontend_page_urls = [

    path('',
          page_views.dash_view,
          name='root'),
    path('index',
          page_views.dash_view,
          name='index'),

    path('dash/',
          page_views.dash_view,
          name='dash_index'),

    path('dash/<str:dash_name>/',
          page_views.dash_view,
          name='dash_view'),

    path('test_component/',
          page_views.test_component,
          name='test_component'),

]