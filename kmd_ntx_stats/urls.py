from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from kmd_ntx_api import api_tables
from kmd_ntx_api import api_views
from kmd_ntx_api import api_viewsets
from kmd_ntx_api import api_filtered_viewsets
from kmd_ntx_api import api_tools
from kmd_ntx_api import api_graph
from kmd_ntx_api import page_views
from kmd_ntx_api import notary_views

router = routers.DefaultRouter()

#admin
router.register(r'users', api_viewsets.UserViewSet)
router.register(r'groups', api_viewsets.GroupViewSet)

# info
router.register(r'info/addresses',
                api_filtered_viewsets.addresses_filter,
                basename='addresses_filter') # 
router.register(r'info/balances',
                api_filtered_viewsets.balances_filter,
                basename='balances_filter')
router.register(r'info/coins',
                api_filtered_viewsets.coins_filter,
                basename='coins_filter')
router.register(r'info/explorers',
                api_filtered_viewsets.explorers_filter,
                basename='explorers_filter')

router.register(r'info/mined_count_season',
                api_filtered_viewsets.mined_count_season_filter,
                basename='mined_count_season_filter')

router.register(r'info/mined_count_date',
                api_filtered_viewsets.mined_count_date_filter,
                basename='mined_count_date_filter')

router.register(r'info/notarised_chain_season',
                api_filtered_viewsets.notarised_chain_season_filter,
                basename='notarised_chain_season_filter')


router.register(r'info/notarisation',
                api_filtered_viewsets.notarised_filter,
                basename='notarised_filter')

router.register(r'info/notarised_count_season',
                api_filtered_viewsets.notarised_count_season_filter,
                basename='notarised_count_season_filter')

router.register(r'info/notarised_chain_date',
                api_filtered_viewsets.notarised_chain_date_filter,
                basename='notarised_chain_date_filter')

router.register(r'info/notarised_count_date',
                api_filtered_viewsets.notarised_count_date_filter,
                basename='notarised_count_date_filter')

router.register(r'info/notarised_tenure',
                api_filtered_viewsets.notarised_tenure_filter,
                basename='notarised_tenure_filter')

router.register(r'info/notary_nodes',
                api_filtered_viewsets.notary_nodes_filter,
                basename='notary_nodes_filter')

router.register(r'info/notary_rewards',
                api_filtered_viewsets.notary_rewards_filter,
                basename='notary_rewards_filter')


router.register(r'info/nn_social',
                api_filtered_viewsets.notary_social_filter,
                basename='notary_social_filter')

router.register(r'info/last_notarised',
                api_filtered_viewsets.last_ntx_filter,
                basename='last_ntx_filter')

router.register(r'info/last_btc_notarised',
                api_filtered_viewsets.last_btc_ntx_filter,
                basename='last_btc_ntx_filter')


# Tools 
router.register(r'tools/decode_opreturn',
                api_tools.api_decode_op_return_tool,
                basename='api_decode_op_return_tool')
router.register(r'tools/address_from_pubkey',
                api_tools.api_address_from_pubkey_tool,
                basename='api_address_from_pubkey_tool')
router.register(r'tools/addr_from_base58',
                api_tools.api_addr_from_base58_tool,
                basename='api_addr_from_base58_tool')

# Graphs
router.register(r'graph_json/balances',
                api_graph.balances_graph,
                basename='balances_graph')
router.register(r'graph_json/daily_ntx',
                api_graph.daily_ntx_graph,
                basename='daily_ntx_graph')


# API VIEWSETS
router.register(r'source/addresses',
                api_viewsets.addressesViewSet,
                basename='addressesViewSet')

router.register(r'source/balances',
                api_viewsets.balancesViewSet,
                basename='balancesViewSet')

router.register(r'source/coins',
                api_viewsets.coinsViewSet,
                basename='coinsViewSet')

router.register(r'source/last_btc_notarised',
                api_viewsets.lastBtcNtxViewSet,
                basename='lastBtcNtxViewSet')

