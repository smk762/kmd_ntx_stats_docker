from django.urls import path
from kmd_ntx_api import views_page

frontend_page_urls = [

    path('',
          views_page.dash_view,
          name='root'),
    path('index',
          views_page.dash_view,
          name='index'),

    path('dash/',
          views_page.dash_view,
          name='dash_index'),

    path('dash/<str:dash_name>/',
          views_page.dash_view,
          name='dash_view'),

    path('test_component/',
          views_page.test_component,
          name='test_component'),

]