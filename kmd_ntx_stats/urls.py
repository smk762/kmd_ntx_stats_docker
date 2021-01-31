from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from kmd_ntx_api import views

router = routers.DefaultRouter()

#admin
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

# info
router.register(r'info/addresses',
                views.addresses_filter,
                basename='addresses_filter')
router.register(r'info/balances',
                views.balances_filter,
                basename='balances_filter')
router.register(r'info/coins',
                views.coins_filter,
                basename='coins_filter')
router.register(r'info/notary_rewards',
                views.rewards_filter,
                basename='rewards_filter')
router.register(r'info/notary_nodes',
                views.notary_nodes,
                basename='notary_nodes')
router.register(r'info/explorers',
                views.explorers,
                basename='explorers')


# daily
router.register(r'mined_stats/daily', views.mined_count_date_filter,
                  basename='mined_count_date_filter') # doc
router.register(r'chain_stats/daily', views.notarised_chain_date_filter,
                  basename='notarised_chain_date_filter') # doc
router.register(r'notary_stats/daily', views.notarised_count_date_filter,
                  basename='notarised_count_date_filter') # doc

# season
router.register(r'mined_stats/season',
                views.mined_count_season_filter,
                basename='mined_count_season_filter')
router.register(r'chain_stats/season',
                views.notarised_chain_season_filter,
                basename='notarised_chain_season_filter')
router.register(r'notary_stats/season',
                views.notarised_count_season_filter,
                basename='notarised_count_season_filter')

# source
router.register(r'source/mined',
                views.MinedViewSet,
                basename='MinedViewSet') # doc
router.register(r'source/notarised',
                views.ntxViewSet,
                basename='ntxViewSet') # doc

# unexposed source
router.register(r'source/addresses',
                views.addressesViewSet,
                basename='addressesViewSet')
router.register(r'source/balances',
                views.balancesViewSet,
                basename='balancesViewSet')
router.register(r'source/coins',
                views.coinsViewSet,
                basename='coinsViewSet')
router.register(r'source/nn_social',
                views.nn_socialViewSet,
                basename='nn_socialViewSet/')
router.register(r'source/mined_count_season',
                views.MinedCountSeasonViewSet,
                basename='MinedCountSeasonViewSet')
router.register(r'source/mined_count_date',
                views.MinedCountDayViewSet,
                basename='MinedCountDayViewSet')
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
router.register(r'source/last_notarised',
                views.lastNtxViewSet,
                basename='lastNtxViewSet')
router.register(r'source/last_btc_notarised',
                views.lastBtcNtxViewSet,
                basename='lastBtcNtxViewSet')
router.register(r'source/notary_rewards',
                views.rewardsViewSet,
                basename='rewardsViewSet')

# tools 
router.register(r'tools/decode_opreturn',
                views.decode_op_return,
                basename='decode_opreturn')

router.register(r'graph_json/balances',
                views.balances_graph,
                basename='balances_graph')
router.register(r'graph_json/daily_ntx',
                views.daily_ntx_graph,
                basename='daily_ntx_graph')

# TODO:
# router.register(r'tools/pubkey_to_address', views.decode_op_return, basename='convert_pubkey')
# path('posts/<int:post_id>/', post_detail_view)

urlpatterns = [
    path('admin/',
          admin.site.urls),
    path('',
          views.dash_view,
          name='index'),
    path('dash/',
          views.dash_view,
          name='dash_index'),
    path('dash/<str:dash_name>/',
          views.dash_view,
          name='dash_view'),
    path('funding/',
          views.funding,
          name='funding'),
    path('funds_sent/',
          views.funds_sent,
          name='funds_sent'),
    path('notary_profile/',
          views.notary_profile_view,
          name='notary_profile'),
    path('notary_profile/<str:notary_name>/',
          views.notary_profile_view,
          name='notary_profile_view'),
    path('coin_profile/',
          views.coin_profile_view,
          name='coin_profile'),                       
    path('coin_profile/<str:chain>/',
          views.coin_profile_view,
          name='coin_profile_view'),
    path('api/',
         include(router.urls)),
    path('faucet/',
          views.faucet,
          name='faucet'),
    path('api/info/chain_sync',
          views.chain_sync_api,
          name='chain_sync_api'),

    path('chain_sync/',
          views.chain_sync,
          name='chain_sync'),
    path('ntx_tenure/',
          views.ntx_tenure,
          name='ntx_tenure'),
    path('ntx_scoreboard/',
          views.ntx_scoreboard,
          name='ntx_scoreboard'),
    path('ntx_scoreboard_24hrs/',
          views.ntx_scoreboard_24hrs,
          name='ntx_scoreboard_24hrs'),
    path('ntx_24hrs/',
          views.ntx_24hrs,
          name='ntx_24hrs'),
    path('api/ntx_24hrs/',
          views.ntx_24hrs_api,
          name='ntx_24hrs_api'),
    path('btc_ntx/',
          views.btc_ntx,
          name='btc_ntx'),
    path('btc_ntx_all/',
          views.btc_ntx_all,
          name='btc_ntx_all'),
    path('chains_last_ntx/',
          views.chains_last_ntx,
          name='chains_last_ntx'),
    path('mining_overview/',
          views.mining_overview,
          name='mining_overview'),
    path('mining_24hrs/',
          views.mining_24hrs,
          name='mining_24hrs'),
    path('api/nn_mined_4hrs_count/',
          views.nn_mined_4hrs_api,
          name='nn_mined_4hrs_api'),
    path('api/nn_mined_last_api/',
          views.nn_mined_last_api,
          name='nn_mined_last_api'),
    
    # Notary BTC txids
    path('api/info/nn_btc_txid_other',
          views.nn_btc_txid_other,
          name='nn_btc_txid_other'),
    path('api/info/split_summary_api',
          views.split_summary_api,
          name='split_summary_api'),
    path('api/info/nn_btc_txid_splits',
          views.nn_btc_txid_splits,
          name='nn_btc_txid_splits'),
    path('api/info/nn_btc_txid_raw',
          views.nn_btc_txid_raw,
          name='nn_btc_txid_raw'),
    path('api/info/nn_btc_txid_spam',
          views.nn_btc_txid_spam,
          name='nn_btc_txid_spam'),
    path('api/info/nn_btc_txid',
          views.nn_btc_txid,
          name='nn_btc_txid'),
    path('api/info/notary_btc_txids',
          views.notary_btc_txids,
          name='notary_btc_txids'),
    path('api/info/nn_btc_txid_list',
          views.nn_btc_txid_list,
          name='nn_btc_txid_list'),

    path('api-auth/',
         include('rest_framework.urls',
            namespace='rest_framework')),
]