import api from '../api';
import {
  ContentAsset,
  ContentTemplate,
  GenerationJob,
  VideoProject,
  ProductAnalysis,
  VideoGenerationRequest,
  TextGenerationRequest,
  ImageGenerationRequest,
  Avatar,
  Voice
} from '../../types/content';

export class ContentAPI {
  private workspaceId: string;

  constructor(workspaceId: string) {
    this.workspaceId = workspaceId;
  }

  private getBaseUrl() {
    return `/api/v1/workspaces/${this.workspaceId}/content/v1`;
  }

  // Content Assets
  async getAssets(): Promise<ContentAsset[]> {
    const response = await api.get(`${this.getBaseUrl()}/assets/`);
    return response.data.results || response.data;
  }

  async getAsset(id: string): Promise<ContentAsset> {
    const response = await api.get(`${this.getBaseUrl()}/assets/${id}/`);
    return response.data;
  }

  async createAsset(data: Partial<ContentAsset>): Promise<ContentAsset> {
    const response = await api.post(`${this.getBaseUrl()}/assets/`, data);
    return response.data;
  }

  async updateAsset(id: string, data: Partial<ContentAsset>): Promise<ContentAsset> {
    const response = await api.patch(`${this.getBaseUrl()}/assets/${id}/`, data);
    return response.data;
  }

  async deleteAsset(id: string): Promise<void> {
    await api.delete(`${this.getBaseUrl()}/assets/${id}/`);
  }

  // Content Templates
  async getTemplates(): Promise<ContentTemplate[]> {
    const response = await api.get(`${this.getBaseUrl()}/templates/`);
    return response.data.results || response.data;
  }

  async getPublicTemplates(): Promise<ContentTemplate[]> {
    const response = await api.get(`${this.getBaseUrl()}/templates/public/`);
    return response.data;
  }

  async getTemplatesByIndustry(industry: string): Promise<ContentTemplate[]> {
    const response = await api.get(`${this.getBaseUrl()}/templates/by_industry/?industry=${industry}`);
    return response.data;
  }

  async getTemplatesByTheme(theme: string): Promise<ContentTemplate[]> {
    const response = await api.get(`${this.getBaseUrl()}/templates/by_theme/?theme=${theme}`);
    return response.data;
  }

  async getTemplate(id: string): Promise<ContentTemplate> {
    const response = await api.get(`${this.getBaseUrl()}/templates/${id}/`);
    return response.data;
  }

  async createTemplate(data: Partial<ContentTemplate>): Promise<ContentTemplate> {
    const response = await api.post(`${this.getBaseUrl()}/templates/`, data);
    return response.data;
  }

  // Generation Jobs
  async getJobs(): Promise<GenerationJob[]> {
    const response = await api.get(`${this.getBaseUrl()}/jobs/`);
    return response.data.results || response.data;
  }

  async getJob(id: string): Promise<GenerationJob> {
    const response = await api.get(`${this.getBaseUrl()}/jobs/${id}/`);
    return response.data;
  }

  // Video Projects
  async getVideoProjects(): Promise<VideoProject[]> {
    const response = await api.get(`${this.getBaseUrl()}/video-projects/`);
    return response.data.results || response.data;
  }

  async getVideoProject(id: string): Promise<VideoProject> {
    const response = await api.get(`${this.getBaseUrl()}/video-projects/${id}/`);
    return response.data;
  }

  async createVideoProject(data: Partial<VideoProject>): Promise<VideoProject> {
    const response = await api.post(`${this.getBaseUrl()}/video-projects/`, data);
    return response.data;
  }

  async updateVideoProject(id: string, data: Partial<VideoProject>): Promise<VideoProject> {
    const response = await api.patch(`${this.getBaseUrl()}/video-projects/${id}/`, data);
    return response.data;
  }

  async generateVideo(id: string): Promise<{ job_id: string; status: string; message: string }> {
    const response = await api.post(`${this.getBaseUrl()}/video-projects/${id}/generate/`);
    return response.data;
  }

