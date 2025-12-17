from django.http import HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from requests_oauthlib import OAuth1Session
import requests
import redis
import json
import logging
from urllib.parse import urlencode

from apps.ad_platforms.models import AdAccount
logger = logging.getLogger(__name__)




@csrf_exempt
def twitter_callback(request):
    oauth_token = request.GET.get("oauth_token")
    oauth_verifier = request.GET.get("oauth_verifier")
    workspace_id = None

    if not (oauth_token and oauth_verifier):
        return JsonResponse({"error": "missing_oauth_params"}, status=400)

    r = redis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))
    info_json = r.get(f"twreq:{oauth_token}")
    info = json.loads(info_json) if info_json else None
    if info:
        workspace_id = workspace_id or info.get("workspace_id")
    if not workspace_id:
        return JsonResponse({"error": "missing_workspace"}, status=400)

    consumer_key = getattr(settings, "TWITTER_CONSUMER_KEY", None)
    consumer_secret = getattr(settings, "TWITTER_CONSUMER_SECRET", None)
    if not (consumer_key and consumer_secret):
        return JsonResponse({"error": "twitter_oauth_not_configured"}, status=500)

    resource_owner_secret = info.get("secret") if info else None
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=oauth_token,
        resource_owner_secret=resource_owner_secret,
    )
    try:
        tokens = oauth.fetch_access_token("https://api.twitter.com/oauth/access_token", verifier=oauth_verifier)
    except Exception:
        return JsonResponse({"error": "token_exchange_failed"}, status=502)

    access_token = tokens.get("oauth_token")
    access_token_secret = tokens.get("oauth_token_secret")
    user_id = tokens.get("user_id")
    screen_name = tokens.get("screen_name")

    try:
        ads_oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )
        acc_resp = ads_oauth.get("https://ads-api.twitter.com/12/accounts", timeout=15)
        acc_json = acc_resp.json()
        logger.info("twitter_ads_accounts_fetch status=%s workspace=%s user=%s", acc_resp.status_code, workspace_id, user_id)
        if acc_resp.status_code != 200:
            ext_id = user_id
            existing = AdAccount.objects.filter(workspace_id=workspace_id, provider="twitter", external_account_id=ext_id).first()
            if existing:
                existing.account_name = existing.account_name or screen_name
                existing.access_token = access_token
                existing.access_token_secret = access_token_secret
                existing.scopes = []
                existing.metadata = {"screen_name": screen_name, "user_id": user_id, "ads_api_error": acc_json, "ads_api_access": False}
                existing.status = "connected"
                existing.save(update_fields=["account_name", "access_token", "access_token_secret", "scopes", "metadata", "status", "updated_at"])
            else:
                AdAccount.objects.create(
                    workspace_id=workspace_id,
                    provider="twitter",
                    account_name=screen_name,
                    external_account_id=ext_id,
                    access_token=access_token,
                    access_token_secret=access_token_secret,
                    scopes=[],
                    metadata={"screen_name": screen_name, "user_id": user_id, "ads_api_error": acc_json, "ads_api_access": False},
                    status="connected",
                )
            if info:
                try:
                    r.delete(f"twreq:{oauth_token}")
                except Exception:
                    pass
            frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
            return_url = info.get("return_url") if info else f"{frontend_url}/ad-accounts/{workspace_id}"
            return HttpResponseRedirect(return_url)
        accounts = (acc_json.get("data") or acc_json.get("accounts") or [])
        if not accounts:
            ext_id = user_id
            existing = AdAccount.objects.filter(workspace_id=workspace_id, provider="twitter", external_account_id=ext_id).first()
            if existing:
                existing.account_name = existing.account_name or screen_name
                existing.access_token = access_token
                existing.access_token_secret = access_token_secret
                existing.scopes = []
                existing.metadata = {"screen_name": screen_name, "user_id": user_id, "ads_accounts": [], "ads_api_access": False}
                existing.status = "connected"
                existing.save(update_fields=["account_name", "access_token", "access_token_secret", "scopes", "metadata", "status", "updated_at"])
            else:
                AdAccount.objects.create(
                    workspace_id=workspace_id,
                    provider="twitter",
                    account_name=screen_name,
                    external_account_id=ext_id,
                    access_token=access_token,
                    access_token_secret=access_token_secret,
                    scopes=[],
                    metadata={"screen_name": screen_name, "user_id": user_id, "ads_accounts": [], "ads_api_access": False},
                    status="connected",
                )
            if info:
                try:
                    r.delete(f"twreq:{oauth_token}")
                except Exception:
                    pass
            frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
            return_url = info.get("return_url") if info else f"{frontend_url}/ad-accounts/{workspace_id}"
            return HttpResponseRedirect(return_url)
        first = accounts[0]
        ext_id = first.get("id") or user_id
        existing = AdAccount.objects.filter(workspace_id=workspace_id, provider="twitter", external_account_id=ext_id).first()
        if existing:
            existing.account_name = first.get("name") or existing.account_name or screen_name
            existing.access_token = access_token
            existing.access_token_secret = access_token_secret
            existing.scopes = []
            existing.metadata = {"screen_name": screen_name, "user_id": user_id, "ads_accounts": accounts}
            existing.status = "connected"
            existing.save(update_fields=["account_name", "access_token", "access_token_secret", "scopes", "metadata", "status", "updated_at"])
        else:
            AdAccount.objects.create(
                workspace_id=workspace_id,
                provider="twitter",
                account_name=first.get("name") or screen_name,
                external_account_id=ext_id,
                access_token=access_token,
                access_token_secret=access_token_secret,
                scopes=[],
                metadata={"screen_name": screen_name, "user_id": user_id, "ads_accounts": accounts},
                status="connected",
            )
    except Exception:
        ext_id = user_id
        existing = AdAccount.objects.filter(workspace_id=workspace_id, provider="twitter", external_account_id=ext_id).first()
        if existing:
            existing.account_name = existing.account_name or screen_name
            existing.access_token = access_token
            existing.access_token_secret = access_token_secret
            existing.scopes = []
            existing.metadata = {"screen_name": screen_name, "user_id": user_id}
            existing.status = "connected"
            existing.save(update_fields=["account_name", "access_token", "access_token_secret", "scopes", "metadata", "status", "updated_at"])
        else:
            AdAccount.objects.create(
                workspace_id=workspace_id,
                provider="twitter",
                account_name=screen_name,
                external_account_id=ext_id,
                access_token=access_token,
                access_token_secret=access_token_secret,
                scopes=[],
                metadata={"screen_name": screen_name, "user_id": user_id},
                status="connected",
            )
        if info:
            try:
                r.delete(f"twreq:{oauth_token}")
            except Exception:
                pass
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        return_url = info.get("return_url") if info else f"{frontend_url}/ad-accounts/{workspace_id}"
        return HttpResponseRedirect(return_url)

    if info:
        try:
            r.delete(f"twreq:{oauth_token}")
        except Exception:
            pass

    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    return_url = info.get("return_url") if info else f"{frontend_url}/ad-accounts/{workspace_id}"
    return HttpResponseRedirect(return_url)

