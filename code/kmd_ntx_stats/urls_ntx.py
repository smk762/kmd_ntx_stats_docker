from django.urls import path
from kmd_ntx_api import views_ntx
from kmd_ntx_api import api_ntx

frontend_ntx_urls = [
    path('notary_profile/',
          views_ntx.notary_profile_view,
          name='notary_profile_index_view'),

    path('notary_profile/<str:notary>/',
          views_ntx.notary_profile_view,
          name='notary_profile_view'),

    path('ntx_scoreboard/',
          views_ntx.ntx_scoreboard,
          name='ntx_scoreboard_view'),

    path('ntx_scoreboard_24hrs/',
          views_ntx.ntx_scoreboard_24hrs,
          name='ntx_scoreboard_24hrs_view'),

    path('atomicdex/seednode_version/',
         views_ntx.seednode_version_view,
         name='seednode_version_view'),

    path('notary_epoch_scores/',
          views_ntx.notary_epoch_scores_view,
          name='notary_epoch_scores_view'),
    
    path('notary_epoch_coin_notarised/',
          views_ntx.notary_epoch_coin_notarised_view,
          name='notary_epoch_coin_notarised_view'),
    
    path('notary_coin_notarised/',
          views_ntx.notary_coin_notarised_view,
          name='notary_coin_notarised_view'),

    path('notarised_24hrs/',
          views_ntx.notarised_24hrs,
          name='notarised_24hrs_view'),

    path('notarisation/',
          views_ntx.notarisation_view,
          name='notarisation_view'),
]

api_ntx_urls = [
    path('api/ntx/notarised_date/',
          api_ntx.notarised_date_api,
          name='notarised_date_api'),

    path('api/ntx/season_stats/',
          api_ntx.season_stats_sorted_api,
          name='season_stats_sorted_api'),

    path('api/ntx/24hr_stats/',
          api_ntx.daily_stats_sorted_api,
          name='daily_stats_sorted_api'),

    path('api/ntx/notarised_tenure/',
          api_ntx.ntx_tenture_api,
          name='ntx_tenture_api'),

    path('api/ntx/notary_fee_efficiency/',
          api_ntx.notary_fee_efficiency_api,
          name='notary_fee_efficiency_api'),
]