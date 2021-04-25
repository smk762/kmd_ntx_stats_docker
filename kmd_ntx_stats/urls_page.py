from django.urls import path
from kmd_ntx_api import views_page
from kmd_ntx_api import views_notary

frontend_page_urls = [

    path('',
          views_page.dash_view,
          name='root'),
    path('index',
          views_page.dash_view,
          name='index'),

    path('chains_last_ntx/',
          views_page.chains_last_ntx,
          name='chains_last_ntx'),

    # TODO: Awaiting delegation to crons / db table
    path('chain_sync/',
          views_page.chain_sync,
          name='chain_sync'),

    path('coin_profile/',
          views_page.coin_profile_view,
          name='coin_profile'),        

    path('coin_profile/<str:chain>/',
          views_page.coin_profile_view,
          name='coin_profile_view'),

    path('dash/',
          views_page.dash_view,
          name='dash_index'),

    path('dash/<str:dash_name>/',
          views_page.dash_view,
          name='dash_view'),

    path('faucet/',
          views_page.faucet,
          name='faucet'),

    path('mining_24hrs/',
          views_page.mining_24hrs,
          name='mining_24hrs'),

    path('mining_overview/',
          views_page.mining_overview,
          name='mining_overview'),

    path('notarised_24hrs/',
          views_page.notarised_24hrs,
          name='notarised_24hrs'),

    path('ntx_scoreboard/',
          views_page.ntx_scoreboard,
          name='ntx_scoreboard'),

    path('ntx_scoreboard_24hrs/',
          views_page.ntx_scoreboard_24hrs,
          name='ntx_scoreboard_24hrs'),

    path('notarised_tenure/',
          views_page.notarised_tenure_view,
          name='notarised_tenure_view'),

    path('notary_profile/',
          views_notary.notary_profile_view,
          name='notary_profile'),

    path('notary_profile/<str:notary>/',
          views_notary.notary_profile_view,
          name='notary_profile_view'),
    
    path('sitemap/',
          views_page.sitemap,
          name='sitemap'),

    path('scoring_epochs/',
          views_page.scoring_epochs_view,
          name='scoring_epochs_view'),

    path('testnet_ntx_scoreboard/',
          views_page.testnet_ntx_scoreboard,
          name='testnet_ntx_scoreboard'),

    path('notary_epoch_scores/',
          views_page.notary_epoch_scores_view,
          name='notary_epoch_scores_view'),
    

    path('vote2021/',
          views_notary.vote2021_view,
          name='vote2021_view'),

    path('candidate_vote2021_detail/',
          views_notary.vote2021_detail_view,
          name='vote2021_detail_view'),
    

    # REVIEW? DEPRECATED?
    path('review/funding/',
          views_page.funding,
          name='funding'),
    path('review/funds_sent/',
          views_page.funds_sent,
          name='funds_sent'),

]