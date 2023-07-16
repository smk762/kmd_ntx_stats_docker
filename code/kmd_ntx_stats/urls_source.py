from rest_framework import routers
from kmd_ntx_api import viewsets_api

source_router = routers.DefaultRouter()

#admin
source_router.register(r'users', viewsets_api.UserViewSet,
                basename='UserViewSet')

source_router.register(r'groups', viewsets_api.GroupViewSet,
                basename='GroupViewSet')

# API MODEL VIEWSETS (Paginated Source)
source_router.register(r'addresses',
                viewsets_api.addressesViewSet,
                basename='addressesViewSet')

source_router.register(r'balances',
                viewsets_api.balancesViewSet,
                basename='balancesViewSet')

source_router.register(r'coins',
                viewsets_api.coinsViewSet,
                basename='coinsViewSet')

source_router.register(r'coin_ntx_season',
                viewsets_api.coinNtxSeasonViewSet,
                basename='coinNtxSeasonViewSet')

source_router.register(r'coin_social',
                viewsets_api.coinSocialViewSet,
                basename='coinSocialViewSet')

source_router.register(r'coin_last_ntx',
                viewsets_api.coinLastNtxViewSet,
                basename='coinLastNtxViewSet')

source_router.register(r'notary_last_ntx',
                viewsets_api.notaryLastNtxViewSet,
                basename='notaryLastNtxViewSet')

source_router.register(r'mined',
                viewsets_api.minedViewSet,
                basename='minedViewSet') 

source_router.register(r'seednode_version_stats',
                viewsets_api.mm2VersionStatsViewSet,
                basename='mm2VersionStatsViewSet')

source_router.register(r'mined_count_daily',
                viewsets_api.minedCountDailyViewSet,
                basename='minedCountDailyViewSet')

source_router.register(r'mined_count_season',
                viewsets_api.minedCountSeasonViewSet,
                basename='minedCountSeasonViewSet')

source_router.register(r'nn_btc_tx',
                viewsets_api.nnBtcTxViewSet,
                basename='nnBtcTxViewSet')

source_router.register(r'nn_ltc_tx',
                viewsets_api.nnLtcTxViewSet,
                basename='nnLtcTxViewSet')

source_router.register(r'nn_social',
                viewsets_api.nnSocialViewSet,
                basename='nnSocialViewSet')

source_router.register(r'notarised',
                viewsets_api.notarisedViewSet,
                basename='notarisedViewSet') # doc

source_router.register(r'notarised_coin_daily',
                viewsets_api.notarisedCoinDailyViewSet,
                basename='notarisedCoinDailyViewSet')

source_router.register(r'notarised_count_daily',
                viewsets_api.notarisedCountDailyViewSet,
                basename='notarisedCountDailyViewSet')

source_router.register(r'notary_ntx_season',
                viewsets_api.notaryNtxSeasonViewSet,
                basename='notaryNtxSeasonViewSet')

source_router.register(r'notarised_tenure',
                viewsets_api.notarisedTenureViewSet,
                basename='notarisedTenureViewSet')

source_router.register(r'scoring_epochs',
                viewsets_api.scoringEpochsViewSet,
                basename='scoringEpochsViewSet')

source_router.register(r'server_ntx_season',
                viewsets_api.serverNtxSeasonViewSet,
                basename='serverNtxSeasonViewSet')

source_router.register(r'rewards_tx',
                viewsets_api.rewardsTxViewSet,
                basename='rewardsTxViewSet')

source_router.register(r'notary_vote',
                viewsets_api.notaryVoteViewSet,
                basename='notaryVoteViewSet')

source_router.register(r'notary_candidates',
                viewsets_api.notaryCandidatesViewSet,
                basename='notaryCandidatesSerializer')
