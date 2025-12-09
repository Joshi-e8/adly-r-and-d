import requests
from typing import Dict, List, Any
from decouple import config

class HuggingFaceProvider:
    """Hugging Face provider for text generation (OpenAI Compatible)"""
    
    def __init__(self):
        self.api_key = config('HUGGINGFACE_API_KEY', default='')
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        self.model = "HuggingFaceH4/zephyr-7b-beta"
    
    def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text content using Hugging Face Chat API"""
        
        language = kwargs.get('language', 'ar')
        tone = kwargs.get('tone', 'professional')
        variations_count = kwargs.get('variations_count', 3)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Construct chat messages
        system_prompt = f"You are a professional marketing copywriter. Tone: {tone}. Language: {language}."
        user_prompt = f"{prompt}\nPlease generate {variations_count} distinct variations. Return them as a numbered list."
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 512,
            "temperature": 0.7,
            "stream": False
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # OpenAI compatible response structure
            generated_text = result['choices'][0]['message']['content']
            
            # Split by newlines and look for numbered items
            lines = generated_text.split('\n')
            variations = [line.strip() for line in lines if line.strip() and (line[0].isdigit() or line.startswith('-'))]
            
            # Fallback if parsing fails
            if not variations:
                variations = [generated_text]
                
            return {
                'success': True,
                'content': variations[:variations_count],
                'metadata': {
                    'language': language,
                    'tone': tone,
                    'provider': 'huggingface',
                    'model': self.model
                }
            }
            
        except Exception as e:
            error_details = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_details += f" | Response: {e.response.text}"
            
            print(f"Hugging Face API Error: {error_details}")
            return {
                'success': False,
                'error': error_details,
                'content': []
            } 
