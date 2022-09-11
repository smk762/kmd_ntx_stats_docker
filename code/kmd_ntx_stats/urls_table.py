from django.urls import path
from kmd_ntx_api import views_table
from kmd_ntx_api import api_table



frontend_table_urls = [
    path('table/addresses/',
          views_table.addresses_table_view,
          name='addresses_table_view'),

    path('table/balances/',
          views_table.balances_table_view,
          name='balances_table_view'),

    path('table/coin_last_ntx/',
          views_table.coin_last_ntx_table_view,
          name='coin_last_ntx_table_view'),

    path('table/coin_ntx_season/',
          views_table.coin_ntx_season_table_view,
          name='coin_ntx_season_table_view'),

    path('table/mined/',
          views_table.mined_table_view,
          name='mined_table_view'),

    path('table/mined_count_daily/',
          views_table.mined_count_daily_table_view,
          name='mined_count_daily_table_view'),

    path('table/mined_count_season/',
          views_table.mined_count_season_table_view,
          name='mined_count_season_table_view'),

    path('table/nn_ltc_tx/',
          views_table.nn_ltc_tx_table_view,
          name='nn_ltc_tx_table_view'),

    path('table/notarised_coin_daily/',
          views_table.notarised_coin_daily_table_view,
          name='notarised_coin_daily_table_view'),

    path('table/notarised_count_daily/',
          views_table.notarised_count_daily_table_view,
          name='notarised_count_daily_table_view'),

    path('table/notarised/',
          views_table.notarised_table_view,
          name='notarised_table_view'),

    path('table/notary_ntx_season/',
          views_table.notary_ntx_season_table_view,
          name='notary_ntx_season_table_view'),

    path('table/notary_last_ntx/',
          views_table.notary_last_ntx_table_view,
          name='notary_last_ntx_table_view'),

    path('table/rewards_tx/',
          views_table.rewards_tx_table_view,
          name='rewards_tx_table_view'),

    path('table/server_ntx_season/',
          views_table.server_ntx_season_table_view,
          name='server_ntx_season_table_view'),

    path('table/scoring_epochs/',
          views_table.scoring_epochs_table_view,
          name='scoring_epochs_table_view'),

]

api_table_urls = [

    # API TABLES V2
    path('api/table/addresses/',
          api_table.addresses_table_api,
          name='addresses_table_api'),

    path('api/table/balances/',
          api_table.balances_table_api,
          name='balances_table_api'),

    path('api/table/coin_last_ntx/',
          api_table.coin_last_ntx_table_api,
          name='coin_last_ntx_table_api'),

    path('api/table/coin_ntx_season/',
          api_table.coin_ntx_season_table_api,
          name='coin_ntx_season_table_api'),

    path('api/table/mined/',
          api_table.mined_table_api,
          name='mined_table_api'),

    path('api/table/mined_count_daily/',
          api_table.mined_count_daily_table_api,
          name='mined_count_daily_table_api'),

    path('api/table/mined_count_season/',
          api_table.mined_count_season_table_api,
          name='mined_count_season_table_api'),

    path('api/table/nn_ltc_tx/',
          api_table.nn_ltc_tx_table_api,
          name='nn_ltc_tx_table_api'),

    path('api/table/notarised/',
          api_table.notarised_table_api,
          name='notarised_table_api'),

    path('api/table/notarised_coin_daily/',
          api_table.notarised_coin_daily_table_api,
          name='notarised_coin_daily_table_api'),

    path('api/table/notarised_count_daily/',
          api_table.notarised_count_daily_table_api,
          name='notarised_count_daily_table_api'),

    path('api/table/notary_ntx_season/',
          api_table.notary_ntx_season_table_api,
          name='notary_ntx_season_table_api'),

    path('api/table/notary_last_ntx/',
          api_table.notary_last_ntx_table_api,
          name='notary_last_ntx_table_api'),

    path('api/table/rewards_tx/',
          api_table.rewards_tx_table_api,
          name='rewards_tx_table_api'),

    path('api/table/server_ntx_season/',
          api_table.server_ntx_season_table_api,
          name='server_ntx_season_table_api'),

    path('api/table/scoring_epochs/',
          api_table.scoring_epochs_table_api,
          name='scoring_epochs_table_api'),
    
    path('api/mining/notary_last_mined_table/',
          api_table.notary_last_mined_table_api,
          name='notary_last_mined_table_api'),

    path('api/table/dex_stats/',
          api_table.dex_stats_table,
          name='dex_stats_table'),

    path('api/table/dex_os_stats/',
          api_table.dex_os_stats_table,
          name='dex_os_stats_table'),

    path('api/table/dex_ui_stats/',
          api_table.dex_ui_stats_table,
          name='dex_ui_stats_table'),

    path('api/table/dex_version_stats/',
          api_table.dex_version_stats_table,
          name='dex_version_stats_table'),


    path('api/table/bestorders/',
          api_table.bestorders_table,
          name='bestorders_table'),


    path('api/table/coin_activation/',
          api_table.coin_activation_table,
          name='coin_activation_table'),

    path('api/table/mined_24hrs/',
          api_table.mined_24hrs_table,
          name='mined_24hrs_table'),

    path('api/table/notary_profile_summary/',
          api_table.notary_profile_summary_table,
          name='notary_profile_summary_table'),

    path('api/table/notary_season_ntx_summary/',
          api_table.notary_season_ntx_summary_table,
          name='notary_season_ntx_summary_table'),

    path('api/table/notary_epoch_scores/',
          api_table.notary_epoch_scores_table,
          name='notary_epoch_scores_table'),

    path('api/table/notarised_tenure/',
          api_table.notarised_tenure_table,
          name='notarised_tenure_table'),
    
    path('api/table/split_stats/',
          api_table.split_stats_table,
          name='split_stats_table'),
]