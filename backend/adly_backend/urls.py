"""
URL configuration for adly_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from apps.ad_platforms.v1.views.oauth import twitter_callback, snapchat_callback, meta_callback, linkedin_callback, youtube_callback

def health_check(request):
    return JsonResponse({'status': 'healthy', 'message': 'ADLY API is running'})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/workspaces/", include("apps.workspaces.urls")),
    path("api/v1/workspaces/<uuid:workspace_id>/content/", include("apps.content_creation.urls")),
    path("api/v1/workspaces/<uuid:workspace_id>/ad-accounts/", include("apps.ad_platforms.urls")),
    path("api/v1/ad-accounts/oauth/twitter/callback/", twitter_callback, name="twitter_oauth_callback"),
    path("api/v1/ad-accounts/oauth/snapchat/callback/", snapchat_callback, name="snapchat_oauth_callback"),
    path("api/v1/ad-accounts/oauth/meta/callback/", meta_callback, name="meta_oauth_callback"),
    path("api/v1/ad-accounts/oauth/linkedin/callback/", linkedin_callback, name="linkedin_oauth_callback"),
    path("api/v1/ad-accounts/oauth/youtube/callback/", youtube_callback, name="youtube_oauth_callback"),
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("health/", health_check, name="health_check"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
