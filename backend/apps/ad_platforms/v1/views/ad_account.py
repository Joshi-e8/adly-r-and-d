from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
from urllib.parse import urlencode
from requests_oauthlib import OAuth1Session
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

        account = AdAccount.objects.create(
            workspace_id=workspace_id,
            provider=data.get("provider"),
            account_name=data.get("account_name"),
            external_account_id=data.get("external_account_id"),
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
        snap_sess = request.session.get("snapchat_oauth", {})
        snap_sess[state] = {
            "workspace_id": str(workspace_id),
            "return_url": f"{frontend_url}/ad-accounts/{workspace_id}",
        }
        request.session["snapchat_oauth"] = snap_sess

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "snapchat-marketing-api",
            "state": state,
        }
        authorization_url = f"https://accounts.snapchat.com/login/oauth2/authorize?{urlencode(params)}"
        return Response({"authorization_url": authorization_url})
