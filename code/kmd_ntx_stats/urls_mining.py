from django.urls import path
from kmd_ntx_api import mining_views
from kmd_ntx_api import mining_api

frontend_mining_urls = [
    path('mining_24hrs/',
          mining_views.mining_24hrs_view,
          name='mining_24hrs_view'),

    path('mining_overview/',
          mining_views.mining_overview_view,
          name='mining_overview_view'),

    path('notary_last_mined/',
          mining_views.notary_last_mined_view,
          name='notary_last_mined_view'),

    path('notary_mining/<str:notary>/',
          mining_views.notary_mining_view,
          name='notary_mining_view'),

    path('notary_mining/',
          mining_views.notary_mining_view,
          name='notary_mining_view'),
    ]

api_mining_urls = [
    path('api/mining/notary_mining/',
          mining_api.notary_mining_api,
          name='notary_mining_api'),

    path('api/info/nn_mined_4hrs_count/',
          mining_api.nn_mined_4hrs_api,
          name='nn_mined_4hrs_api'),

    path('api/mining/mining_24hrs/',
          mining_api.mining_24hrs_api,
          name='mining_24hrs_api'),
    
    path('api/info/mined_count_daily/',
          mining_api.mined_count_daily_by_name,
          name='mined_count_daily_by_name'),

    path('api/info/mined_count_season/',
          mining_api.mined_count_season_by_name,
          name='mined_count_season_by_name'),
    ]