from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from kmd_ntx_api import views

router = routers.DefaultRouter()

router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'notarisation/notarised', views.ntxViewSet)
router.register(r'mining/mined', views.MinedViewSet)
router.register(r'mining/s3_mining_stats_db', views.s3_mining_stats_db, basename='s3_mining_stats_db')
router.register(r'mining/s3_mining_stats', views.s3_mining_stats, basename='s3_mining_stats')
router.register(r'notarisation/s3_ntx_chain_counts', views.s3_ntx_chain_counts, basename='s3_ntx_chain_counts')
router.register(r'notarisation/s3_ntx_notary_counts', views.s3_ntx_notary_counts, basename='s3_ntx_notary_counts')
router.register(r'info/s3_ntx_chains_list', views.s3_ntx_chains_list, basename='s3_ntx_chains_list')
router.register(r'info/adresses', views.addressesViewSet)
router.register(r'info/notary_addresses_list', views.notary_addresses_list, basename='notary_addresses_list')
router.register(r'info/notary_balances', views.balancesViewSet)
router.register(r'info/s3_notary_balances', views.s3_notary_balances, basename='s3_notary_balances')
router.register(r'info/coins', views.coinsViewSet)
router.register(r'info/s3_dpow_coins', views.s3_dpow_coins, basename='s3_dpow_coins')
router.register(r'info/mm2_coins', views.mm2_coins, basename='mm2_coins')
router.register(r'info/notary_kmd_rewards', views.rewardsViewSet)
router.register(r'info/notary_names_list', views.notary_names_list, basename='notary_names_list')
router.register(r'tools/decode_opret', views.decodeOpRetViewSet, basename='decode_opret')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]