@csrf_exempt
def snapchat_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")
    workspace_id = request.GET.get("workspace_id")
    if not (code and state):
        return JsonResponse({"error": "missing_oauth_params"}, status=400)

    r = redis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))
    info_json = r.get(f"snapreq:{state}")
    info = json.loads(info_json) if info_json else None
    if not info:
        snap_sess = request.session.get("snapchat_oauth", {})
        info = snap_sess.get(state)
    if info:
        workspace_id = workspace_id or info.get("workspace_id")
    if not workspace_id:
        return JsonResponse({"error": "missing_workspace"}, status=400)

    client_id = getattr(settings, "SNAPCHAT_CLIENT_ID", None)
    client_secret = getattr(settings, "SNAPCHAT_CLIENT_SECRET", None)
    redirect_base = getattr(settings, "SNAPCHAT_REDIRECT_BASE_URL", None)
    if not (client_id and client_secret and redirect_base):
        return JsonResponse({"error": "snapchat_oauth_not_configured"}, status=500)

    redirect_uri = f"{redirect_base}"
    try:
        resp = requests.post(
            "https://accounts.snapchat.com/login/oauth2/access_token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            },
            timeout=15,
        )
        data = resp.json()
    except Exception:
        return JsonResponse({"error": "token_exchange_failed"}, status=502)

    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    scope = data.get("scope", "")
    scopes = scope.split() if isinstance(scope, str) else []

    existing = AdAccount.objects.filter(workspace_id=workspace_id, provider="snapchat").first()
    if existing:
        existing.access_token = access_token
        existing.refresh_token = refresh_token
        existing.scopes = scopes
        existing.metadata = {"raw": data}
        existing.status = "connected"
        existing.save(update_fields=["access_token", "refresh_token", "scopes", "metadata", "status", "updated_at"])
    else:
        AdAccount.objects.create(
            workspace_id=workspace_id,
            provider="snapchat",
            access_token=access_token,
            refresh_token=refresh_token,
            scopes=scopes,
            metadata={"raw": data},
            status="connected",
        )

    if info:
        try:
            r.delete(f"snapreq:{state}")
        except Exception:
            pass

    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    return_url = info.get("return_url") if info else f"{frontend_url}/ad-accounts/{workspace_id}"
    return HttpResponseRedirect(return_url)

