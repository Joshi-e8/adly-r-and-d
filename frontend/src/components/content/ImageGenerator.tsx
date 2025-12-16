import React, { useState } from 'react';
import { ContentAPI } from '../../services/content/contentApi';
import { ImageGenerationRequest } from '../../types/content';

interface ImageGeneratorProps {
  workspaceId: string;
  onImageGenerated?: (jobId: string) => void;
}

export const ImageGenerator: React.FC<ImageGeneratorProps> = ({ workspaceId, onImageGenerated }) => {
  const [contentApi] = useState(() => new ContentAPI(workspaceId));
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<ImageGenerationRequest>({
    prompt: '',
    style: 'realistic',
    dimensions: '1024x1024',
    variations_count: 1
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.prompt.trim()) {
      alert('Please provide an image prompt');
      return;
    }

    setLoading(true);
    try {
      const result = await contentApi.generateImage(formData);
      
      if (onImageGenerated) {
        onImageGenerated(result.job_id);
      }
      
      alert('Image generation started! Check the Content Library for results.');
      
      // Reset form
      setFormData({
        ...formData,
        prompt: ''
      });
      
    } catch (error) {
      console.error('Failed to generate image:', error);
      alert('Failed to start image generation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const styleExamples = {
    realistic: 'Photorealistic, natural lighting, high detail',
    artistic: 'Creative, painterly, artistic interpretation',
    minimalist: 'Clean, simple, minimal design',
    vintage: 'Retro, nostalgic, aged appearance',
    modern: 'Contemporary, sleek, cutting-edge'
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-2xl font-bold mb-6">Generate Images</h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">Image Prompt</label>
            <textarea
              value={formData.prompt}
              onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
              placeholder="Describe the image you want to generate..."
              rows={4}
              className="w-full p-2 border rounded-md"
              required
            />
            <p className="text-sm text-gray-500 mt-1">
              Be specific about what you want to see in the image
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Style</label>
            <select
              value={formData.style}
              onChange={(e) => setFormData({ ...formData, style: e.target.value as ImageGenerationRequest['style'] })}
              className="w-full p-2 border rounded-md"
            >
              {Object.keys(styleExamples).map((style) => (
                <option key={style} value={style}>
                  {style.charAt(0).toUpperCase() + style.slice(1)}
                </option>
              ))}
            </select>
            <p className="text-sm text-gray-500 mt-1">
              {styleExamples[formData.style || 'realistic']}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Dimensions</label>
            <select
              value={formData.dimensions}
              onChange={(e) => setFormData({ ...formData, dimensions: e.target.value as ImageGenerationRequest['dimensions'] })}
              className="w-full p-2 border rounded-md"
            >
              <option value="1024x1024">Square (1024x1024) - Social Media Posts</option>
              <option value="1024x1792">Portrait (1024x1792) - Stories, Mobile Ads</option>
              <option value="1792x1024">Landscape (1792x1024) - Banners, Desktop Ads</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Number of Variations</label>
            <select
              value={formData.variations_count}
              onChange={(e) => setFormData({ ...formData, variations_count: parseInt(e.target.value) })}
              className="w-full p-2 border rounded-md"
            >
              {[1, 2, 3, 4].map(num => (
                <option key={num} value={num}>{num}</option>
              ))}
            </select>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 mb-2">💡 Tips for Better Results</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Be specific about colors, lighting, and composition</li>
              <li>• Include cultural context for Arabic/Middle Eastern themes</li>
              <li>• Mention the product category and target audience</li>
              <li>• Use descriptive adjectives (elegant, modern, festive, etc.)</li>
            </ul>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Images'}
          </button>
        </form>

        <div className="mt-8">
          <h3 className="font-medium mb-3">Example Prompts</h3>
          <div className="space-y-2 text-sm">
            <div className="p-3 bg-gray-50 rounded">
              <strong>Fashion:</strong> "Elegant Arabic woman wearing modern hijab fashion, professional photography, studio lighting, minimalist background"
            </div>
            <div className="p-3 bg-gray-50 rounded">
              <strong>Food:</strong> "Traditional Middle Eastern dessert, Ramadan theme, golden colors, festive presentation, high-quality food photography"
            </div>
            <div className="p-3 bg-gray-50 rounded">
              <strong>Electronics:</strong> "Modern smartphone with Arabic interface, sleek design, tech environment, professional product photography"
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
