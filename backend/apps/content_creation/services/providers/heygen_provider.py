import os
from typing import Dict, List, Any
from decouple import config


class HeyGenProvider:
    """HeyGen provider for AI avatar video generation"""
    
    def __init__(self):
        self.api_key = config('HEYGEN_API_KEY', default='')
        self.base_url = 'https://api.heygen.com/v1'
    
    def generate_video(self, script: str, avatar_settings: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate video with AI avatar"""
        
        language = kwargs.get('language', 'ar')
        brand_settings = kwargs.get('brand_settings', {})
        
        # Mock video generation response
        # In production, this would make actual API calls to HeyGen
        
        video_data = {
            'success': True,
            'video_id': f'heygen_video_{hash(script)}',
            'status': 'processing',
            'estimated_completion': '2-5 minutes',
            'preview_url': 'https://example.com/preview.mp4',
            'metadata': {
                'duration': self._estimate_duration(script),
                'language': language,
                'avatar': avatar_settings.get('avatar_id', 'default_arabic_female'),
                'voice': avatar_settings.get('voice_id', 'arabic_female_1'),
                'resolution': '1080p',
                'format': 'mp4'
            }
        }
        
        return video_data
    
    def get_available_avatars(self, language: str = 'ar') -> List[Dict[str, Any]]:
        """Get available avatars for the specified language"""
        
        # Mock avatar data
        avatars = {
            'ar': [
                {
                    'id': 'arabic_female_1',
                    'name': 'سارة',
                    'gender': 'female',
                    'age_range': '25-35',
                    'style': 'professional',
                    'preview_image': 'https://example.com/avatar1.jpg'
                },
                {
                    'id': 'arabic_male_1',
                    'name': 'أحمد',
                    'gender': 'male',
                    'age_range': '30-40',
                    'style': 'professional',
                    'preview_image': 'https://example.com/avatar2.jpg'
                },
                {
                    'id': 'arabic_female_2',
                    'name': 'فاطمة',
                    'gender': 'female',
                    'age_range': '20-30',
                    'style': 'casual',
                    'preview_image': 'https://example.com/avatar3.jpg'
                }
            ],
            'en': [
                {
                    'id': 'english_female_1',
                    'name': 'Emma',
                    'gender': 'female',
                    'age_range': '25-35',
                    'style': 'professional',
                    'preview_image': 'https://example.com/avatar4.jpg'
                },
                {
                    'id': 'english_male_1',
                    'name': 'James',
                    'gender': 'male',
                    'age_range': '30-40',
                    'style': 'professional',
                    'preview_image': 'https://example.com/avatar5.jpg'
                }
            ]
        }
        
        return avatars.get(language, avatars['en'])
    
    def get_available_voices(self, language: str = 'ar') -> List[Dict[str, Any]]:
        """Get available voices for the specified language"""
        
        voices = {
            'ar': [
                {
                    'id': 'arabic_female_voice_1',
                    'name': 'صوت نسائي عربي 1',
                    'gender': 'female',
                    'accent': 'gulf',
                    'tone': 'professional',
                    'sample_url': 'https://example.com/voice1.mp3'
                },
                {
                    'id': 'arabic_male_voice_1',
                    'name': 'صوت رجالي عربي 1',
                    'gender': 'male',
                    'accent': 'gulf',
                    'tone': 'professional',
                    'sample_url': 'https://example.com/voice2.mp3'
                },
                {
                    'id': 'arabic_female_voice_2',
                    'name': 'صوت نسائي عربي 2',
                    'gender': 'female',
                    'accent': 'levantine',
                    'tone': 'friendly',
                    'sample_url': 'https://example.com/voice3.mp3'
                }
            ],
            'en': [
                {
                    'id': 'english_female_voice_1',
                    'name': 'English Female Voice 1',
                    'gender': 'female',
                    'accent': 'american',
                    'tone': 'professional',
                    'sample_url': 'https://example.com/voice4.mp3'
                },
                {
                    'id': 'english_male_voice_1',
                    'name': 'English Male Voice 1',
                    'gender': 'male',
                    'accent': 'british',
                    'tone': 'professional',
                    'sample_url': 'https://example.com/voice5.mp3'
                }
            ]
        }
        
        return voices.get(language, voices['en'])
    
    def get_video_templates(self) -> List[Dict[str, Any]]:
        """Get available video templates"""
        
        templates = [
            {
                'id': 'product_showcase_1',
                'name': 'Product Showcase - Modern',
                'description': 'Clean modern template for product presentations',
                'preview_image': 'https://example.com/template1.jpg',
                'duration_range': '15-60 seconds',
                'suitable_for': ['electronics', 'fashion', 'beauty']
            },
            {
                'id': 'ramadan_special',
                'name': 'Ramadan Special',
                'description': 'Festive template for Ramadan campaigns',
                'preview_image': 'https://example.com/template2.jpg',
                'duration_range': '20-45 seconds',
                'suitable_for': ['food', 'fashion', 'general']
            },
            {
                'id': 'eid_celebration',
                'name': 'Eid Celebration',
                'description': 'Joyful template for Eid promotions',
                'preview_image': 'https://example.com/template3.jpg',
                'duration_range': '15-30 seconds',
                'suitable_for': ['fashion', 'beauty', 'gifts']
            },
            {
                'id': 'national_day_ksa',
                'name': 'Saudi National Day',
                'description': 'Patriotic template for National Day campaigns',
                'preview_image': 'https://example.com/template4.jpg',
                'duration_range': '20-40 seconds',
                'suitable_for': ['general', 'automotive', 'real_estate']
            }
        ]
        
        return templates
    
    def check_video_status(self, video_id: str) -> Dict[str, Any]:
        """Check the status of video generation"""
        
        # Mock status check
        return {
            'video_id': video_id,
            'status': 'completed',  # or 'processing', 'failed'
            'progress': 100,
            'download_url': f'https://example.com/videos/{video_id}.mp4',
            'thumbnail_url': f'https://example.com/thumbnails/{video_id}.jpg',
            'duration': 30,
            'file_size': 15728640,  # bytes
            'created_at': '2024-01-15T10:30:00Z'
        }
    
    def _estimate_duration(self, script: str) -> int:
        """Estimate video duration based on script length"""
        # Rough estimation: 150 words per minute for Arabic, 180 for English
        word_count = len(script.split())
        
        # Assume Arabic if contains Arabic characters
        if any('\u0600' <= char <= '\u06FF' for char in script):
            words_per_minute = 150
        else:
            words_per_minute = 180
        
        duration_minutes = word_count / words_per_minute
        duration_seconds = max(15, int(duration_minutes * 60))  # Minimum 15 seconds
        
        return duration_seconds
    
    def customize_brand_elements(self, brand_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Apply brand customization to video"""
        
        customizations = {
            'logo_position': brand_settings.get('logo_position', 'bottom_right'),
            'brand_colors': brand_settings.get('colors', ['#000000', '#FFFFFF']),
            'font_family': brand_settings.get('font', 'Arial'),
            'background_style': brand_settings.get('background', 'gradient'),
            'overlay_opacity': brand_settings.get('overlay_opacity', 0.8)
        }
        
        return customizations