@csrf_exempt
def meta_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")
    workspace_id = request.GET.get("workspace_id")
    if not (code and state):
        return JsonResponse({"error": "missing_oauth_params"}, status=400)

    r = redis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))
    info_json = r.get(f"fbreq:{state}")
    info = json.loads(info_json) if info_json else None
    if info:
        workspace_id = workspace_id or info.get("workspace_id")
    if not workspace_id:
        return JsonResponse({"error": "missing_workspace"}, status=400)

    app_id = getattr(settings, "META_APP_ID", None)
    app_secret = getattr(settings, "META_APP_SECRET", None)
    redirect_base = getattr(settings, "META_REDIRECT_BASE_URL", None)
    if not (app_id and app_secret and redirect_base):
        return JsonResponse({"error": "meta_oauth_not_configured"}, status=500)

    redirect_uri = f"{redirect_base}"
    try:
        token_resp = requests.get(
            "https://graph.facebook.com/v20.0/oauth/access_token",
            params={
                "client_id": app_id,
                "client_secret": app_secret,
                "redirect_uri": redirect_uri,
                "code": code,
            },
            timeout=15,
        )
        token_json = token_resp.json()
        if token_resp.status_code != 200:
            return JsonResponse({"error": "token_exchange_failed", "status": token_resp.status_code, "detail": token_json}, status=502)
    except Exception:
        return JsonResponse({"error": "token_exchange_failed"}, status=502)

    access_token = token_json.get("access_token")
    try:
        long_resp = requests.get(
            "https://graph.facebook.com/v20.0/oauth/access_token",
            params={
                "grant_type": "fb_exchange_token",
                "client_id": app_id,
                "client_secret": app_secret,
                "fb_exchange_token": access_token,
            },
            timeout=15,
        )
        long_json = long_resp.json()
        if long_resp.status_code == 200 and long_json.get("access_token"):
            access_token = long_json.get("access_token")
    except Exception:
        pass

    try:
        acc_resp = requests.get(
            "https://graph.facebook.com/v20.0/me/adaccounts",
            params={"fields": "name,account_id,account_status", "access_token": access_token},
            timeout=15,
        )
        acc_json = acc_resp.json()
        if acc_resp.status_code != 200:
            return JsonResponse({"error": "ads_api_error", "status": acc_resp.status_code, "detail": acc_json}, status=502)
        accounts = acc_json.get("data") or []
        if not accounts:
            return JsonResponse({"error": "no_ads_account", "status": acc_resp.status_code, "detail": acc_json}, status=400)
        first = accounts[0]
        ext_id = first.get("account_id")
        existing = AdAccount.objects.filter(workspace_id=workspace_id, provider="meta", external_account_id=ext_id).first()
        if existing:
            existing.account_name = first.get("name") or existing.account_name
            existing.access_token = access_token
            existing.scopes = []
            existing.metadata = {"ads_accounts": accounts}
            existing.status = "connected"
            existing.save(update_fields=["account_name", "access_token", "scopes", "metadata", "status", "updated_at"])
        else:
            AdAccount.objects.create(
                workspace_id=workspace_id,
                provider="meta",
                account_name=first.get("name"),
                external_account_id=ext_id,
                access_token=access_token,
                scopes=[],
                metadata={"ads_accounts": accounts},
                status="connected",
            )
    except Exception:
        return JsonResponse({"error": "ads_accounts_fetch_failed"}, status=502)

    if info:
        try:
            r.delete(f"fbreq:{state}")
        except Exception:
            pass

    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    return_url = info.get("return_url") if info else f"{frontend_url}/ad-accounts/{workspace_id}"
    return HttpResponseRedirect(return_url)

