from django.urls import path
from kmd_ntx_api import views_ntx
from kmd_ntx_api import api_ntx

frontend_ntx_urls = [
    path('notary_profile/',
          views_ntx.notary_profile_view,
          name='notary_profile_index_view'),

    path('notary/notary_coin_ntx_detail/',
          views_ntx.notary_coin_ntx_detail_view,
          name='notary_coin_ntx_detail_view'),    

    path('notary_profile/<str:notary>/',
          views_ntx.notary_profile_view,
          name='notary_profile_view'),

    path('notary_mining/<str:notary>/',
          views_ntx.notary_mining_view,
          name='notary_mining_view'),

    path('ntx_scoreboard/',
          views_ntx.ntx_scoreboard,
          name='ntx_scoreboard_view'),

    path('ntx_scoreboard_24hrs/',
          views_ntx.ntx_scoreboard_24hrs,
          name='ntx_scoreboard_24hrs_view'),

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

    path('notary_mining/',
          views_ntx.notary_mining_view,
          name='notary_mining_view'),
]

api_ntx_urls = [
    path('api/ntx/notarised_date',
          api_ntx.notarised_date_api,
          name='notarised_date_api'),
]