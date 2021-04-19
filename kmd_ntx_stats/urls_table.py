from django.urls import path
from kmd_ntx_api import api_table

api_table_urls = [

    # API TABLES V2
    path('api/table/addresses/',
          api_table.addresses_table,
          name='addresses_table'),

    path('api/table/balances/',
          api_table.balances_table,
          name='balances_table'),

    path('api/table/last_mined/',
          api_table.last_mined_table,
          name='last_mined_table'),

    path('api/table/last_notarised/',
          api_table.last_notarised_table,
          name='last_notarised_table'),

    path('api/table/mined_24hrs/',
          api_table.mined_24hrs_table,
          name='mined_24hrs_table'),

    path('api/table/mined_count_season/',
          api_table.mined_count_season_table,
          name='mined_count_season_table'),

    path('api/table/notarised/',
          api_table.notarised_table,
          name='notarised_table'),

    path('api/table/notarised_24hrs/',
          api_table.notarised_24hrs_table,
          name='notarised_24hrs_table'),

    path('api/table/notarised_chain_season/',
          api_table.notarised_chain_season_table,
          name='notarised_chain_season_table'),

    path('api/table/notarised_count_season/',
          api_table.notarised_count_season_table,
          name='notarised_count_season_table'),

    path('api/table/notary_profile_summary/',
          api_table.notary_profile_summary_table,
          name='notary_profile_summary_table'),

    path('api/table/notary_epoch_scores/',
          api_table.notary_epoch_scores_table,
          name='notary_epoch_scores_table'),

    path('api/table/notarised_tenure/',
          api_table.notarised_tenure_table,
          name='notarised_tenure_table'),

    path('api/table/scoring_epochs/',
          api_table.scoring_epochs_table,
          name='scoring_epochs_table'),

    path('api/table/split_stats/',
          api_table.split_stats_table,
          name='split_stats_table'),
]