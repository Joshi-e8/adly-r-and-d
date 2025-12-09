import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adly_backend.settings')
django.setup()

from apps.authentication.models import User
from apps.workspaces.models import Workspace
from apps.content_creation.services.generation_service import GenerationService

def test_huggingface_generation():
    print("🚀 Starting Hugging Face Integration Test...")
    
    # Get a user (assuming one exists from previous steps)
    user = User.objects.first()
    if not user:
        print("❌ No user found to run test with.")
        return

    # Get or create a workspace for the user
    workspace = Workspace.objects.filter(owner=user).first()
    if not workspace:
        print("⚠️ No workspace found, creating one...")
        workspace = Workspace.objects.create(name="Test Workspace", owner=user)
    
    service = GenerationService()
    
    # Debug Key
    key = service.huggingface_provider.api_key
    print(f"🔑 Loaded Key: {key[:4] if key else 'None'}...{key[-4:] if key else ''}")
    
    print(f"👤 User: {user.email}")
    print(f"wb Workspace: {workspace.id}")
    print("🔄 Calling generate_text with provider='huggingface'...")
    
    try:
        # Create a job synchronously (as per recent changes)
        job = service.generate_text(
            workspace_id=str(workspace.id),
            user=user,
            type='headline',
            provider='huggingface',
            product_context="A smart coffee maker that schedules your brew via app",
            variations_count=2,
            tone='witty'
        )
        
        print("\n✅ Job Created & Processed!")
        print(f"🆔 Job ID: {job.id}")
        print(f"📊 Status: {job.status}")
        
        if job.status == 'completed':
            print("\n🎉 SUCCESS! Generated Content:")
            print("-" * 40)
            if job.result_asset:
                # The content is stored in metadata/content
                content = job.result_asset.metadata.get('content', [])
                for idx, text in enumerate(content, 1):
                    print(f"{idx}. {text}")
            else:
                 print("⚠️ Job completed but no result asset found.")
            print("-" * 40)
        else:
            print(f"\n❌ FAILED. Error Message: {job.error_message}")
            
    except Exception as e:
        print(f"\n❌ Exception during test: {str(e)}")

if __name__ == "__main__":
    test_huggingface_generation()