@csrf_exempt
def linkedin_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")
    workspace_id = request.GET.get("workspace_id")
    error = request.GET.get("error")
    error_description = request.GET.get("error_description")

    if error and state:
        r = redis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))
        info_json = r.get(f"lnreq:{state}")
        info = json.loads(info_json) if info_json else None
        if info:
            workspace_id = workspace_id or info.get("workspace_id")
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        return_url = info.get("return_url") if info else (f"{frontend_url}/ad-accounts/{workspace_id}" if workspace_id else frontend_url)
        params = {"oauth_error": error}
        if error_description:
            params["oauth_error_description"] = error_description
        sep = "&" if ("?" in return_url) else "?"
        return HttpResponseRedirect(f"{return_url}{sep}{urlencode(params)}")

    if not (code and state):
        return JsonResponse({"error": "missing_oauth_params"}, status=400)

    r = redis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))
    info_json = r.get(f"lnreq:{state}")
    info = json.loads(info_json) if info_json else None
    if info:
        workspace_id = workspace_id or info.get("workspace_id")
    if not workspace_id:
        return JsonResponse({"error": "missing_workspace"}, status=400)

    client_id = getattr(settings, "LINKEDIN_CLIENT_ID", None)
    client_secret = getattr(settings, "LINKEDIN_CLIENT_SECRET", None)
    redirect_base = getattr(settings, "LINKEDIN_REDIRECT_BASE_URL", None)
    if not (client_id and client_secret and redirect_base):
        return JsonResponse({"error": "linkedin_oauth_not_configured"}, status=500)

    redirect_uri = f"{redirect_base}"
    try:
        token_resp = requests.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            timeout=15,
        )
        token_json = token_resp.json()
        if token_resp.status_code != 200:
            return JsonResponse({"error": "token_exchange_failed", "status": token_resp.status_code, "detail": token_json}, status=502)
    except Exception:
        return JsonResponse({"error": "token_exchange_failed"}, status=502)

    access_token = token_json.get("access_token")
    try:
        me_resp = requests.get(
            "https://api.linkedin.com/v2/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
        )
        me_json = me_resp.json()
        if me_resp.status_code != 200:
            return JsonResponse({"error": "profile_fetch_failed", "status": me_resp.status_code, "detail": me_json}, status=502)
        first = me_json.get("localizedFirstName") or ""
        last = me_json.get("localizedLastName") or ""
        person_id = me_json.get("id")
        account_name = f"{first} {last}".strip() or person_id
        external_id = f"urn:li:person:{person_id}"
        existing = AdAccount.objects.filter(workspace_id=workspace_id, provider="linkedin", external_account_id=external_id).first()
        if existing:
            existing.account_name = account_name
            existing.access_token = access_token
            existing.scopes = []
            existing.metadata = {"me": me_json}
            existing.status = "connected"
            existing.save(update_fields=["account_name", "access_token", "scopes", "metadata", "status", "updated_at"])
        else:
            AdAccount.objects.create(
                workspace_id=workspace_id,
                provider="linkedin",
                account_name=account_name,
                external_account_id=external_id,
                access_token=access_token,
                scopes=[],
                metadata={"me": me_json},
                status="connected",
            )
    except Exception:
        return JsonResponse({"error": "linkedin_connect_failed"}, status=502)

    if info:
        try:
            r.delete(f"lnreq:{state}")
        except Exception:
            pass

    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    return_url = info.get("return_url") if info else f"{frontend_url}/ad-accounts/{workspace_id}"
    return HttpResponseRedirect(return_url)

