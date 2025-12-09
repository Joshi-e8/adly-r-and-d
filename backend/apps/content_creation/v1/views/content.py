from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models
from apps.workspaces.permissions.permission import WorkspacePermission
from apps.content_creation.models import (
    ContentAsset, ContentTemplate, GenerationJob, 
    VideoProject, ProductAnalysis
)
from apps.content_creation.v1.serializer.content import (
    ContentAssetSerializer, ContentTemplateSerializer, GenerationJobSerializer,
    VideoProjectSerializer, ProductAnalysisSerializer, VideoGenerationRequestSerializer,
    TextGenerationRequestSerializer, ImageGenerationRequestSerializer
)
from apps.content_creation.services.generation_service import GenerationService
from apps.content_creation.services.product_analyzer import ProductAnalyzer


class ContentAssetViewSet(viewsets.ModelViewSet):
    serializer_class = ContentAssetSerializer
    permission_classes = [IsAuthenticated, WorkspacePermission]
    
    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        return ContentAsset.objects.filter(workspace_id=workspace_id)
    
    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        serializer.save(workspace_id=workspace_id)


class ContentTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ContentTemplateSerializer
    permission_classes = [IsAuthenticated, WorkspacePermission]
    
    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        # Include both workspace-specific and public templates
        return ContentTemplate.objects.filter(
            models.Q(workspace_id=workspace_id) | models.Q(is_public=True)
        )
    
    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        serializer.save(workspace_id=workspace_id)
    
    @action(detail=False, methods=['get'])
    def public(self, request, workspace_id=None):
        """Get public templates"""
        templates = ContentTemplate.objects.filter(is_public=True)
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_industry(self, request, workspace_id=None):
        """Get templates by industry"""
        industry = request.query_params.get('industry')
        if not industry:
            return Response({'error': 'Industry parameter required'}, status=400)
        
        templates = self.get_queryset().filter(industry=industry)
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_theme(self, request, workspace_id=None):
        """Get templates by theme"""
        theme = request.query_params.get('theme')
        if not theme:
            return Response({'error': 'Theme parameter required'}, status=400)
        
        templates = self.get_queryset().filter(theme=theme)
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)


class GenerationJobViewSet(viewsets.ModelViewSet):
    serializer_class = GenerationJobSerializer
    permission_classes = [IsAuthenticated, WorkspacePermission]
    http_method_names = ['get', 'post', 'delete']
    
    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        return GenerationJob.objects.filter(workspace_id=workspace_id)
    
    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        serializer.save(workspace_id=workspace_id, user=self.request.user)


class VideoProjectViewSet(viewsets.ModelViewSet):
    serializer_class = VideoProjectSerializer
    permission_classes = [IsAuthenticated, WorkspacePermission]
    
    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        return VideoProject.objects.filter(workspace_id=workspace_id)
    
    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        serializer.save(workspace_id=workspace_id, user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def generate(self, request, workspace_id=None, pk=None):
        """Generate video for project"""
        project = self.get_object()
        
        try:
            generation_service = GenerationService()
            job = generation_service.generate_video_from_project(project)
            
            return Response({
                'message': 'Video generation started',
                'job_id': job.id,
                'status': job.status
            })
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, workspace_id=None, pk=None):
        """Regenerate video with variations"""
        project = self.get_object()
        variations_count = request.data.get('variations_count', 1)
        
        try:
            generation_service = GenerationService()
            jobs = generation_service.generate_video_variations(project, variations_count)
            
            return Response({
                'message': f'Generating {len(jobs)} video variations',
                'job_ids': [job.id for job in jobs]
            })
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductAnalysisViewSet(viewsets.ModelViewSet):
    serializer_class = ProductAnalysisSerializer
    permission_classes = [IsAuthenticated, WorkspacePermission]
    http_method_names = ['get', 'post', 'delete']
    
    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        return ProductAnalysis.objects.filter(workspace_id=workspace_id)
    
    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        serializer.save(workspace_id=workspace_id)


class GenerationAPIViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, WorkspacePermission]
    
    @action(detail=False, methods=['post'])
    def generate_video(self, request, workspace_id=None):
        """Generate video from product URL or script"""
        serializer = VideoGenerationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        try:
            generation_service = GenerationService()
            
            # Create video project
            project_data = {
                'workspace_id': workspace_id,
                'user': request.user,
                'name': f"Video - {serializer.validated_data.get('product_url', 'Custom Script')}",
                'product_url': serializer.validated_data.get('product_url'),
                'script': serializer.validated_data.get('script'),
                'avatar_settings': serializer.validated_data.get('avatar_settings', {}),
                'brand_settings': serializer.validated_data.get('brand_settings', {}),
                'language': serializer.validated_data.get('language', 'ar')
            }
            
            project = VideoProject.objects.create(**project_data)
            
            # Start generation
            job = generation_service.generate_video_from_project(project)
            
            return Response({
                'project_id': project.id,
                'job_id': job.id,
                'status': job.status,
                'message': 'Video generation started'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_text(self, request, workspace_id=None):
        """Generate text content (headlines, descriptions, CTAs, scripts)"""
        serializer = TextGenerationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        try:
            generation_service = GenerationService()
            job = generation_service.generate_text(
                workspace_id=workspace_id,
                user=request.user,
                **serializer.validated_data
            )
            
            return Response({
                'job_id': job.id,
                'status': job.status,
                'message': 'Text generation started'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_image(self, request, workspace_id=None):
        """Generate images for display ads"""
        serializer = ImageGenerationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        try:
            generation_service = GenerationService()
            job = generation_service.generate_image(
                workspace_id=workspace_id,
                user=request.user,
                **serializer.validated_data
            )
            
            return Response({
                'job_id': job.id,
                'status': job.status,
                'message': 'Image generation started'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def analyze_product(self, request, workspace_id=None):
        """Analyze product from URL"""
        product_url = request.data.get('product_url')
        if not product_url:
            return Response({'error': 'product_url is required'}, status=400)
        
        try:
            analyzer = ProductAnalyzer()
            analysis = analyzer.analyze_product(workspace_id, product_url)
            
            serializer = ProductAnalysisSerializer(analysis)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )