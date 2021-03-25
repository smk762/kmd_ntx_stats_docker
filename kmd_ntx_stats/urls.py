from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from kmd_ntx_api import views
from kmd_ntx_api import api_viewsets
from kmd_ntx_api import api_tools
from kmd_ntx_api import api_graph
from kmd_ntx_api import page_views

router = routers.DefaultRouter()

#admin
router.register(r'users', api_viewsets.UserViewSet)
router.register(r'groups', api_viewsets.GroupViewSet)

# info
router.register(r'info/addresses',
                api_viewsets.addresses_filter,
                basename='addresses_filter') # 
router.register(r'info/balances',
                api_viewsets.balances_filter,
                basename='balances_filter')
router.register(r'info/coins',
                api_viewsets.coins_filter,
                basename='coins_filter')
router.register(r'info/explorers',
                api_viewsets.explorers_filter,
                basename='explorers_filter')
router.register(r'info/mined_count_season',
                api_viewsets.mined_count_season_filter,
                basename='mined_count_season_filter')
router.register(r'info/mined_count_date',
                api_viewsets.mined_count_date_filter,
                basename='mined_count_date_filter')
router.register(r'info/mined',
                api_viewsets.mined_filter,
                basename='mined_filter')
router.register(r'info/notarised',
                api_viewsets.notarised_filter,
                basename='notarised_filter')

router.register(r'info/notarised_chain_season',
                api_viewsets.notarised_chain_season_filter,
                basename='notarised_chain_season_filter')
router.register(r'info/notarised_count_season',
                api_viewsets.notarised_count_season_filter,
                basename='notarised_count_season_filter')
router.register(r'info/notarised_chain_date',
                api_viewsets.notarised_chain_date_filter,
                basename='notarised_chain_date_filter')
router.register(r'info/notarised_count_date',
                api_viewsets.notarised_count_date_filter,
                basename='notarised_count_date_filter')
router.register(r'info/notarised_tenure',
                api_viewsets.notarised_tenure_filter,
                basename='notarised_tenure_filter')
router.register(r'info/notary_nodes',
                api_viewsets.notary_nodes_filter,
                basename='notary_nodes_filter')
router.register(r'info/notary_rewards',
                api_viewsets.notary_rewards_filter,
                basename='notary_rewards_filter')


router.register(r'info/nn_social',
                api_viewsets.notary_social_filter,
                basename='notary_social_filter')

router.register(r'source/last_notarised',
                api_viewsets.lastNtxViewSet,
                basename='lastNtxViewSet')
router.register(r'info/last_notarised',
                api_viewsets.last_ntx_filter,
                basename='last_ntx_filter')

router.register(r'source/last_btc_notarised',
                api_viewsets.lastBtcNtxViewSet,
                basename='lastBtcNtxViewSet')
router.register(r'info/last_btc_notarised',
                api_viewsets.last_btc_ntx_filter,
                basename='last_btc_ntx_filter')

# CSV output
router.register(r'csv/notarised_tenure',
                api_viewsets.notarised_tenure_csv,
                basename='notarised_tenure_csv')

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


# source
router.register(r'source/addresses',
                views.addressesViewSet,
                basename='addressesViewSet')
router.register(r'source/balances',
                views.balancesViewSet,
                basename='balancesViewSet')
router.register(r'source/coins',
                views.coinsViewSet,
                basename='coinsViewSet')
router.register(r'source/mined',
                views.MinedViewSet,
                basename='MinedViewSet') # doc
router.register(r'source/mined_count_season',
                views.MinedCountSeasonViewSet,
                basename='MinedCountSeasonViewSet')
router.register(r'source/mined_count_date',
                views.MinedCountDayViewSet,
                basename='MinedCountDayViewSet')
router.register(r'source/nn_social',
                api_viewsets.nn_socialViewSet,
                basename='nn_socialViewSet')
router.register(r'source/notarised',
                views.ntxViewSet,
                basename='ntxViewSet') # doc
router.register(r'source/notarised_chain_season',
                views.ntxChainSeasonViewSet,
                basename='ntxChainSeasonViewSet')
router.register(r'source/notarised_count_season',
                views.ntxCountSeasonViewSet,
                basename='ntxCountSeasonViewSet')
router.register(r'source/notarised_chain_date',
                views.ntxChainDateViewSet,
                basename='ntxChainDateViewSet')
router.register(r'source/notarised_count_date',
                views.ntxCountDateViewSet,
                basename='ntxCountDateViewSet')
router.register(r'source/notarised_tenure',
                views.ntxTenureViewSet,
                basename='ntxTenureViewSet')
router.register(r'source/notary_rewards',
                views.rewardsViewSet,
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
    path('funding/',
          page_views.funding,
          name='funding'),
    path('funds_sent/',
          page_views.funds_sent,
          name='funds_sent'),

    path('mining_24hrs/',
          page_views.mining_24hrs,
          name='mining_24hrs'),
    path('mining_overview/',
          page_views.mining_overview,
          name='mining_overview'),

    path('notary_profile/',
          page_views.notary_profile_view,
          name='notary_profile'),
    path('notary_profile/<str:notary_name>/',
          page_views.notary_profile_view,
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
    path('ntx_tenure/',
          page_views.ntx_tenure,
          name='ntx_tenure'),

    path('sitemap/',
          page_views.sitemap,
          name='sitemap'),
    path('testnet_ntx_scoreboard',
          page_views.testnet_ntx_scoreboard,
          name='testnet_ntx_scoreboard'),

    # OTHER API

    path('api/ntx_24hrs/',
          views.ntx_24hrs_api,
          name='ntx_24hrs_api'),
    path('api/nn_mined_4hrs_count/',
          views.nn_mined_4hrs_api,
          name='nn_mined_4hrs_api'),
    path('api/nn_mined_last_api/',
          views.nn_mined_last_api,
          name='nn_mined_last_api'),
    
    path('api/info/notarisation_txid',
          views.notarisation_txid,
          name='notarisation_txid'),
    
    # Notary BTC txids
    path('api/info/address_btc_txids',
          views.address_btc_txids,
          name='address_btc_txids'),
    path('api/info/notary_btc_txids',
          views.notary_btc_txids,
          name='notary_btc_txids'),

    path('api/info/nn_btc_txid',
          views.nn_btc_txid,
          name='nn_btc_txid'),
    path('api/info/nn_btc_txid_other',
          views.nn_btc_txid_other,
          name='nn_btc_txid_other'),
    path('api/info/nn_btc_txid_raw',
          views.nn_btc_txid_raw,
          name='nn_btc_txid_raw'),
    path('api/info/nn_btc_txid_spam',
          views.nn_btc_txid_spam,
          name='nn_btc_txid_spam'),
    path('api/info/nn_btc_txid_splits',
          views.nn_btc_txid_splits,
          name='nn_btc_txid_splits'),
    path('api/info/split_summary_api',
          views.split_summary_api,
          name='split_summary_api'),

    # LTC
    path('api/info/nn_ltc_txid',
          views.nn_ltc_txid,
          name='nn_ltc_txid'),

    path('api/info/notary_ltc_txids',
          views.notary_ltc_txids,
          name='notary_ltc_txids'),

    # TESTNET API
    path('api/testnet/totals',
          views.api_testnet_totals,
          name='api_testnet_totals'),
    path('api/testnet/raw',
          views.api_testnet_raw,
          name='api_testnet_raw'),
    path('api/testnet/raw_24hr',
          views.api_testnet_raw_24hr,
          name='api_testnet_raw_24hr'),

    # OTHER API
    path('api/info/chain_sync',
          views.chain_sync_api,
          name='chain_sync_api'),

    path('api/info/btc_ntx_lag',
          views.api_btc_ntx_lag,
          name='api_btc_ntx_lag'),


]