@csrf_exempt
def youtube_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")
    workspace_id = request.GET.get("workspace_id")
    if not (code and state):
        return JsonResponse({"error": "missing_oauth_params"}, status=400)

    r = redis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))
    info_json = r.get(f"ytreq:{state}")
    info = json.loads(info_json) if info_json else None
    if info:
        workspace_id = workspace_id or info.get("workspace_id")
    if not workspace_id:
        return JsonResponse({"error": "missing_workspace"}, status=400)

    client_id = getattr(settings, "YOUTUBE_CLIENT_ID", None)
    client_secret = getattr(settings, "YOUTUBE_CLIENT_SECRET", None)
    redirect_base = getattr(settings, "YOUTUBE_REDIRECT_BASE_URL", None)
    if not (client_id and client_secret and redirect_base):
        return JsonResponse({"error": "youtube_oauth_not_configured"}, status=500)

    redirect_uri = f"{redirect_base}"
    try:
        token_resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=15,
        )
        token_json = token_resp.json()
        if token_resp.status_code != 200:
            return JsonResponse({"error": "token_exchange_failed", "status": token_resp.status_code, "detail": token_json}, status=502)
    except Exception:
        return JsonResponse({"error": "token_exchange_failed"}, status=502)

    access_token = token_json.get("access_token")
    refresh_token = token_json.get("refresh_token")
    scope = token_json.get("scope", "")
    scopes = scope.split() if isinstance(scope, str) else []

    try:
        ch_resp = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={"part": "snippet,contentDetails", "mine": "true"},
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
        )
        ch_json = ch_resp.json()
        if ch_resp.status_code != 200:
            return JsonResponse({"error": "channel_fetch_failed", "status": ch_resp.status_code, "detail": ch_json}, status=502)
        items = ch_json.get("items") or []
        if not items:
            return JsonResponse({"error": "no_channel"}, status=400)
        first = items[0]
        channel_id = first.get("id")
        channel_title = ((first.get("snippet") or {}).get("title"))
        existing = AdAccount.objects.filter(workspace_id=workspace_id, provider="youtube", external_account_id=channel_id).first()
        if existing:
            existing.account_name = channel_title or channel_id
            existing.access_token = access_token
            existing.refresh_token = refresh_token
            existing.scopes = scopes
            existing.metadata = {"channel": first, "raw": token_json}
            existing.status = "connected"
            existing.save(update_fields=["account_name", "access_token", "refresh_token", "scopes", "metadata", "status", "updated_at"])
        else:
            AdAccount.objects.create(
                workspace_id=workspace_id,
                provider="youtube",
                account_name=channel_title or channel_id,
                external_account_id=channel_id,
                access_token=access_token,
                refresh_token=refresh_token,
                scopes=scopes,
                metadata={"channel": first, "raw": token_json},
                status="connected",
            )
    except Exception:
        return JsonResponse({"error": "youtube_connect_failed"}, status=502)

    if info:
        try:
            r.delete(f"ytreq:{state}")
        except Exception:
            pass

    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    return_url = info.get("return_url") if info else f"{frontend_url}/ad-accounts/{workspace_id}"
    return HttpResponseRedirect(return_url)
