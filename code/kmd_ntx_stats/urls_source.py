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

# TODO: Awaiting delegation to crons / db table
#source_router.register(r'chain_sync',
#                viewsets_api.chainSyncViewSet,
#                basename='chainSyncViewSet')

source_router.register(r'coins',
                viewsets_api.coinsViewSet,
                basename='coinsViewSet')

source_router.register(r'coin_social',
                viewsets_api.coinSocialViewSet,
                basename='coinSocialViewSet')

# TODO: Not in use, will implement S5
#source_router.register(r'funding_transactions',
#                viewsets_api.fundingTXViewSet,
#                basename='fundingTXViewSet')

source_router.register(r'last_notarised',
                viewsets_api.lastNotarisedViewSet,
                basename='lastNotarisedViewSet')

source_router.register(r'mined',
                viewsets_api.minedViewSet,
                basename='minedViewSet') 

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

source_router.register(r'notarised_chain_daily',
                viewsets_api.notarisedChainDailyViewSet,
                basename='notarisedChainDailyViewSet')

source_router.register(r'notarised_chain_season',
                viewsets_api.notarisedChainSeasonViewSet,
                basename='notarisedChainSeasonViewSet')

source_router.register(r'notarised_count_daily',
                viewsets_api.notarisedCountDailyViewSet,
                basename='notarisedCountDailyViewSet')

source_router.register(r'notarised_count_season',
                viewsets_api.notarisedCountSeasonViewSet,
                basename='notarisedCountSeasonViewSet')

source_router.register(r'notarised_tenure',
                viewsets_api.notarisedTenureViewSet,
                basename='notarisedTenureViewSet')

source_router.register(r'scoring_epochs',
                viewsets_api.scoringEpochsViewSet,
                basename='scoringEpochsViewSet')
