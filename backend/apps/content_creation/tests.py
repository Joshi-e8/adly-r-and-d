from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.workspaces.models import Workspace
from apps.content_creation.models import (
    ContentAsset, ContentTemplate, GenerationJob, 
    VideoProject, ProductAnalysis
)

User = get_user_model()


class ContentCreationModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.workspace = Workspace.objects.create(
            name='Test Workspace',
            slug='test-workspace',
            owner=self.user
        )

    def test_content_asset_creation(self):
        asset = ContentAsset.objects.create(
            workspace=self.workspace,
            type='video',
            name='Test Video',
            language='ar'
        )
        self.assertEqual(asset.name, 'Test Video')
        self.assertEqual(asset.type, 'video')
        self.assertEqual(asset.language, 'ar')

    def test_content_template_creation(self):
        template = ContentTemplate.objects.create(
            workspace=self.workspace,
            name='Test Template',
            type='video',
            industry='fashion',
            theme='ramadan',
            template_data={'duration': 30}
        )
        self.assertEqual(template.name, 'Test Template')
        self.assertEqual(template.industry, 'fashion')
        self.assertEqual(template.theme, 'ramadan')

    def test_generation_job_creation(self):
        job = GenerationJob.objects.create(
            workspace=self.workspace,
            user=self.user,
            type='video',
            provider='heygen',
            prompt='Generate a video for fashion product'
        )
        self.assertEqual(job.type, 'video')
        self.assertEqual(job.provider, 'heygen')
        self.assertEqual(job.status, 'pending')

    def test_video_project_creation(self):
        project = VideoProject.objects.create(
            workspace=self.workspace,
            user=self.user,
            name='Test Video Project',
            product_url='https://example.com/product',
            language='ar'
        )
        self.assertEqual(project.name, 'Test Video Project')
        self.assertEqual(project.language, 'ar')
        self.assertEqual(project.status, 'draft')

    def test_product_analysis_creation(self):
        analysis = ProductAnalysis.objects.create(
            workspace=self.workspace,
            product_url='https://example.com/product',
            title='Test Product',
            price=99.99,
            currency='SAR'
        )
        self.assertEqual(analysis.title, 'Test Product')
        self.assertEqual(analysis.price, 99.99)
        self.assertEqual(analysis.currency, 'SAR')