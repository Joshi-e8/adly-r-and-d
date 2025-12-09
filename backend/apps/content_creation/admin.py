from django.contrib import admin
from apps.content_creation.models import (
    ContentAsset, ContentTemplate, GenerationJob, 
    VideoProject, ProductAnalysis
)


@admin.register(ContentAsset)
class ContentAssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'workspace', 'language', 'generated_by', 'created_at']
    list_filter = ['type', 'language', 'generated_by', 'created_at']
    search_fields = ['name', 'generation_prompt']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'type', 'workspace', 'language')
        }),
        ('File Details', {
            'fields': ('file_url', 'file_size', 'mime_type', 'metadata')
        }),
        ('Generation Details', {
            'fields': ('generated_by', 'generation_prompt')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ContentTemplate)
class ContentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'industry', 'theme', 'is_public', 'created_at']
    list_filter = ['type', 'industry', 'theme', 'is_public', 'created_at']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'type', 'workspace', 'is_public')
        }),
        ('Categorization', {
            'fields': ('industry', 'theme')
        }),
        ('Template Data', {
            'fields': ('template_data',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(GenerationJob)
class GenerationJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'provider', 'status', 'workspace', 'user', 'created_at']
    list_filter = ['type', 'provider', 'status', 'created_at']
    search_fields = ['prompt', 'error_message']
    readonly_fields = ['id', 'created_at', 'completed_at']
    
    fieldsets = (
        ('Job Information', {
            'fields': ('workspace', 'user', 'type', 'provider', 'status')
        }),
        ('Generation Details', {
            'fields': ('prompt', 'parameters')
        }),
        ('Results', {
            'fields': ('result_asset', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(VideoProject)
class VideoProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'language', 'workspace', 'user', 'created_at']
    list_filter = ['status', 'language', 'created_at']
    search_fields = ['name', 'product_url', 'script']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Project Information', {
            'fields': ('name', 'workspace', 'user', 'status', 'language')
        }),
        ('Content Details', {
            'fields': ('product_url', 'script', 'template')
        }),
        ('Settings', {
            'fields': ('avatar_settings', 'brand_settings')
        }),
        ('Generated Content', {
            'fields': ('generated_video', 'variations')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ProductAnalysis)
class ProductAnalysisAdmin(admin.ModelAdmin):
    list_display = ['title', 'product_url', 'price', 'currency', 'workspace', 'created_at']
    list_filter = ['currency', 'category', 'created_at']
    search_fields = ['title', 'product_url', 'brand']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('workspace', 'product_url', 'title', 'brand', 'category')
        }),
        ('Product Details', {
            'fields': ('description', 'price', 'currency', 'images', 'features')
        }),
        ('Analysis Data', {
            'fields': ('analysis_data',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )