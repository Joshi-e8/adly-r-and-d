from django.core.management.base import BaseCommand
from apps.content_creation.models import ContentTemplate


class Command(BaseCommand):
    help = 'Create default content templates'

    def handle(self, *args, **options):
        templates = [
            {
                'name': 'Modern Product Showcase',
                'type': 'video',
                'industry': 'general',
                'theme': 'general',
                'template_data': {
                    'duration': 30,
                    'scenes': [
                        {
                            'type': 'intro',
                            'duration': 5,
                            'elements': ['logo', 'product_image', 'headline']
                        },
                        {
                            'type': 'features',
                            'duration': 15,
                            'elements': ['product_showcase', 'feature_list', 'benefits']
                        },
                        {
                            'type': 'cta',
                            'duration': 10,
                            'elements': ['call_to_action', 'contact_info', 'logo']
                        }
                    ],
                    'style': {
                        'background': 'gradient',
                        'colors': ['#1a1a1a', '#ffffff'],
                        'font': 'modern',
                        'animation': 'smooth'
                    }
                },
                'is_public': True
            },
            {
                'name': 'Ramadan Special Template',
                'type': 'video',
                'industry': 'general',
                'theme': 'ramadan',
                'template_data': {
                    'duration': 30,
                    'scenes': [
                        {
                            'type': 'greeting',
                            'duration': 8,
                            'elements': ['ramadan_greeting', 'crescent_moon', 'islamic_pattern']
                        },
                        {
                            'type': 'product',
                            'duration': 15,
                            'elements': ['product_showcase', 'ramadan_offer', 'special_price']
                        },
                        {
                            'type': 'blessing',
                            'duration': 7,
                            'elements': ['ramadan_wishes', 'cta_button', 'contact']
                        }
                    ],
                    'style': {
                        'background': 'ramadan_night',
                        'colors': ['#2c5530', '#d4af37', '#ffffff'],
                        'font': 'arabic_elegant',
                        'animation': 'gentle',
                        'cultural_elements': ['crescent', 'stars', 'islamic_patterns']
                    }
                },
                'is_public': True
            },
            {
                'name': 'Eid Celebration Template',
                'type': 'video',
                'industry': 'general',
                'theme': 'eid',
                'template_data': {
                    'duration': 25,
                    'scenes': [
                        {
                            'type': 'eid_greeting',
                            'duration': 6,
                            'elements': ['eid_mubarak', 'festive_decoration', 'joyful_colors']
                        },
                        {
                            'type': 'celebration',
                            'duration': 12,
                            'elements': ['product_display', 'eid_offer', 'family_joy']
                        },
                        {
                            'type': 'wishes',
                            'duration': 7,
                            'elements': ['eid_wishes', 'purchase_cta', 'brand_logo']
                        }
                    ],
                    'style': {
                        'background': 'eid_celebration',
                        'colors': ['#4a90e2', '#f5a623', '#ffffff'],
                        'font': 'festive_arabic',
                        'animation': 'joyful',
                        'cultural_elements': ['lanterns', 'crescents', 'geometric_patterns']
                    }
                },
                'is_public': True
            },
            {
                'name': 'Saudi National Day Template',
                'type': 'video',
                'industry': 'general',
                'theme': 'national_day',
                'template_data': {
                    'duration': 35,
                    'scenes': [
                        {
                            'type': 'patriotic_intro',
                            'duration': 8,
                            'elements': ['saudi_flag', 'national_anthem', 'pride_message']
                        },
                        {
                            'type': 'product_pride',
                            'duration': 20,
                            'elements': ['made_in_saudi', 'product_quality', 'national_values']
                        },
                        {
                            'type': 'celebration_cta',
                            'duration': 7,
                            'elements': ['celebrate_together', 'special_offer', 'contact_info']
                        }
                    ],
                    'style': {
                        'background': 'saudi_landscape',
                        'colors': ['#006c35', '#ffffff'],
                        'font': 'bold_arabic',
                        'animation': 'proud',
                        'cultural_elements': ['palm_trees', 'desert', 'traditional_patterns']
                    }
                },
                'is_public': True
            },
            {
                'name': 'Fashion Product Template',
                'type': 'video',
                'industry': 'fashion',
                'theme': 'general',
                'template_data': {
                    'duration': 25,
                    'scenes': [
                        {
                            'type': 'style_intro',
                            'duration': 5,
                            'elements': ['fashion_logo', 'trendy_text', 'style_preview']
                        },
                        {
                            'type': 'product_showcase',
                            'duration': 15,
                            'elements': ['model_wearing', 'fabric_details', 'style_variations']
                        },
                        {
                            'type': 'fashion_cta',
                            'duration': 5,
                            'elements': ['shop_now', 'fashion_forward', 'brand_signature']
                        }
                    ],
                    'style': {
                        'background': 'fashion_studio',
                        'colors': ['#000000', '#ffffff', '#c9a96e'],
                        'font': 'elegant',
                        'animation': 'stylish',
                        'elements': ['runway_lights', 'fabric_textures']
                    }
                },
                'is_public': True
            },
            {
                'name': 'Electronics Product Template',
                'type': 'video',
                'industry': 'electronics',
                'theme': 'general',
                'template_data': {
                    'duration': 30,
                    'scenes': [
                        {
                            'type': 'tech_intro',
                            'duration': 6,
                            'elements': ['tech_logo', 'innovation_text', 'product_preview']
                        },
                        {
                            'type': 'features_demo',
                            'duration': 18,
                            'elements': ['product_360', 'feature_highlights', 'tech_specs']
                        },
                        {
                            'type': 'tech_cta',
                            'duration': 6,
                            'elements': ['upgrade_now', 'tech_support', 'warranty_info']
                        }
                    ],
                    'style': {
                        'background': 'tech_environment',
                        'colors': ['#1e3a8a', '#ffffff', '#06b6d4'],
                        'font': 'modern_tech',
                        'animation': 'dynamic',
                        'elements': ['circuit_patterns', 'digital_effects']
                    }
                },
                'is_public': True
            }
        ]

        created_count = 0
        for template_data in templates:
            template, created = ContentTemplate.objects.get_or_create(
                name=template_data['name'],
                type=template_data['type'],
                defaults=template_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Template already exists: {template.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new templates')
        )