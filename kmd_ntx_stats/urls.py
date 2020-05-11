from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from kmd_ntx_api import views

router = routers.DefaultRouter()

#admin
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

# auto-filterable
router.register(r'addresses', views.addresses_filter, basename='addresses_filter')
router.register(r'balances', views.balances_filter, basename='balances_filter')
router.register(r'coins', views.coins_filter, basename='coins_filter')
router.register(r'mined', views.mined_filter, basename='mined_filter')
router.register(r'mined_count_season', views.mined_count_season_filter, basename='mined_count_season_filter')
router.register(r'mined_count_date', views.mined_count_date_filter, basename='mined_count_date_filter')
router.register(r'notarised', views.notarised_filter, basename='notarised_filter')
router.register(r'notarised_chain_season', views.notarised_chain_season_filter, basename='notarised_chain_season_filter')
router.register(r'notarised_count_season', views.notarised_count_season_filter, basename='notarised_count_season_filter')
router.register(r'notarised_chain_date', views.notarised_chain_date_filter, basename='notarised_chain_date_filter')
router.register(r'notarised_count_date', views.notarised_count_date_filter, basename='notarised_count_date_filter')
router.register(r'notary_rewards', views.rewards_filter, basename='rewards_filter')

# simple lists
router.register(r'notary_names', views.notary_names, basename='notary_names')

# source
router.register(r'source/addresses', views.addressesViewSet)
router.register(r'source/balances', views.balancesViewSet)
router.register(r'source/coins', views.coinsViewSet)
router.register(r'source/mined', views.MinedViewSet)
router.register(r'source/mined_count_season', views.MinedCountSeasonViewSet)
router.register(r'source/notarised', views.ntxViewSet)
router.register(r'source/notarised_chain_season', views.ntxChainSeasonViewSet)
router.register(r'source/notarised_count_season', views.ntxCountSeasonViewSet)
router.register(r'source/notary_rewards', views.rewardsViewSet)

# tools 
router.register(r'tools/decode_opret', views.decodeOpRetViewSet, basename='decode_opret')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]