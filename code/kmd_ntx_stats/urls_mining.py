from django.urls import path
from kmd_ntx_api import views_mining
from kmd_ntx_api import api_mining

frontend_mining_urls = [
    path('mining_24hrs/',
          views_mining.mining_24hrs_view,
          name='mining_24hrs_view'),

    path('mining_overview/',
          views_mining.mining_overview_view,
          name='mining_overview_view'),

    path('notary_last_mined/',
          views_mining.notary_last_mined_view,
          name='notary_last_mined_view'),

    path('notary_mining/<str:notary>/',
          views_mining.notary_mining_view,
          name='notary_mining_view'),

    path('notary_mining/',
          views_mining.notary_mining_view,
          name='notary_mining_view'),
    ]

api_mining_urls = [
    path('api/mining/notary_last_mined_table/',
          api_mining.notary_last_mined_table,
          name='notary_last_mined_table'),

    path('api/mining/notary_mining/',
          api_mining.notary_mining_api,
          name='notary_mining_api'),

    path('api/info/nn_mined_4hrs_count/',
          api_mining.nn_mined_4hrs_api,
          name='nn_mined_4hrs_api'),

    path('api/info/mined_count_daily/',
          api_mining.mined_count_daily_by_name,
          name='mined_count_daily_by_name'),

    path('api/info/mined_count_season/',
          api_mining.mined_count_season_by_name,
          name='mined_count_season_by_name'),
    ]