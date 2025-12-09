from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.content_creation.v1.views.content import (
    ContentAssetViewSet, ContentTemplateViewSet, GenerationJobViewSet,
    VideoProjectViewSet, ProductAnalysisViewSet, GenerationAPIViewSet
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'assets', ContentAssetViewSet, basename='content-assets')
router.register(r'templates', ContentTemplateViewSet, basename='content-templates')
router.register(r'jobs', GenerationJobViewSet, basename='generation-jobs')
router.register(r'video-projects', VideoProjectViewSet, basename='video-projects')
router.register(r'product-analysis', ProductAnalysisViewSet, basename='product-analysis')
router.register(r'generate', GenerationAPIViewSet, basename='generation-api')

urlpatterns = [
    path('v1/', include(router.urls)),
]