router.register(r'source/last_notarised',
                api_viewsets.lastNtxViewSet,
                basename='lastNtxViewSet')

router.register(r'source/mined',
                api_viewsets.MinedViewSet,
                basename='MinedViewSet') 

router.register(r'source/mined_count_date',
                api_viewsets.MinedCountDayViewSet,
                basename='MinedCountDayViewSet')

router.register(r'source/mined_count_date',
                api_viewsets.MinedCountDayViewSet,
                basename='MinedCountDayViewSet')

router.register(r'source/mined_count_season',
                api_viewsets.MinedCountSeasonViewSet,
                basename='MinedCountSeasonViewSet')


router.register(r'source/nn_social',
                api_viewsets.nn_socialViewSet,
                basename='nn_socialViewSet')

router.register(r'source/notarised',
                api_viewsets.ntxViewSet,
                basename='ntxViewSet') # doc

router.register(r'source/notarised_count_date',
                api_viewsets.ntxCountDateViewSet,
                basename='ntxCountDateViewSet')

router.register(r'source/notarised_count_season',
                api_viewsets.ntxCountSeasonViewSet,
                basename='ntxCountSeasonViewSet')

router.register(r'source/notarised_chain_date',
                api_viewsets.ntxChainDateViewSet,
                basename='ntxChainDateViewSet')

router.register(r'source/notarised_chain_season',
                api_viewsets.ntxChainSeasonViewSet,
                basename='ntxChainSeasonViewSet')

router.register(r'source/notarised_tenure',
                api_viewsets.ntxTenureViewSet,
                basename='ntxTenureViewSet')

router.register(r'source/notary_rewards',
                api_viewsets.rewardsViewSet,
                basename='rewardsViewSet')

