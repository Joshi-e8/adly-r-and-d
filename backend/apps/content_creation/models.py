import uuid
from django.db import models
from django.conf import settings
from apps.workspaces.models import Workspace


class ContentAsset(models.Model):
    ASSET_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('text', 'Text'),
    ]
    
    LANGUAGES = [
        ('ar', 'Arabic'),
        ('en', 'English'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='content_assets')
    type = models.CharField(max_length=50, choices=ASSET_TYPES)
    name = models.CharField(max_length=255)
    file_url = models.URLField(blank=True, null=True)
    file_size = models.IntegerField(blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    generated_by = models.CharField(max_length=100, blank=True, null=True)
    generation_prompt = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=10, choices=LANGUAGES, default='ar')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'content_assets'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.type})"


class ContentTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('video', 'Video Template'),
        ('image', 'Image Template'),
        ('text', 'Text Template'),
    ]
    
    INDUSTRIES = [
        ('fashion', 'Fashion'),
        ('electronics', 'Electronics'),
        ('food', 'Food & Beverage'),
        ('beauty', 'Beauty & Cosmetics'),
        ('automotive', 'Automotive'),
        ('real_estate', 'Real Estate'),
        ('health', 'Health & Wellness'),
        ('education', 'Education'),
        ('travel', 'Travel & Tourism'),
        ('general', 'General'),
    ]
    
    THEMES = [
        ('ramadan', 'Ramadan'),
        ('eid', 'Eid'),
        ('national_day', 'National Day'),
        ('new_year', 'New Year'),
        ('summer', 'Summer'),
        ('winter', 'Winter'),
        ('back_to_school', 'Back to School'),
        ('general', 'General'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='content_templates', null=True, blank=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    industry = models.CharField(max_length=50, choices=INDUSTRIES, default='general')
    theme = models.CharField(max_length=50, choices=THEMES, default='general')
    template_data = models.JSONField()
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'content_templates'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.type})"


class GenerationJob(models.Model):
    JOB_TYPES = [
        ('text', 'Text Generation'),
        ('image', 'Image Generation'),
        ('video', 'Video Generation'),
        ('voice', 'Voice Generation'),
        ('script', 'Script Generation'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    PROVIDERS = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('stability', 'Stability AI'),
        ('elevenlabs', 'ElevenLabs'),
        ('heygen', 'HeyGen'),
        ('synthesia', 'Synthesia'),
        ('runway', 'Runway ML'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='generation_jobs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=50, choices=JOB_TYPES)
    provider = models.CharField(max_length=100, choices=PROVIDERS)
    prompt = models.TextField()
    parameters = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    result_asset = models.ForeignKey(ContentAsset, on_delete=models.SET_NULL, null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'generation_jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} job - {self.status}"


class VideoProject(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='video_projects')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    product_url = models.URLField(blank=True, null=True)
    script = models.TextField(blank=True, null=True)
    template = models.ForeignKey(ContentTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    avatar_settings = models.JSONField(default=dict, blank=True)
    brand_settings = models.JSONField(default=dict, blank=True)
    language = models.CharField(max_length=10, default='ar')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    generated_video = models.ForeignKey(ContentAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name='video_projects')
    variations = models.ManyToManyField(ContentAsset, blank=True, related_name='video_project_variations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'video_projects'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.status}"


class ProductAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='product_analyses')
    product_url = models.URLField()
    title = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, default='SAR')
    images = models.JSONField(default=list, blank=True)
    features = models.JSONField(default=list, blank=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    analysis_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_analyses'
        ordering = ['-created_at']
        unique_together = ['workspace', 'product_url']

    def __str__(self):
        return f"Analysis: {self.title or self.product_url}"