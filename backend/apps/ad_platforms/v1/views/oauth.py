from django.http import HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from requests_oauthlib import OAuth1Session
import requests
import redis
import json
import logging

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
            logger.warning("twitter_ads_accounts_error status=%s errors=%s", acc_resp.status_code, acc_json.get("errors"))
            return JsonResponse({"error": "ads_api_error", "status": acc_resp.status_code, "detail": acc_json}, status=502)
        accounts = (acc_json.get("data") or acc_json.get("accounts") or [])
        if not accounts:
            logger.info("twitter_ads_accounts_empty status=%s workspace=%s user=%s", acc_resp.status_code, workspace_id, user_id)
            return JsonResponse({"error": "no_ads_account", "status": acc_resp.status_code, "detail": acc_json}, status=400)
        first = accounts[0]
        AdAccount.objects.create(
            workspace_id=workspace_id,
            provider="twitter",
            account_name=first.get("name") or screen_name,
            external_account_id=first.get("id") or user_id,
            access_token=access_token,
            access_token_secret=access_token_secret,
            scopes=[],
            metadata={"screen_name": screen_name, "user_id": user_id, "ads_accounts": accounts},
            status="connected",
        )
    except Exception:
        return JsonResponse({"error": "ads_accounts_fetch_failed"}, status=502)

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

    account = AdAccount.objects.create(
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
            del snap_sess[state]
        except Exception:
            pass
        request.session["snapchat_oauth"] = snap_sess

    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    return_url = info.get("return_url") if info else f"{frontend_url}/ad-accounts/{workspace_id}"
    return HttpResponseRedirect(return_url)