urlpatterns = [
    path('api/',
         include(router.urls)),
    path('admin/',
          admin.site.urls),
    path('api-auth/',
         include('rest_framework.urls',
            namespace='rest_framework')),

    path('',
          page_views.dash_view,
          name='root'),
    path('index',
          page_views.dash_view,
          name='index'),

    path('btc_ntx/',
          page_views.btc_ntx,
          name='btc_ntx'),
    path('btc_ntx_all/',
          page_views.btc_ntx_all,
          name='btc_ntx_all'),

    path('chains_last_ntx/',
          page_views.chains_last_ntx,
          name='chains_last_ntx'),

    path('chain_sync/',
          page_views.chain_sync,
          name='chain_sync'),

    path('coin_profile/',
          page_views.coin_profile_view,
          name='coin_profile'),                       
    path('coin_profile/<str:chain>/',
          page_views.coin_profile_view,
          name='coin_profile_view'),

    path('dash/',
          page_views.dash_view,
          name='dash_index'),
    path('dash/<str:dash_name>/',
          page_views.dash_view,
          name='dash_view'),

    path('faucet/',
          page_views.faucet,
          name='faucet'),


    path('mining_24hrs/',
          page_views.mining_24hrs,
          name='mining_24hrs'),
    path('mining_overview/',
          page_views.mining_overview,
          name='mining_overview'),

    path('notary_profile/',
          notary_views.notary_profile_view,
          name='notary_profile'),
    path('notary_profile/<str:notary>/',
          notary_views.notary_profile_view,
          name='notary_profile_view'),

    path('ntx_24hrs/',
          page_views.ntx_24hrs,
          name='ntx_24hrs'),

    path('ntx_scoreboard/',
          page_views.ntx_scoreboard,
          name='ntx_scoreboard'),

    path('ntx_scoreboard_24hrs/',
          page_views.ntx_scoreboard_24hrs,
          name='ntx_scoreboard_24hrs'),

    path('notarised_tenure/',
          page_views.notarised_tenure_view,
          name='notarised_tenure_view'),

    path('sitemap/',
          page_views.sitemap,
          name='sitemap'),

    path('scoring_epochs',
          page_views.scoring_epochs_view,
          name='scoring_epochs_view'),

    path('testnet_ntx_scoreboard',
          page_views.testnet_ntx_scoreboard,
          name='testnet_ntx_scoreboard'),

    path('notary_epoch_scoring_table/',
          page_views.notary_epoch_scoring_table,
          name='notary_epoch_scoring_table'),
    

    # OTHER API
    


    # API views (simple)
    path('api/info/address_btc_txids',
          api_views.address_btc_txids,
          name='address_btc_txids'),

    path('api/info/sidebar_links',
          api_views.api_sidebar_links,
          name='api_sidebar_links'),

    path('api/info/server_chains',
          api_views.api_server_chains,
          name='api_server_chains'),

    path('api/info/dpow_server_coins',
          api_views.api_dpow_server_coins_dict,
          name='api_dpow_server_coins_dict'),

    path('api/info/btc_ntx_lag',
          api_views.api_btc_ntx_lag,
          name='api_btc_ntx_lag'),

    path('api/testnet/totals',
          api_views.api_testnet_totals,
          name='api_testnet_totals'),

    path('api/info/chain_sync',
          api_views.chain_sync_api,
          name='chain_sync_api'),

    path('api/info/mining_24hrs',
          api_views.mining_24hrs_api,
          name='mining_24hrs_api'),

    path('api/info/notarisation_txid',
          api_views.notarisation_txid,
          name='notarisation_txid'),


    path('api/info/chain_notarisation_txid_list',
          api_views.chain_notarisation_txid_list,
          name='chain_notarisation_txid_list'),

    path('api/info/notary_btc_txids',
          api_views.notary_btc_txids,
          name='notary_btc_txids'),

    path('api/info/notary_ltc_txids',
          api_views.notary_ltc_txids,
          name='notary_ltc_txids'),

    path('api/info/nn_btc_txid',
          api_views.nn_btc_txid,
          name='nn_btc_txid'),

    path('api/info/nn_btc_txid_list',
          api_views.nn_btc_txid_list,
          name='nn_btc_txid_list'),

    path('api/info/nn_ltc_txid_list',
          api_views.nn_ltc_txid_list,
          name='nn_ltc_txid_list'),

    path('api/info/nn_btc_txid_ntx',
          api_views.nn_btc_txid_ntx,
          name='nn_btc_txid_ntx'),

    path('api/info/nn_btc_txid_splits',
          api_views.nn_btc_txid_splits,
          name='nn_btc_txid_splits'),

    path('api/info/nn_ltc_txid',
          api_views.nn_ltc_txid,
          name='nn_ltc_txid'),

    path('api/nn_mined_4hrs_count/',
          api_views.nn_mined_4hrs_api,
          name='nn_mined_4hrs_api'),
    
    path('api/nn_mined_last_api/',
          api_views.nn_mined_last_api,
          name='nn_mined_last_api'),

    path('api/ntx_24hrs/',
          api_views.ntx_24hrs_api,
          name='ntx_24hrs_api'),

    path('api/info/split_summary_api',
          api_views.split_summary_api,
          name='split_summary_api'),

    path('api/info/split_summary_api',
          api_views.split_summary_api,
          name='split_summary_api'),
    
    path('api/info/split_summary_table',
          api_views.split_summary_table,
          name='split_summary_table'),
    
    path('api/info/notarised_season_score',
          api_views.notarised_season_score,
          name='notarised_season_score'),
    

    path('api/table/epoch_scoring',
          api_tables.epoch_scoring_table,
          name='epoch_scoring_table'),

    path('api/table/notary_epoch_scoring',
          api_tables.api_table_notary_epoch_scoring,
          name='api_table_notary_epoch_scoring'),

    path('api/table/mined_count_season',
          api_tables.mined_count_season_table,
          name='mined_count_season_table'),

    # PENDING

    # REVIEW? DEPRECATED?
    path('review/funding/',
          page_views.funding,
          name='funding'),
    path('review/funds_sent/',
          page_views.funds_sent,
          name='funds_sent'),

]