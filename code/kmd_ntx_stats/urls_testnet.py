from django.urls import path
from kmd_ntx_api import views_testnet
from kmd_ntx_api import api_testnet


# API STATUS V2
frontend_testnet_urls = [
    path('testnet_ntx_scoreboard/',
          views_testnet.testnet_ntx_scoreboard_view,
          name='testnet_ntx_scoreboard_view'),

    path('s5_address_confirmation/',
          views_testnet.s5_address_confirmation,
          name='s5_address_confirmation_view'),

    path('notary_vote/',
          views_testnet.notary_vote_view,
          name='notary_vote_view'),
    
    path('candidate_notary_vote_detail/',
          views_testnet.notary_vote_detail_view,
          name='notary_vote_detail_view'),
]

api_testnet_urls = [
    path('api/testnet/totals/',
          api_testnet.api_testnet_totals,
          name='api_testnet_totals'),

    path('api/info/notary_vote_stats/',
          api_testnet.notary_vote_stats_info,
          name='notary_vote_stats_info'),

    path('api/table/notary_vote/',
          api_testnet.notary_vote_table,
          name='notary_vote_table'),
    
    path('api/table/notary_vote_totals/',
          api_testnet.vote_aggregates_api,
          name='vote_aggregates_api'),
]