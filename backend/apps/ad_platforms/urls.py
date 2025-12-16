from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.ad_platforms.v1.views.ad_account import AdAccountViewSet


router = DefaultRouter()
router.register(r'ad-accounts', AdAccountViewSet, basename='ad-accounts')

urlpatterns = [
    path('v1/', include(router.urls)),
]
