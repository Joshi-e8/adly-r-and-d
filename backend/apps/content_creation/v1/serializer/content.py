from rest_framework import serializers
from apps.content_creation.models import (
    ContentAsset, ContentTemplate, GenerationJob, 
    VideoProject, ProductAnalysis
)


class ContentAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentAsset
        fields = [
            'id', 'workspace', 'type', 'name', 'file_url', 'file_size',
            'mime_type', 'metadata', 'generated_by', 'generation_prompt',
            'language', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentTemplate
        fields = [
            'id', 'workspace', 'name', 'type', 'industry', 'theme',
            'template_data', 'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GenerationJobSerializer(serializers.ModelSerializer):
    result_asset = ContentAssetSerializer(read_only=True)
    
    class Meta:
        model = GenerationJob
        fields = [
            'id', 'workspace', 'user', 'type', 'provider', 'prompt',
            'parameters', 'status', 'result_asset', 'error_message',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'result_asset', 'error_message', 'created_at', 'completed_at']


class VideoProjectSerializer(serializers.ModelSerializer):
    generated_video = ContentAssetSerializer(read_only=True)
    variations = ContentAssetSerializer(many=True, read_only=True)
    template = ContentTemplateSerializer(read_only=True)
    
    class Meta:
        model = VideoProject
        fields = [
            'id', 'workspace', 'user', 'name', 'product_url', 'script',
            'template', 'avatar_settings', 'brand_settings', 'language',
            'status', 'generated_video', 'variations', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'generated_video', 'variations', 'created_at', 'updated_at']


class ProductAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAnalysis
        fields = [
            'id', 'workspace', 'product_url', 'title', 'description',
            'price', 'currency', 'images', 'features', 'category',
            'brand', 'analysis_data', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class VideoGenerationRequestSerializer(serializers.Serializer):
    product_url = serializers.URLField(required=False)
    script = serializers.CharField(required=False, allow_blank=True)
    template_id = serializers.UUIDField(required=False)
    avatar_settings = serializers.JSONField(required=False, default=dict)
    brand_settings = serializers.JSONField(required=False, default=dict)
    language = serializers.ChoiceField(choices=[('ar', 'Arabic'), ('en', 'English')], default='ar')
    variations_count = serializers.IntegerField(min_value=1, max_value=5, default=1)
    
    def validate(self, data):
        if not data.get('product_url') and not data.get('script'):
            raise serializers.ValidationError("Either product_url or script must be provided")
        return data


class TextGenerationRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=[
        ('headline', 'Headline'),
        ('description', 'Description'),
        ('cta', 'Call to Action'),
        ('script', 'Video Script')
    ])
    product_context = serializers.CharField(required=False, allow_blank=True)
    tone = serializers.ChoiceField(choices=[
        ('professional', 'Professional'),
        ('casual', 'Casual'),
        ('festive', 'Festive'),
        ('promotional', 'Promotional'),
        ('cultural', 'Cultural')
    ], default='professional')
    language = serializers.ChoiceField(choices=[('ar', 'Arabic'), ('en', 'English')], default='ar')
    variations_count = serializers.IntegerField(min_value=1, max_value=10, default=3)


class ImageGenerationRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=1000)
    style = serializers.ChoiceField(choices=[
        ('realistic', 'Realistic'),
        ('artistic', 'Artistic'),
        ('minimalist', 'Minimalist'),
        ('vintage', 'Vintage'),
        ('modern', 'Modern')
    ], default='realistic')
    dimensions = serializers.ChoiceField(choices=[
        ('1024x1024', 'Square (1024x1024)'),
        ('1024x1792', 'Portrait (1024x1792)'),
        ('1792x1024', 'Landscape (1792x1024)')
    ], default='1024x1024')
    variations_count = serializers.IntegerField(min_value=1, max_value=4, default=1)