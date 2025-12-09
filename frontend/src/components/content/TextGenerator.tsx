import React, { useState } from 'react';
import { ContentAPI } from '../../services/content/contentApi';
import { TextGenerationRequest } from '../../types/content';

interface TextGeneratorProps {
  workspaceId: string;
  onTextGenerated?: (jobId: string) => void;
}

export const TextGenerator: React.FC<TextGeneratorProps> = ({ workspaceId, onTextGenerated }) => {
  const [contentApi] = useState(() => new ContentAPI(workspaceId));
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<TextGenerationRequest>({
    type: 'headline',
    product_context: '',
    tone: 'professional',
    language: 'ar',
    variations_count: 3
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.product_context?.trim()) {
      alert('Please provide product context');
      return;
    }

    setLoading(true);
    try {
      const result = await contentApi.generateText(formData);
      
      if (onTextGenerated) {
        onTextGenerated(result.job_id);
      }
      
      alert('Text generation started! Check the Content Library for results.');
      
      // Reset form
      setFormData({
        ...formData,
        product_context: ''
      });
      
    } catch (error) {
      console.error('Failed to generate text:', error);
      alert('Failed to start text generation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-2xl font-bold mb-6">Generate Text Content</h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">Content Type</label>
            <select
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
              className="w-full p-2 border rounded-md"
            >
              <option value="headline">Headlines</option>
              <option value="description">Product Descriptions</option>
              <option value="cta">Call-to-Action</option>
              <option value="script">Video Scripts</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Language</label>
            <select
              value={formData.language}
              onChange={(e) => setFormData({ ...formData, language: e.target.value as 'ar' | 'en' })}
              className="w-full p-2 border rounded-md"
            >
              <option value="ar">العربية</option>
              <option value="en">English</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Tone</label>
            <select
              value={formData.tone}
              onChange={(e) => setFormData({ ...formData, tone: e.target.value as any })}
              className="w-full p-2 border rounded-md"
            >
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="festive">Festive</option>
              <option value="promotional">Promotional</option>
              <option value="cultural">Cultural</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Product Context</label>
            <textarea
              value={formData.product_context}
              onChange={(e) => setFormData({ ...formData, product_context: e.target.value })}
              placeholder={formData.language === 'ar' ? 'اكتب وصف المنتج أو الخدمة...' : 'Describe your product or service...'}
              rows={4}
              className="w-full p-2 border rounded-md"
              required
            />
            <p className="text-sm text-gray-500 mt-1">
              Provide details about your product, target audience, and key benefits
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Number of Variations</label>
            <select
              value={formData.variations_count}
              onChange={(e) => setFormData({ ...formData, variations_count: parseInt(e.target.value) })}
              className="w-full p-2 border rounded-md"
            >
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
                <option key={num} value={num}>{num}</option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Text'}
          </button>
        </form>
      </div>
    </div>
  );
};