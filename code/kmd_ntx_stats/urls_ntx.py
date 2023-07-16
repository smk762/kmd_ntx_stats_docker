from django.urls import path
from kmd_ntx_api import ntx_views
from kmd_ntx_api import ntx_api


frontend_ntx_urls = [
      path('notary_profile/',
            ntx_views.notary_profile_view,
            name='notary_profile_index_view'),

      path('notary_profile/<str:notary>/',
            ntx_views.notary_profile_view,
            name='notary_profile_view'),

      path('coin_profile/',
            ntx_views.coin_profile_view,
            name='coin_profile_index_view'),

      path('coin_profile/<str:coin>/',
            ntx_views.coin_profile_view,
            name='coin_profile_view'),

      path('ntx_scoreboard/',
            ntx_views.ntx_scoreboard_view,
            name='ntx_scoreboard_view'),

      path('ntx_scoreboard_24hrs/',
            ntx_views.ntx_scoreboard_24hrs_view,
            name='ntx_scoreboard_24hrs_view'),

      path('atomicdex/seednode_version/',
            ntx_views.seednode_version_view,
            name='seednode_version_view'),

      path('coins_last_ntx/',
            ntx_views.coins_last_ntx_view,
            name='coins_last_ntx_view'),

      path('notarised_24hrs/',
            ntx_views.notarised_24hrs_view,
            name='notarised_24hrs_view'),

      path('notarised_tenure/',
            ntx_views.notarised_tenure_view,
            name='notarised_tenure_view'),

      path('notarisation/',
            ntx_views.notarisation_view,
            name='notarisation_view'),

      path('tools/notaryfaucet/',
            ntx_views.notaryfaucet_view,
            name='notaryfaucet_view'),

      # Detail pages, not in navbar
      path('notary_epoch_scores/',
            ntx_views.notary_epoch_scores_view,
            name='notary_epoch_scores_view'),

      path('notary_epoch_coin_notarised/',
            ntx_views.notary_epoch_coin_notarised_view,
            name='notary_epoch_coin_notarised_view'),

      path('notary_coin_notarised/',
            ntx_views.notary_coin_notarised_view,
            name='notary_coin_notarised_view'),
]

api_ntx_urls = [
    path('api/ntx/notarised_date/',
          ntx_api.notarised_date_api,
          name='notarised_date_api'),

    path('api/ntx/season_stats/',
          ntx_api.season_stats_sorted_api,
          name='season_stats_sorted_api'),

    path('api/ntx/24hr_stats/',
          ntx_api.daily_stats_sorted_api,
          name='daily_stats_sorted_api'),

    path('api/ntx/notarised_tenure/',
          ntx_api.ntx_tenture_api,
          name='ntx_tenture_api'),

]