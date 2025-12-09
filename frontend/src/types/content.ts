export interface ContentAsset {
  id: string;
  workspace: string;
  type: 'image' | 'video' | 'audio' | 'text';
  name: string;
  file_url?: string;
  file_size?: number;
  mime_type?: string;
  metadata: Record<string, any>;
  generated_by?: string;
  generation_prompt?: string;
  language: 'ar' | 'en';
  created_at: string;
  updated_at: string;
}

export interface ContentTemplate {
  id: string;
  workspace?: string;
  name: string;
  type: 'video' | 'image' | 'text';
  industry: string;
  theme: string;
  template_data: Record<string, any>;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface GenerationJob {
  id: string;
  workspace: string;
  user?: string;
  type: 'text' | 'image' | 'video' | 'voice' | 'script';
  provider: string;
  prompt: string;
  parameters: Record<string, any>;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result_asset?: ContentAsset;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export interface VideoProject {
  id: string;
  workspace: string;
  user?: string;
  name: string;
  product_url?: string;
  script?: string;
  template?: ContentTemplate;
  avatar_settings: Record<string, any>;
  brand_settings: Record<string, any>;
  language: 'ar' | 'en';
  status: 'draft' | 'generating' | 'completed' | 'failed';
  generated_video?: ContentAsset;
  variations: ContentAsset[];
  created_at: string;
  updated_at: string;
}

export interface ProductAnalysis {
  id: string;
  workspace: string;
  product_url: string;
  title?: string;
  description?: string;
  price?: number;
  currency: string;
  images: string[];
  features: string[];
  category?: string;
  brand?: string;
  analysis_data: Record<string, any>;
  created_at: string;
}

export interface VideoGenerationRequest {
  product_url?: string;
  script?: string;
  template_id?: string;
  avatar_settings?: Record<string, any>;
  brand_settings?: Record<string, any>;
  language?: 'ar' | 'en';
  variations_count?: number;
}

export interface TextGenerationRequest {
  type: 'headline' | 'description' | 'cta' | 'script';
  product_context?: string;
  tone?: 'professional' | 'casual' | 'festive' | 'promotional' | 'cultural';
  language?: 'ar' | 'en';
  variations_count?: number;
}

export interface ImageGenerationRequest {
  prompt: string;
  style?: 'realistic' | 'artistic' | 'minimalist' | 'vintage' | 'modern';
  dimensions?: '1024x1024' | '1024x1792' | '1792x1024';
  variations_count?: number;
}

export interface Avatar {
  id: string;
  name: string;
  gender: 'male' | 'female';
  age_range: string;
  style: string;
  preview_image: string;
}

export interface Voice {
  id: string;
  name: string;
  gender: 'male' | 'female';
  accent: string;
  tone: string;
  sample_url: string;
}