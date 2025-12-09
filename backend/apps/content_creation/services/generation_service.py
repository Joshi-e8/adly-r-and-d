import uuid
from typing import List, Dict, Any
from django.utils import timezone
from apps.content_creation.models import GenerationJob, ContentAsset, VideoProject
from apps.content_creation.services.providers.openai_provider import OpenAIProvider
from apps.content_creation.services.providers.heygen_provider import HeyGenProvider
from apps.content_creation.services.providers.stability_provider import StabilityProvider
from apps.content_creation.services.providers.huggingface_provider import HuggingFaceProvider


class GenerationService:
    """Service for managing AI content generation"""
    
    def __init__(self):
        self.text_provider = OpenAIProvider()
        self.video_provider = HeyGenProvider()
        self.image_provider = StabilityProvider()
        self.huggingface_provider = HuggingFaceProvider()
    
    def generate_video_from_project(self, project: VideoProject) -> GenerationJob:
        """Generate video from a video project"""
        
        # Create generation job
        job = GenerationJob.objects.create(
            workspace=project.workspace,
            user=project.user,
            type='video',
            provider='heygen',
            prompt=self._build_video_prompt(project),
            parameters={
                'product_url': project.product_url,
                'script': project.script,
                'avatar_settings': project.avatar_settings,
                'brand_settings': project.brand_settings,
                'language': project.language
            }
        )
        
        # Update project status
        project.status = 'generating'
        project.save()
        
        # Queue the generation task (would be handled by Celery in production)
        self._queue_video_generation(job)
        
        return job
    
    def generate_video_variations(self, project: VideoProject, count: int = 1) -> List[GenerationJob]:
        """Generate multiple video variations"""
        jobs = []
        
        for i in range(count):
            job = GenerationJob.objects.create(
                workspace=project.workspace,
                user=project.user,
                type='video',
                provider='heygen',
                prompt=self._build_video_prompt(project, variation=i+1),
                parameters={
                    'product_url': project.product_url,
                    'script': project.script,
                    'avatar_settings': project.avatar_settings,
                    'brand_settings': project.brand_settings,
                    'language': project.language,
                    'variation': i + 1
                }
            )
            jobs.append(job)
            self._queue_video_generation(job)
        
        return jobs
    
    def generate_text(self, workspace_id: str, user, type: str, **kwargs) -> GenerationJob:
        """Generate text content"""
        
        prompt = self._build_text_prompt(type, **kwargs)
        
        job = GenerationJob.objects.create(
            workspace_id=workspace_id,
            user=user,
            type='text',
            provider=kwargs.get('provider', 'openai'),
            prompt=prompt,
            parameters={
                'text_type': type,
                'tone': kwargs.get('tone', 'professional'),
                'language': kwargs.get('language', 'ar'),
                'variations_count': kwargs.get('variations_count', 3),
                'product_context': kwargs.get('product_context', '')
            }
        )
        
        self._queue_text_generation(job)
        return job
    
    def generate_image(self, workspace_id: str, user, **kwargs) -> GenerationJob:
        """Generate image content"""
        
        job = GenerationJob.objects.create(
            workspace_id=workspace_id,
            user=user,
            type='image',
            provider='stability',
            prompt=kwargs.get('prompt', ''),
            parameters={
                'style': kwargs.get('style', 'realistic'),
                'dimensions': kwargs.get('dimensions', '1024x1024'),
                'variations_count': kwargs.get('variations_count', 1)
            }
        )
        
        self._queue_image_generation(job)
        return job
    
    def _build_video_prompt(self, project: VideoProject, variation: int = 0) -> str:
        """Build prompt for video generation"""
        base_prompt = f"""
        Create a video advertisement with the following specifications:
        
        Language: {project.language}
        Product URL: {project.product_url or 'N/A'}
        Script: {project.script or 'Generate from product'}
        
        Avatar Settings: {project.avatar_settings}
        Brand Settings: {project.brand_settings}
        """
        
        if variation > 0:
            base_prompt += f"\nVariation: {variation} (create different tone/style)"
        
        return base_prompt.strip()
    
    def _build_text_prompt(self, text_type: str, **kwargs) -> str:
        """Build prompt for text generation"""
        language = kwargs.get('language', 'ar')
        tone = kwargs.get('tone', 'professional')
        product_context = kwargs.get('product_context', '')
        variations_count = kwargs.get('variations_count', 3)
        
        language_name = 'Arabic' if language == 'ar' else 'English'
        
        prompts = {
            'headline': f"Generate {variations_count} compelling {tone} headlines in {language_name} for: {product_context}",
            'description': f"Generate {variations_count} {tone} product descriptions in {language_name} for: {product_context}",
            'cta': f"Generate {variations_count} {tone} call-to-action phrases in {language_name} for: {product_context}",
            'script': f"Generate {variations_count} {tone} video scripts in {language_name} for: {product_context}"
        }
        
        return prompts.get(text_type, f"Generate {text_type} content in {language_name}")
    
    def _queue_video_generation(self, job: GenerationJob):
        """Queue video generation task (placeholder for Celery task)"""
        # In production, this would dispatch to Celery
        # For now, we'll mark it as processing
        job.status = 'processing'
        job.save()
        
        # Simulate async processing
        print(f"Queued video generation job: {job.id}")
    
    def _queue_text_generation(self, job: GenerationJob):
        """Queue text generation task (placeholder for Celery task)"""
        job.status = 'processing'
        job.save()
        print(f"Queued text generation job: {job.id}")
        
        # Synchronous execution for R&D
        try:
            result = None
            if job.provider == 'huggingface':
                result = self.huggingface_provider.generate_text(
                    job.prompt,
                    **job.parameters
                )
            elif job.provider == 'openai':
                result = self.text_provider.generate_text(
                    job.prompt,
                    **job.parameters
                )
            
            if result:
                if result.get('success'):
                    # Save results as a text file asset (simulated)
                    import json
                    
                    # Convert content list to a single string for storage
                    content_text = "\n\n".join(result.get('content', []))
                    
                    # Store as metadata in the asset
                    asset_data = {
                        'file_url': '',  # No actual file upload in thi synch mode
                        'file_size': len(content_text),
                        'mime_type': 'text/plain',
                        'metadata': {
                            'content': result.get('content'),
                            'provider_metadata': result.get('metadata')
                        }
                    }
                    
                    self.complete_generation_job(job, asset_data)
                else:
                    job.status = 'failed'
                    job.error_message = result.get('error', 'Unknown provider error')
                    job.save()
                    
        except Exception as e:
            print(f"Sync generation failed: {e}")
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
    
    def _queue_image_generation(self, job: GenerationJob):
        """Queue image generation task (placeholder for Celery task)"""
        job.status = 'processing'
        job.save()
        print(f"Queued image generation job: {job.id}")
    
    def complete_generation_job(self, job: GenerationJob, result_data: Dict[str, Any]):
        """Complete a generation job with results"""
        try:
            # Create content asset
            asset = ContentAsset.objects.create(
                workspace=job.workspace,
                type=self._get_asset_type_from_job(job.type),
                name=f"Generated {job.type} - {timezone.now().strftime('%Y%m%d_%H%M%S')}",
                file_url=result_data.get('file_url'),
                file_size=result_data.get('file_size'),
                mime_type=result_data.get('mime_type'),
                metadata=result_data.get('metadata', {}),
                generated_by=job.provider,
                generation_prompt=job.prompt,
                language=job.parameters.get('language', 'ar')
            )
            
            # Update job
            job.result_asset = asset
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.save()
            
            # Update related video project if applicable
            if job.type == 'video':
                video_projects = VideoProject.objects.filter(
                    workspace=job.workspace,
                    status='generating'
                )
                for project in video_projects:
                    if not project.generated_video:
                        project.generated_video = asset
                        project.status = 'completed'
                        project.save()
                        break
                    else:
                        project.variations.add(asset)
            
            return asset
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = timezone.now()
            job.save()
            raise
    
    def _get_asset_type_from_job(self, job_type: str) -> str:
        """Map job type to asset type"""
        mapping = {
            'video': 'video',
            'image': 'image',
            'text': 'text',
            'voice': 'audio',
            'script': 'text'
        }
        return mapping.get(job_type, 'text')