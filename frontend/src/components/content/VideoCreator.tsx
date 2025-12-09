import React, { useState, useEffect } from 'react';
import { ContentAPI } from '../../services/content/contentApi';
import { ContentTemplate, Avatar, Voice, VideoGenerationRequest } from '../../types/content';

interface VideoCreatorProps {
  workspaceId: string;
  onVideoGenerated?: (projectId: string, jobId: string) => void;
}

export const VideoCreator: React.FC<VideoCreatorProps> = ({ workspaceId, onVideoGenerated }) => {
  const [contentApi] = useState(() => new ContentAPI(workspaceId));
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  
  // Form data
  const [productUrl, setProductUrl] = useState('');
  const [script, setScript] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<ContentTemplate | null>(null);
  const [selectedAvatar, setSelectedAvatar] = useState<Avatar | null>(null);
  const [selectedVoice, setSelectedVoice] = useState<Voice | null>(null);
  const [language, setLanguage] = useState<'ar' | 'en'>('ar');
  const [brandSettings, setBrandSettings] = useState({
    colors: ['#000000', '#ffffff'],
    logo_position: 'bottom_right',
    font: 'Arial'
  });
  
  // Data
  const [templates, setTemplates] = useState<ContentTemplate[]>([]);
  const [avatars, setAvatars] = useState<Avatar[]>([]);
  const [voices, setVoices] = useState<Voice[]>([]);

  useEffect(() => {
    loadTemplates();
    loadAvatars();
    loadVoices();
  }, [language]);

  const loadTemplates = async () => {
    try {
      const data = await contentApi.getPublicTemplates();
      setTemplates(data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const loadAvatars = async () => {
    try {
      const data = await contentApi.getAvatars(language);
      setAvatars(data);
    } catch (error) {
      console.error('Failed to load avatars:', error);
    }
  };

  const loadVoices = async () => {
    try {
      const data = await contentApi.getVoices(language);
      setVoices(data);
    } catch (error) {
      console.error('Failed to load voices:', error);
    }
  };

  const handleGenerate = async () => {
    if (!productUrl && !script) {
      alert('Please provide either a product URL or script');
      return;
    }

    setLoading(true);
    try {
      const request: VideoGenerationRequest = {
        product_url: productUrl || undefined,
        script: script || undefined,
        template_id: selectedTemplate?.id,
        avatar_settings: {
          avatar_id: selectedAvatar?.id,
          voice_id: selectedVoice?.id
        },
        brand_settings: brandSettings,
        language: language,
        variations_count: 1
      };

      const result = await contentApi.generateVideoFromRequest(request);
      
      if (onVideoGenerated) {
        onVideoGenerated(result.project_id, result.job_id);
      }
      
      alert('Video generation started! You will be notified when it\'s ready.');
      
    } catch (error) {
      console.error('Failed to generate video:', error);
      alert('Failed to start video generation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Content Source</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Language</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value as 'ar' | 'en')}
            className="w-full p-2 border rounded-md"
          >
            <option value="ar">العربية</option>
            <option value="en">English</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Product URL (Optional)</label>
          <input
            type="url"
            value={productUrl}
            onChange={(e) => setProductUrl(e.target.value)}
            placeholder="https://example.com/product"
            className="w-full p-2 border rounded-md"
          />
          <p className="text-sm text-gray-500 mt-1">
            We'll analyze the product and generate a script automatically
          </p>
        </div>

        <div className="text-center text-gray-500">OR</div>

        <div>
          <label className="block text-sm font-medium mb-2">Custom Script</label>
          <textarea
            value={script}
            onChange={(e) => setScript(e.target.value)}
            placeholder={language === 'ar' ? 'اكتب النص الخاص بك هنا...' : 'Write your custom script here...'}
            rows={6}
            className="w-full p-2 border rounded-md"
          />
        </div>
      </div>

      <button
        onClick={() => setStep(2)}
        disabled={!productUrl && !script}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        Next: Choose Template
      </button>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Choose Template</h3>
        <button
          onClick={() => setStep(1)}
          className="text-blue-600 hover:text-blue-700"
        >
          Back
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map((template) => (
          <div
            key={template.id}
            onClick={() => setSelectedTemplate(template)}
            className={`p-4 border rounded-lg cursor-pointer transition-colors ${
              selectedTemplate?.id === template.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <h4 className="font-medium">{template.name}</h4>
            <p className="text-sm text-gray-500 mt-1">
              {template.industry} • {template.theme}
            </p>
            <div className="mt-2 text-xs text-gray-400">
              Duration: {template.template_data.duration}s
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={() => setStep(3)}
        disabled={!selectedTemplate}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        Next: Choose Avatar
      </button>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Choose Avatar & Voice</h3>
        <button
          onClick={() => setStep(2)}
          className="text-blue-600 hover:text-blue-700"
        >
          Back
        </button>
      </div>

      <div>
        <h4 className="font-medium mb-3">Avatar</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {avatars.map((avatar) => (
            <div
              key={avatar.id}
              onClick={() => setSelectedAvatar(avatar)}
              className={`p-3 border rounded-lg cursor-pointer text-center transition-colors ${
                selectedAvatar?.id === avatar.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="w-16 h-16 bg-gray-200 rounded-full mx-auto mb-2"></div>
              <div className="text-sm font-medium">{avatar.name}</div>
              <div className="text-xs text-gray-500">{avatar.style}</div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h4 className="font-medium mb-3">Voice</h4>
        <div className="space-y-2">
          {voices.map((voice) => (
            <div
              key={voice.id}
              onClick={() => setSelectedVoice(voice)}
              className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                selectedVoice?.id === voice.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">{voice.name}</div>
                  <div className="text-sm text-gray-500">{voice.accent} • {voice.tone}</div>
                </div>
                <button className="text-blue-600 hover:text-blue-700 text-sm">
                  Play Sample
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <button
        onClick={() => setStep(4)}
        disabled={!selectedAvatar || !selectedVoice}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        Next: Brand Settings
      </button>
    </div>
  );

  const renderStep4 = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Brand Settings</h3>
        <button
          onClick={() => setStep(3)}
          className="text-blue-600 hover:text-blue-700"
        >
          Back
        </button>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Brand Colors</label>
          <div className="flex space-x-2">
            <input
              type="color"
              value={brandSettings.colors[0]}
              onChange={(e) => setBrandSettings({
                ...brandSettings,
                colors: [e.target.value, brandSettings.colors[1]]
              })}
              className="w-12 h-8 border rounded"
            />
            <input
              type="color"
              value={brandSettings.colors[1]}
              onChange={(e) => setBrandSettings({
                ...brandSettings,
                colors: [brandSettings.colors[0], e.target.value]
              })}
              className="w-12 h-8 border rounded"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Logo Position</label>
          <select
            value={brandSettings.logo_position}
            onChange={(e) => setBrandSettings({
              ...brandSettings,
              logo_position: e.target.value
            })}
            className="w-full p-2 border rounded-md"
          >
            <option value="bottom_right">Bottom Right</option>
            <option value="bottom_left">Bottom Left</option>
            <option value="top_right">Top Right</option>
            <option value="top_left">Top Left</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Font</label>
          <select
            value={brandSettings.font}
            onChange={(e) => setBrandSettings({
              ...brandSettings,
              font: e.target.value
            })}
            className="w-full p-2 border rounded-md"
          >
            <option value="Arial">Arial</option>
            <option value="Helvetica">Helvetica</option>
            <option value="Times New Roman">Times New Roman</option>
            <option value="Georgia">Georgia</option>
          </select>
        </div>
      </div>

      <button
        onClick={handleGenerate}
        disabled={loading}
        className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50"
      >
        {loading ? 'Generating Video...' : 'Generate Video'}
      </button>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-2">Create AI Video Ad</h2>
        <div className="flex items-center space-x-4">
          {[1, 2, 3, 4].map((stepNumber) => (
            <div
              key={stepNumber}
              className={`flex items-center ${stepNumber < 4 ? 'flex-1' : ''}`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step >= stepNumber
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {stepNumber}
              </div>
              {stepNumber < 4 && (
                <div
                  className={`flex-1 h-1 mx-2 ${
                    step > stepNumber ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border p-6">
        {step === 1 && renderStep1()}
        {step === 2 && renderStep2()}
        {step === 3 && renderStep3()}
        {step === 4 && renderStep4()}
      </div>
    </div>
  );
};