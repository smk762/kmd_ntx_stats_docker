from django.urls import path
from kmd_ntx_api import api_info

api_info_urls = [

    # API INFO V2
    path('api/index/',
          api_info.api_index,
          name='api_index'),

    path('api/pages_index/',
          api_info.pages_index,
          name='api_index'),

    path('api/info/balances/',
          api_info.balances_info,
          name='balances_info'),

    path('api/info/base_58/',
          api_info.base_58_coin_params,
          name='base_58_coin_params'),

    path('api/info/coins/',
          api_info.coins_info,
          name='coins_info'),

    path('api/info/coin_icons/',
          api_info.coin_icons_info,
          name='coin_icons_info'),

    path('api/info/coin_social/',
          api_info.coin_social_info,
          name='coin_social_info'),

    path('api/info/daemon_cli/',
          api_info.coin_daemon_cli,
          name='coin_daemon_cli'),

    path('api/info/dpow_server_coins/',
          api_info.dpow_server_coins_info,
          name='dpow_server_coins_info'),

    path('api/info/electrums/',
          api_info.coin_electrums,
          name='coin_electrums'),

    path('api/info/electrums_ssl/',
          api_info.coin_electrums_ssl,
          name='coin_electrums_ssl'),

    path('api/info/explorers/',
          api_info.coin_explorers,
          name='coin_explorers'),

    path('api/info/coin_icons/',
          api_info.coin_icons_info,
          name='coin_icons_info'),

    path('api/info/launch_params/',
          api_info.coin_launch_params,
          name='coin_launch_params'),

    path('api/info/nn_social/',
          api_info.nn_social_info,
          name='nn_social_info'),

    path('api/info/notarisation_txid_list/',
          api_info.notarisation_txid_list,
          name='notarisation_txid_list'),

    path('api/info/notarised_coins/',
          api_info.notarised_coins,
          name='notarised_coins_info'),

    path('api/info/notarised_servers/',
          api_info.notarised_servers,
          name='notarised_servers_info'),

    path('api/info/notarised_coin_daily/',
          api_info.notarised_coin_daily_info,
          name='notarised_coin_daily_info'),

    path('api/info/notarised_count_daily/',
          api_info.notarised_count_daily_info,
          name='notarised_count_daily_info'),

    path('api/info/notarised_txid/',
          api_info.notarised_txid,
          name='notarised_txid'),

    path('api/info/notary_icons/',
          api_info.notary_icons_info,
          name='notary_icons_info'),

    path('api/info/notary_nodes/',
          api_info.notary_nodes_info,
          name='notary_nodes_info'),

    path('api/info/btc_txid_list/',
          api_info.btc_txid_list,
          name='btc_txid_list'),

    path('api/info/notary_btc_txid/',
          api_info.notary_btc_txid,
          name='notary_btc_txid'),

    path('api/info/notary_btc_transactions/',
          api_info.notary_btc_transactions,
          name='notary_btc_transactions'),

    path('api/info/ltc_txid_list/',
          api_info.ltc_txid_list,
          name='ltc_txid_list'),

    path('api/info/notary_ltc_txid/',
          api_info.notary_ltc_txid,
          name='notary_ltc_txid'),

    path('api/info/notary_ltc_transactions/',
          api_info.notary_ltc_transactions,
          name='notary_ltc_transactions'),

    path('api/info/rewards_by_address/',
          api_info.rewards_by_address,
          name='rewards_by_address'),

]