  async regenerateVideo(id: string, variations_count: number = 1): Promise<{ job_ids: string[] }> {
    const response = await api.post(`${this.getBaseUrl()}/video-projects/${id}/regenerate/`, {
      variations_count
    });
    return response.data;
  }

  // Product Analysis
  async getProductAnalyses(): Promise<ProductAnalysis[]> {
    const response = await api.get(`${this.getBaseUrl()}/product-analysis/`);
    return response.data.results || response.data;
  }

  async analyzeProduct(product_url: string): Promise<ProductAnalysis> {
    const response = await api.post(`${this.getBaseUrl()}/generate/analyze_product/`, {
      product_url
    });
    return response.data;
  }

  // Generation APIs
  async generateVideoFromRequest(request: VideoGenerationRequest): Promise<{
    project_id: string;
    job_id: string;
    status: string;
    message: string;
  }> {
    const response = await api.post(`${this.getBaseUrl()}/generate/generate_video/`, request);
    return response.data;
  }

  async generateText(request: TextGenerationRequest): Promise<{
    job_id: string;
    status: string;
    message: string;
  }> {
    const response = await api.post(`${this.getBaseUrl()}/generate/generate_text/`, request);
    return response.data;
  }

  async generateImage(request: ImageGenerationRequest): Promise<{
    job_id: string;
    status: string;
    message: string;
  }> {
    const response = await api.post(`${this.getBaseUrl()}/generate/generate_image/`, request);
    return response.data;
  }

  // Mock data for avatars and voices (would come from providers in production)
  async getAvatars(language: 'ar' | 'en' = 'ar'): Promise<Avatar[]> {
    // Mock data - in production this would call the actual API
    const avatars: Record<string, Avatar[]> = {
      ar: [
        {
          id: 'arabic_female_1',
          name: 'سارة',
          gender: 'female',
          age_range: '25-35',
          style: 'professional',
          preview_image: '/avatars/sarah.jpg'
        },
        {
          id: 'arabic_male_1',
          name: 'أحمد',
          gender: 'male',
          age_range: '30-40',
          style: 'professional',
          preview_image: '/avatars/ahmed.jpg'
        }
      ],
      en: [
        {
          id: 'english_female_1',
          name: 'Emma',
          gender: 'female',
          age_range: '25-35',
          style: 'professional',
          preview_image: '/avatars/emma.jpg'
        },
        {
          id: 'english_male_1',
          name: 'James',
          gender: 'male',
          age_range: '30-40',
          style: 'professional',
          preview_image: '/avatars/james.jpg'
        }
      ]
    };

    return Promise.resolve(avatars[language] || avatars.ar);
  }

  async getVoices(language: 'ar' | 'en' = 'ar'): Promise<Voice[]> {
    // Mock data - in production this would call the actual API
    const voices: Record<string, Voice[]> = {
      ar: [
        {
          id: 'arabic_female_voice_1',
          name: 'صوت نسائي عربي 1',
          gender: 'female',
          accent: 'gulf',
          tone: 'professional',
          sample_url: '/voices/arabic_female_1.mp3'
        },
        {
          id: 'arabic_male_voice_1',
          name: 'صوت رجالي عربي 1',
          gender: 'male',
          accent: 'gulf',
          tone: 'professional',
          sample_url: '/voices/arabic_male_1.mp3'
        }
      ],
      en: [
        {
          id: 'english_female_voice_1',
          name: 'English Female Voice 1',
          gender: 'female',
          accent: 'american',
          tone: 'professional',
          sample_url: '/voices/english_female_1.mp3'
        },
        {
          id: 'english_male_voice_1',
          name: 'English Male Voice 1',
          gender: 'male',
          accent: 'british',
          tone: 'professional',
          sample_url: '/voices/english_male_1.mp3'
        }
      ]
    };

    return Promise.resolve(voices[language] || voices.ar);
  }
}