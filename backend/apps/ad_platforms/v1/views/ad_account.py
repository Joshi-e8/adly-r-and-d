from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
from urllib.parse import urlencode
from requests_oauthlib import OAuth1Session
import requests
import json
import redis
import json
import redis
from apps.workspaces.permissions.permission import WorkspacePermission
from apps.ad_platforms.models import AdAccount
from apps.ad_platforms.v1.serializer.ad_account import (
    AdAccountSerializer,
    AdAccountConnectSerializer,
)


class AdAccountViewSet(viewsets.ModelViewSet):
    serializer_class = AdAccountSerializer
    permission_classes = [IsAuthenticated, WorkspacePermission]

    def get_queryset(self):
        workspace_id = self.kwargs.get("workspace_id")
        return AdAccount.objects.filter(workspace_id=workspace_id)

    def create(self, request, *args, **kwargs):
        workspace_id = self.kwargs.get("workspace_id")
        serializer = AdAccountConnectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        ext_id = data.get("external_account_id")
        provider = data.get("provider")
        existing = None
        if ext_id:
            existing = AdAccount.objects.filter(workspace_id=workspace_id, provider=provider, external_account_id=ext_id).first()
        else:
            existing = AdAccount.objects.filter(workspace_id=workspace_id, provider=provider).first()

        if existing:
            existing.account_name = data.get("account_name") or existing.account_name
            existing.access_token = data.get("access_token") or existing.access_token
            existing.access_token_secret = data.get("access_token_secret") or existing.access_token_secret
            existing.refresh_token = data.get("refresh_token") or existing.refresh_token
            existing.scopes = data.get("scopes") or existing.scopes
            existing.metadata = data.get("metadata") or existing.metadata
            existing.status = "connected"
            existing.save(update_fields=[
                "account_name",
                "access_token",
                "access_token_secret",
                "refresh_token",
                "scopes",
                "metadata",
                "status",
                "updated_at",
            ])
            return Response(AdAccountSerializer(existing).data, status=status.HTTP_200_OK)

        account = AdAccount.objects.create(
            workspace_id=workspace_id,
            provider=provider,
            account_name=data.get("account_name"),
            external_account_id=ext_id,
            access_token=data.get("access_token"),
            access_token_secret=data.get("access_token_secret"),
            refresh_token=data.get("refresh_token"),
            scopes=data.get("scopes") or [],
            metadata=data.get("metadata") or {},
            created_by=request.user,
            status="connected",
        )

        return Response(AdAccountSerializer(account).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="disconnect")
    def disconnect(self, request, workspace_id=None, pk=None):
        account = get_object_or_404(AdAccount, pk=pk, workspace_id=workspace_id)
        account.status = "disconnected"
        account.save(update_fields=["status", "updated_at"])
        return Response({"status": "disconnected"})

    @action(detail=True, methods=["post"], url_path="validate")
    def validate(self, request, workspace_id=None, pk=None):
        account = get_object_or_404(AdAccount, pk=pk, workspace_id=workspace_id)
        return Response({"provider": account.provider, "status": "ok"})


    @action(detail=False, methods=["get"], url_path="twitter/start")
    def twitter_start(self, request, workspace_id=None):
        consumer_key = getattr(settings, "TWITTER_CONSUMER_KEY", None)
        consumer_secret = getattr(settings, "TWITTER_CONSUMER_SECRET", None)
        callback_base = getattr(settings, "TWITTER_CALLBACK_BASE_URL", None)
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")

        if not (consumer_key and consumer_secret and callback_base):
            return Response({"error": "Twitter Ads OAuth not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        callback_uri = f"{callback_base}"
        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, callback_uri=callback_uri)
        try:
            fetch_response = oauth.fetch_request_token("https://api.twitter.com/oauth/request_token?x_auth_access_type=write")
        except Exception as e:
            return Response({"error": "Failed to initialize Twitter Ads OAuth", "detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")

        r = redis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))
        r.setex(
            f"twreq:{resource_owner_key}",
            600,
            json.dumps({
                "secret": resource_owner_secret,
                "workspace_id": str(workspace_id),
                "return_url": f"{frontend_url}/ad-accounts/{workspace_id}",
            }),
        )
        authorization_url = f"https://api.twitter.com/oauth/authorize?{urlencode({'oauth_token': resource_owner_key})}"
        return Response({"authorization_url": authorization_url})

    @action(detail=False, methods=["get"], url_path="snapchat/start")
    def snapchat_start(self, request, workspace_id=None):
        client_id = getattr(settings, "SNAPCHAT_CLIENT_ID", None)
        redirect_base = getattr(settings, "SNAPCHAT_REDIRECT_BASE_URL", None)
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")

        if not (client_id and redirect_base):
            return Response({"error": "Snapchat OAuth not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        redirect_uri = f"{redirect_base}"
        import secrets
        state = secrets.token_urlsafe(16)
        r = redis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))
        r.setex(
            f"snapreq:{state}",
            600,
            json.dumps({
                "workspace_id": str(workspace_id),
                "return_url": f"{frontend_url}/ad-accounts/{workspace_id}",
            }),
        )

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "snapchat-marketing-api",
            "state": state,
        }
        authorization_url = f"https://accounts.snapchat.com/login/oauth2/authorize?{urlencode(params)}"
        return Response({"authorization_url": authorization_url})

    @action(detail=False, methods=["get"], url_path="meta/start")
    def meta_start(self, request, workspace_id=None):
        app_id = getattr(settings, "META_APP_ID", None)
        redirect_base = getattr(settings, "META_REDIRECT_BASE_URL", None)
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")

        if not (app_id and redirect_base):
            return Response({"error": "Meta OAuth not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        redirect_uri = f"{redirect_base}"
        import secrets
        state = secrets.token_urlsafe(16)

        r = redis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))
        r.setex(
            f"fbreq:{state}",
            600,
            json.dumps({
                "workspace_id": str(workspace_id),
                "return_url": f"{frontend_url}/ad-accounts/{workspace_id}",
            }),
        )

        params = {
            "client_id": app_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
            "scope": "ads_management,ads_read,business_management",
        }
        authorization_url = f"https://www.facebook.com/v20.0/dialog/oauth?{urlencode(params)}"
        return Response({"authorization_url": authorization_url})

    @action(detail=False, methods=["post"], url_path="meta/upload-ad")
    def meta_upload_ad(self, request, workspace_id=None):
        ad_account_id = request.data.get("ad_account_id")
        page_id = request.data.get("page_id")
        message = request.data.get("message")
        link_url = request.data.get("link_url")
        creative_type = request.data.get("creative_type") or "image"
        media = request.FILES.get("media")

        if not page_id:
            return Response({"error": "missing_page_id"}, status=status.HTTP_400_BAD_REQUEST)

        account = None
        if ad_account_id:
            account = AdAccount.objects.filter(workspace_id=workspace_id, provider="meta", external_account_id=ad_account_id).first()
        else:
            account = AdAccount.objects.filter(workspace_id=workspace_id, provider="meta").first()
        if not account:
            return Response({"error": "no_meta_account"}, status=status.HTTP_400_BAD_REQUEST)

        token = account.access_token
        act_id = f"act_{account.external_account_id}"

        try:
            if creative_type == "video":
                files = {"source": media} if media else None
                resp = requests.post(
                    f"https://graph.facebook.com/v20.0/{act_id}/advideos",
                    params={"access_token": token},
                    files=files,
                    timeout=30,
                )
                data = resp.json()
                if resp.status_code != 200:
                    return Response({"error": "video_upload_failed", "status": resp.status_code, "detail": data}, status=status.HTTP_502_BAD_GATEWAY)
                video_id = data.get("id")
                object_story_spec = {
                    "page_id": page_id,
                    "video_data": {
                        "video_id": video_id,
                        "message": message or "",
                    },
                }
            else:
                files = {"bytes": media} if media else None
                resp = requests.post(
                    f"https://graph.facebook.com/v20.0/{act_id}/adimages",
                    params={"access_token": token},
                    files=files,
                    timeout=30,
                )
                data = resp.json()
                if resp.status_code != 200:
                    return Response({"error": "image_upload_failed", "status": resp.status_code, "detail": data}, status=status.HTTP_502_BAD_GATEWAY)
                img = (data.get("images") or [{}])[0]
                image_hash = img.get("hash")
                object_story_spec = {
                    "page_id": page_id,
                    "link_data": {
                        "image_hash": image_hash,
                        "link": link_url or "",
                        "message": message or "",
                    },
                }

            resp = requests.post(
                f"https://graph.facebook.com/v20.0/{act_id}/adcreatives",
                data={
                    "access_token": token,
                    "object_story_spec": json.dumps(object_story_spec),
                    "name": request.data.get("name") or "ADLY Creative",
                },
                timeout=30,
            )
            cr_json = resp.json()
            if resp.status_code != 200:
                return Response({"error": "creative_create_failed", "status": resp.status_code, "detail": cr_json}, status=status.HTTP_502_BAD_GATEWAY)
            creative_id = cr_json.get("id")
            return Response({"creative_id": creative_id, "status": "created", "detail": cr_json})
        except Exception as e:
            return Response({"error": "meta_upload_error", "detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    @action(detail=False, methods=["get"], url_path="meta/pages")
    def meta_list_pages(self, request, workspace_id=None):
        ad_account_id = request.GET.get("ad_account_id")
        account = None
        if ad_account_id:
            account = AdAccount.objects.filter(workspace_id=workspace_id, provider="meta", external_account_id=ad_account_id).first()
        else:
            account = AdAccount.objects.filter(workspace_id=workspace_id, provider="meta").first()
        if not account:
            return Response({"error": "no_meta_account"}, status=status.HTTP_400_BAD_REQUEST)

        token = account.access_token
        try:
            resp = requests.get(
                "https://graph.facebook.com/v20.0/me/accounts",
                params={"fields": "id,name", "limit": 200, "access_token": token},
                timeout=15,
            )
            data = resp.json()
            if resp.status_code != 200:
                return Response({"error": "pages_fetch_failed", "status": resp.status_code, "detail": data}, status=status.HTTP_502_BAD_GATEWAY)
            pages = data.get("data") or []
            return Response({"pages": pages})
        except Exception as e:
            return Response({"error": "pages_fetch_error", "detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    @action(detail=False, methods=["get"], url_path="linkedin/start")
    def linkedin_start(self, request, workspace_id=None):
        client_id = getattr(settings, "LINKEDIN_CLIENT_ID", None)
        redirect_base = getattr(settings, "LINKEDIN_REDIRECT_BASE_URL", None)
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        scopes = getattr(settings, "LINKEDIN_SCOPES", "r_liteprofile") or "r_liteprofile"

        if not (client_id and redirect_base):
            return Response({"error": "LinkedIn OAuth not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        redirect_uri = f"{redirect_base}"
        import secrets
        state = secrets.token_urlsafe(16)

        r = redis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))
        r.setex(
            f"lnreq:{state}",
            600,
            json.dumps({
                "workspace_id": str(workspace_id),
                "return_url": f"{frontend_url}/ad-accounts/{workspace_id}",
            }),
        )

        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": scopes,
        }
        authorization_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
        return Response({"authorization_url": authorization_url})

    @action(detail=False, methods=["get"], url_path="youtube/start")
    def youtube_start(self, request, workspace_id=None):
        client_id = getattr(settings, "YOUTUBE_CLIENT_ID", None)
        redirect_base = getattr(settings, "YOUTUBE_REDIRECT_BASE_URL", None)
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        scopes = getattr(settings, "YOUTUBE_SCOPES", "openid email profile https://www.googleapis.com/auth/youtube.readonly") or "openid email profile https://www.googleapis.com/auth/youtube.readonly"

        if not (client_id and redirect_base):
            return Response({"error": "YouTube OAuth not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        redirect_uri = f"{redirect_base}"
        import secrets
        state = secrets.token_urlsafe(16)

        r = redis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))
        r.setex(
            f"ytreq:{state}",
            600,
            json.dumps({
                "workspace_id": str(workspace_id),
                "return_url": f"{frontend_url}/ad-accounts/{workspace_id}",
            }),
        )

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scopes,
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
        }
        authorization_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        return Response({"authorization_url": authorization_url})
