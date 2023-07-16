from django.urls import path
from kmd_ntx_api import table_views
from kmd_ntx_api import table_api



frontend_table_urls = [
    path('table/addresses/',
          table_views.addresses_table_view,
          name='addresses_table_view'),

    path('table/balances/',
          table_views.balances_table_view,
          name='balances_table_view'),

    path('table/coin_last_ntx/',
          table_views.coin_last_ntx_table_view,
          name='coin_last_ntx_table_view'),

    path('table/coin_ntx_season/',
          table_views.coin_ntx_season_table_view,
          name='coin_ntx_season_table_view'),

    path('table/mined/',
          table_views.mined_table_view,
          name='mined_table_view'),

    path('table/mined_count_daily/',
          table_views.mined_count_daily_table_view,
          name='mined_count_daily_table_view'),

    path('table/mined_count_season/',
          table_views.mined_count_season_table_view,
          name='mined_count_season_table_view'),

    path('table/nn_ltc_tx/',
          table_views.nn_ltc_tx_table_view,
          name='nn_ltc_tx_table_view'),

    path('table/notarised_coin_daily/',
          table_views.notarised_coin_daily_table_view,
          name='notarised_coin_daily_table_view'),

    path('table/notarised_count_daily/',
          table_views.notarised_count_daily_table_view,
          name='notarised_count_daily_table_view'),

    path('table/notarised/',
          table_views.notarised_table_view,
          name='notarised_table_view'),

    path('table/notary_ntx_season/',
          table_views.notary_ntx_season_table_view,
          name='notary_ntx_season_table_view'),

    path('table/notary_last_ntx/',
          table_views.notary_last_ntx_table_view,
          name='notary_last_ntx_table_view'),

    path('table/server_ntx_season/',
          table_views.server_ntx_season_table_view,
          name='server_ntx_season_table_view'),

    path('table/scoring_epochs/',
          table_views.scoring_epochs_table_view,
          name='scoring_epochs_table_view'),

]

api_table_urls = [

    # API TABLES V2
    path('api/table/kmd_supply/',
          table_api.kmd_supply_table_api,
          name='kmd_supply_table_api'),

    path('api/table/addresses/',
          table_api.addresses_table_api,
          name='addresses_table_api'),

    path('api/table/balances/',
          table_api.balances_table_api,
          name='balances_table_api'),

    path('api/table/coin_last_ntx/',
          table_api.coin_last_ntx_table_api,
          name='coin_last_ntx_table_api'),

    path('api/table/coin_ntx_season/',
          table_api.coin_ntx_season_table_api,
          name='coin_ntx_season_table_api'),

    path('api/table/mined/',
          table_api.mined_table_api,
          name='mined_table_api'),

    path('api/table/mined_count_daily/',
          table_api.mined_count_daily_table_api,
          name='mined_count_daily_table_api'),

    path('api/table/mined_count_season/',
          table_api.mined_count_season_table_api,
          name='mined_count_season_table_api'),

    path('api/table/nn_ltc_tx/',
          table_api.nn_ltc_tx_table_api,
          name='nn_ltc_tx_table_api'),

    path('api/table/notarised/',
          table_api.notarised_table_api,
          name='notarised_table_api'),

    path('api/table/notarised_coin_daily/',
          table_api.notarised_coin_daily_table_api,
          name='notarised_coin_daily_table_api'),

    path('api/table/notarised_count_daily/',
          table_api.notarised_count_daily_table_api,
          name='notarised_count_daily_table_api'),

    path('api/table/notary_ntx_season/',
          table_api.notary_ntx_season_table_api,
          name='notary_ntx_season_table_api'),

    path('api/table/notary_last_ntx/',
          table_api.notary_last_ntx_table_api,
          name='notary_last_ntx_table_api'),

    path('api/table/server_ntx_season/',
          table_api.server_ntx_season_table_api,
          name='server_ntx_season_table_api'),

    path('api/table/scoring_epochs/',
          table_api.scoring_epochs_table_api,
          name='scoring_epochs_table_api'),
    
    path('api/mining/notary_last_mined_table/',
          table_api.notary_last_mined_table_api,
          name='notary_last_mined_table_api'),

    path('api/table/dex_stats/',
          table_api.dex_stats_table,
          name='dex_stats_table'),

    path('api/table/dex_os_stats/',
          table_api.dex_os_stats_table,
          name='dex_os_stats_table'),

    path('api/table/dex_ui_stats/',
          table_api.dex_ui_stats_table,
          name='dex_ui_stats_table'),

    path('api/table/dex_version_stats/',
          table_api.dex_version_stats_table,
          name='dex_version_stats_table'),


    path('api/table/bestorders/',
          table_api.bestorders_table,
          name='bestorders_table'),


    path('api/table/coin_activation/',
          table_api.coin_activation_table,
          name='coin_activation_table'),

    path('api/table/mined_24hrs/',
          table_api.mined_24hrs_table,
          name='mined_24hrs_table'),

    path('api/table/notary_profile_summary/',
          table_api.notary_profile_summary_table,
          name='notary_profile_summary_table'),

    path('api/table/notary_season_ntx_summary/',
          table_api.notary_season_ntx_summary_table,
          name='notary_season_ntx_summary_table'),

    path('api/table/notary_epoch_scores/',
          table_api.notary_epoch_scores_table,
          name='notary_epoch_scores_table'),

    path('api/table/notarised_tenure/',
          table_api.notarised_tenure_table,
          name='notarised_tenure_table'),
    
]