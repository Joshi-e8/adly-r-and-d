from rest_framework import serializers
from apps.ad_platforms.models import AdAccount


class AdAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdAccount
        fields = [
            "id",
            "workspace",
            "provider",
            "account_name",
            "external_account_id",
            "status",
            "scopes",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "workspace", "status"]


class AdAccountConnectSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=[("twitter", "Twitter"), ("snapchat", "Snapchat")])
    account_name = serializers.CharField(required=False, allow_blank=True)
    external_account_id = serializers.CharField(required=False, allow_blank=True)
    access_token = serializers.CharField(required=False, allow_blank=True)
    access_token_secret = serializers.CharField(required=False, allow_blank=True)
    refresh_token = serializers.CharField(required=False, allow_blank=True)
    scopes = serializers.ListField(child=serializers.CharField(), required=False)
    metadata = serializers.DictField(required=False)
