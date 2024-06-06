from django.urls import path
from kmd_ntx_api import info_api

api_info_urls = [

    path('info/mined_between_blocks/',
         info_api.mined_between_blocks,
         name='mined_between_blocks_api'),

    path('info/mined_between_blocktimes/',
         info_api.mined_between_blocktimes,
         name='mined_between_blocktimes_api'),

    path('api/info/balances/',
          info_api.balances_info,
          name='balances_info'),

    path('api/info/base_58/',
          info_api.base_58_coin_params,
          name='base_58_coin_params'),

    path('api/info/coins/',
          info_api.coins_info,
          name='coins_info'),

    path('api/info/coin_prefixes/',
          info_api.coin_prefixes,
          name='coin_prefixes'),

    path('api/info/coin_icons/',
          info_api.coin_icons_info,
          name='coin_icons_info'),

    path('api/info/coin_social/',
          info_api.coin_social_info,
          name='coin_social_info'),

    path('api/info/daemon_cli/',
          info_api.coin_daemon_cli,
          name='coin_daemon_cli'),

    path('api/info/dpow_server_coins/',
          info_api.dpow_server_coins_info,
          name='dpow_server_coins_info'),

    path('api/info/electrums/',
          info_api.coin_electrums,
          name='coin_electrums'),

    path('api/info/electrums_ssl/',
          info_api.coin_electrums_ssl,
          name='coin_electrums_ssl'),
    
    path('api/info/electrums_wss/',
          info_api.coin_electrums_wss,
          name='coin_electrums_wss'),

    path('api/info/explorers/',
          info_api.coin_explorers,
          name='coin_explorers'),

    path('api/info/coin_icons/',
          info_api.coin_icons_info,
          name='coin_icons_info'),

    path('api/info/launch_params/',
          info_api.coin_launch_params,
          name='coin_launch_params'),

    path('api/info/nn_social/',
          info_api.nn_social_info,
          name='nn_social_info'),

    path('api/info/notarisation_txid_list/',
          info_api.notarisation_txid_list,
          name='notarisation_txid_list'),

    path('api/info/notarised_txid/',
          info_api.notarised_txid,
          name='notarised_txid'),

    path('api/info/notarised_coins/',
          info_api.notarised_coins,
          name='notarised_coins_info'),

    path('api/info/notarised_servers/',
          info_api.notarised_servers,
          name='notarised_servers_info'),

    path('api/info/notarised_coin_daily/',
          info_api.notarised_coin_daily_info,
          name='notarised_coin_daily_info'),

    path('api/info/notarised_count_daily/',
          info_api.notarised_count_daily_info,
          name='notarised_count_daily_info'),

    path('api/info/notary_icons/',
          info_api.notary_icons_info,
          name='notary_icons_info'),

    path('api/info/notary_nodes/',
          info_api.notary_nodes_info,
          name='notary_nodes_info'),
    
    path('api/info/notary_season/',
          info_api.notary_season,
          name='notary_season_info'),
    
    path('api/info/notary_seasons/',
          info_api.notary_seasons,
          name='notary_seasons_info'),

    path('api/info/ltc_txid_list/',
          info_api.ltc_txid_list,
          name='ltc_txid_list'),

    path('api/info/notary_ltc_txid/',
          info_api.notary_ltc_txid,
          name='notary_ltc_txid'),

    path('api/info/notary_ltc_transactions/',
          info_api.notary_ltc_transactions,
          name='notary_ltc_transactions'),

]