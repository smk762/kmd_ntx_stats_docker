from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from kmd_ntx_api import views

router = routers.DefaultRouter()

router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'notarisation/notarised', views.ntxViewSet)
router.register(r'notarisation/notarised_chains', views.notarised_chains, basename='notarised_chains')
router.register(r'notarisation/ntx_chain_counts', views.ntx_chain_counts, basename='ntx_chain_counts')
router.register(r'notarisation/ntx_notary_counts', views.ntx_notary_counts, basename='ntx_notary_counts')
#	router.register(r'notarisation/ntx_chain_counts/{chain}', views.ntx_chain_counts, basename='ntx_chain_counts')
router.register(r'mining/mined', views.MinedViewSet)
router.register(r'mining/mined_count', views.MinedCountViewSet)
router.register(r'mining/season3_mining_stats', views.season3_mining_stats, basename='season3_mining_stats')
router.register(r'info/notary_addresses', views.notary_addresses, basename='notary_addresses')
router.register(r'info/notary_names', views.notary_names, basename='notary_names')
router.register(r'tools/decode_opret', views.decodeOpRetViewSet, basename='decode_opret')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]