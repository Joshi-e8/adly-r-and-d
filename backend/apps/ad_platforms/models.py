import uuid
from django.db import models
from django.conf import settings
from apps.workspaces.models import Workspace


class AdAccount(models.Model):
    PROVIDERS = [
        ("twitter", "Twitter"),
        ("snapchat", "Snapchat"),
        ("meta", "Meta"),
        ("tiktok", "TikTok"),
    ]

    STATUSES = [
        ("connected", "Connected"),
        ("disconnected", "Disconnected"),
        ("error", "Error"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="ad_accounts")
    provider = models.CharField(max_length=50, choices=PROVIDERS)
    account_name = models.CharField(max_length=255, blank=True, null=True)
    external_account_id = models.CharField(max_length=255, blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    access_token_secret = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    scopes = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=50, choices=STATUSES, default="connected")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ad_accounts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.workspace_id} - {self.provider} - {self.external_account_id or self.account_name or self.id}"
