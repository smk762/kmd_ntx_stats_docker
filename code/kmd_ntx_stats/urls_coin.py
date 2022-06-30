from django.urls import path
from kmd_ntx_api import views_coin
from kmd_ntx_api import api_mining

frontend_coin_urls = [
    path('coin_profile/',
          views_coin.coin_profile_view,
          name='coin_profile_index_view'),

    path('coin_profile/<str:coin>/',
          views_coin.coin_profile_view,
          name='coin_profile_view'),

    path('coins_last_ntx/',
          views_coin.coins_last_ntx,
          name='coins_last_ntx_view'),

    path('coin_notarised_24hrs/',
          views_coin.coin_notarised_24hrs_view,
          name='coin_notarised_24hrs'),

    path('notarised_tenure/',
          views_coin.notarised_tenure_view,
          name='notarised_tenure_view'),

    path('scoring_epochs/',
          views_coin.scoring_epochs_view,
          name='scoring_epochs_view'),    
    ]


api_coins_urls = [
    path('api/info/nn_mined_4hrs_count/',
          api_mining.nn_mined_4hrs_api,
          name='nn_mined_4hrs_api'),

    path('api/mining/mining_24hrs/',
          api_mining.mining_24hrs_api,
          name='mining_24hrs_api'),

    path('api/info/mined_count_daily/',
          api_mining.mined_count_daily_by_name,
          name='mined_count_daily_by_name'),

    path('api/info/mined_count_season/',
          api_mining.mined_count_season_by_name,
          name='mined_count_season_by_name'),
    ]