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

    # REVIEW? DEPRECATED?
    path('review/funding/',
          views_page.funding,
          name='funding'),
    
    path('review/funds_sent/',
          views_page.funds_sent,
          name='funds_sent'),

    path('sitemap/',
          views_page.sitemap,
          name='sitemap'),

    path('test_component/',
          views_page.test_component,
          name='test_component'),

]