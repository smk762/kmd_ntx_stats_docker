from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from kmd_ntx_api import views

router = routers.DefaultRouter()

router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'notary/s3/mining', views.s3_mining_stats, basename='s3_mining_stats')
router.register(r'notary/s3/notarisation', views.s3_ntx_notary_counts, basename='s3_ntx_notary_counts')
router.register(r'notary/s3/chain_notarisation', views.s3_ntx_chain_counts, basename='s3_ntx_chain_counts')
router.register(r'notary/s3/dpow_coins', views.s3_dpow_coins, basename='s3_dpow_coins')
router.register(r'notary/s3/notary_addresses', views.s3_notary_addresses_list, basename='s3_notary_addresses_list')
router.register(r'notary/s3/notary_balances', views.s3_notary_balances, basename='s3_notary_balances')
router.register(r'notary/s3/notary_names', views.s3_notary_names_list, basename='s3_notary_names_list')

router.register(r'coins/mm2_coins', views.mm2_coins, basename='mm2_coins')
router.register(r'coins/electrums', views.coin_electrums, basename='coin_electrums')
router.register(r'coins/explorers', views.coin_explorers, basename='coin_explorers')

router.register(r'source/adresses', views.addressesViewSet)
router.register(r'source/balances', views.balancesViewSet)
router.register(r'source/notarised', views.ntxViewSet)
router.register(r'source/mined', views.MinedViewSet)
router.register(r'source/notary_balances', views.balancesViewSet)
router.register(r'source/coins', views.coinsViewSet)
router.register(r'source/notary_kmd_rewards', views.rewardsViewSet)

router.register(r'info/notary_addresses_list', views.notary_addresses_list, basename='notary_addresses_list')
router.register(r'info/notary_names_list', views.notary_names_list, basename='notary_names_list')

router.register(r'tools/decode_opret', views.decodeOpRetViewSet, basename='decode_opret')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]