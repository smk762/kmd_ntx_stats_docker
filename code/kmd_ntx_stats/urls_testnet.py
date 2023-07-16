from django.urls import path
from kmd_ntx_api import testnet_views
from kmd_ntx_api import testnet_api


# API STATUS V2
frontend_testnet_urls = [
    path('testnet_ntx_scoreboard/',
          testnet_views.testnet_ntx_scoreboard_view,
          name='testnet_ntx_scoreboard_view'),

    path('notary_vote/',
          testnet_views.notary_vote_view,
          name='notary_vote_view'),
    
    path('candidate_notary_vote_detail/',
          testnet_views.notary_vote_detail_view,
          name='notary_vote_detail_view'),
]

api_testnet_urls = [
    path('api/testnet/proposals/',
          testnet_api.api_testnet_proposals,
          name='api_testnet_proposals'),

    path('api/info/notary_vote_stats/',
          testnet_api.notary_vote_stats_info,
          name='notary_vote_stats_info'),
    
    path('api/table/notary_vote_totals/',
          testnet_api.vote_aggregates_api,
          name='vote_aggregates_api'),
    
    path('api/table/notary_vote_detail_table/',
          testnet_api.api_notary_vote_detail_table,
          name='api_notary_vote_detail_table'),
    
    path('api/table/testnet_ntx_scoreboard/',
          testnet_api.api_testnet_scoreboard,
          name='api_testnet_scoreboard'),

    path('api/info/is_election_over/',
          testnet_api.is_election_over_api,
          name='is_election_over_api'),
]