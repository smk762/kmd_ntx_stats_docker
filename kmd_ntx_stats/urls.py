from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from kmd_ntx_api import views

router = routers.DefaultRouter()

router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'mined', views.MinedViewSet)
router.register(r'notarised', views.ntxViewSet)
router.register(r'mined_count', views.MinedCountViewSet)
router.register(r'notarised_count', views.ntxCountViewSet)
router.register(r'decode_opret', views.decodeOpRetViewSet, basename='decode_opret')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]