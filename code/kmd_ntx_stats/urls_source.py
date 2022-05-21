from rest_framework import routers
from kmd_ntx_api import api_viewsets

source_router = routers.DefaultRouter()

#admin
source_router.register(r'users', api_viewsets.UserViewSet,
                basename='UserViewSet')

source_router.register(r'groups', api_viewsets.GroupViewSet,
                basename='GroupViewSet')

# API MODEL VIEWSETS (Paginated Source)
source_router.register(r'addresses',
                api_viewsets.addressesViewSet,
                basename='addressesViewSet')

source_router.register(r'balances',
                api_viewsets.balancesViewSet,
                basename='balancesViewSet')

# TODO: Awaiting delegation to crons / db table
#source_router.register(r'coin_sync',
#                api_viewsets.coinSyncViewSet,
#                basename='coinSyncViewSet')

source_router.register(r'coins',
                api_viewsets.coinsViewSet,
                basename='coinsViewSet')

source_router.register(r'coin_ntx_season',
                api_viewsets.coinNtxSeasonViewSet,
                basename='coinNtxSeasonViewSet')

source_router.register(r'coin_social',
                api_viewsets.coinSocialViewSet,
                basename='coinSocialViewSet')

# TODO: Not in use, will implement S5
#source_router.register(r'funding_transactions',
#                api_viewsets.fundingTXViewSet,
#                basename='fundingTXViewSet')

source_router.register(r'coin_last_ntx',
                api_viewsets.coinLastNtxViewSet,
                basename='coinLastNtxViewSet')

source_router.register(r'notary_last_ntx',
                api_viewsets.notaryLastNtxViewSet,
                basename='notaryLastNtxViewSet')

source_router.register(r'mined',
                api_viewsets.minedViewSet,
                basename='minedViewSet') 

source_router.register(r'seednode_version_stats',
                api_viewsets.mm2VersionStatsViewSet,
                basename='mm2VersionStatsViewSet')

source_router.register(r'mined_count_daily',
                api_viewsets.minedCountDailyViewSet,
                basename='minedCountDailyViewSet')

source_router.register(r'mined_count_season',
                api_viewsets.minedCountSeasonViewSet,
                basename='minedCountSeasonViewSet')

source_router.register(r'nn_btc_tx',
                api_viewsets.nnBtcTxViewSet,
                basename='nnBtcTxViewSet')

source_router.register(r'nn_ltc_tx',
                api_viewsets.nnLtcTxViewSet,
                basename='nnLtcTxViewSet')

source_router.register(r'nn_social',
                api_viewsets.nnSocialViewSet,
                basename='nnSocialViewSet')

source_router.register(r'notarised',
                api_viewsets.notarisedViewSet,
                basename='notarisedViewSet') # doc

source_router.register(r'notarised_coin_daily',
                api_viewsets.notarisedCoinDailyViewSet,
                basename='notarisedCoinDailyViewSet')

source_router.register(r'notarised_count_daily',
                api_viewsets.notarisedCountDailyViewSet,
                basename='notarisedCountDailyViewSet')

source_router.register(r'notary_ntx_season',
                api_viewsets.notaryNtxSeasonViewSet,
                basename='notaryNtxSeasonViewSet')

source_router.register(r'notarised_tenure',
                api_viewsets.notarisedTenureViewSet,
                basename='notarisedTenureViewSet')

source_router.register(r'scoring_epochs',
                api_viewsets.scoringEpochsViewSet,
                basename='scoringEpochsViewSet')

source_router.register(r'server_ntx_season',
                api_viewsets.serverNtxSeasonViewSet,
                basename='serverNtxSeasonViewSet')

source_router.register(r'rewards_tx',
                api_viewsets.rewardsTxViewSet,
                basename='rewardsTxViewSet')

source_router.register(r'notary_vote',
                api_viewsets.notaryVoteViewSet,
                basename='notaryVoteViewSet')

source_router.register(r'notary_candidates',
                api_viewsets.notaryCandidatesViewSet,
                basename='notaryCandidatesSerializer')
