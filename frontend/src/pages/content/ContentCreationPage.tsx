import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { VideoCreator } from '../../components/content/VideoCreator';
import { TextGenerator } from '../../components/content/TextGenerator';
import { ImageGenerator } from '../../components/content/ImageGenerator';
import { ContentLibrary } from '../../components/content/ContentLibrary';

interface ContentCreationPageProps {
  workspaceId: string;
}

export const ContentCreationPage: React.FC<ContentCreationPageProps> = ({ workspaceId }) => {
  const [activeTab, setActiveTab] = useState<'video' | 'text' | 'image' | 'library'>('video');
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleContentGenerated = (jobId: string) => {
    void jobId;
    setActiveTab('library');
  };

  const handleVideoGenerated = (projectId: string, jobId: string) => {
    handleContentGenerated(jobId);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                ← Back to Dashboard
              </button>
              <div className="text-2xl font-bold text-blue-600">ADLY</div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                {user?.first_name} {user?.last_name}
              </span>
              <button
                onClick={logout}
                className="text-sm bg-gray-100 text-gray-700 px-3 py-1 rounded hover:bg-gray-200"
              >
                Logout
              </button>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Content Creation</h1>
              <p className="text-gray-600 mt-1">Create AI-powered video ads and manage your content</p>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setActiveTab('video')}
                className={`px-4 py-2 rounded-md font-medium ${
                  activeTab === 'video'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                🎥 Video
              </button>
              <button
                onClick={() => setActiveTab('text')}
                className={`px-4 py-2 rounded-md font-medium ${
                  activeTab === 'text'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                📝 Text
              </button>
              <button
                onClick={() => setActiveTab('image')}
                className={`px-4 py-2 rounded-md font-medium ${
                  activeTab === 'image'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                🖼️ Images
              </button>
              <button
                onClick={() => setActiveTab('library')}
                className={`px-4 py-2 rounded-md font-medium ${
                  activeTab === 'library'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                📚 Library
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="py-8">
        {activeTab === 'video' && (
          <VideoCreator 
            workspaceId={workspaceId} 
            onVideoGenerated={handleVideoGenerated}
          />
        )}
        {activeTab === 'text' && (
          <TextGenerator 
            workspaceId={workspaceId} 
            onTextGenerated={handleContentGenerated}
          />
        )}
        {activeTab === 'image' && (
          <ImageGenerator 
            workspaceId={workspaceId} 
            onImageGenerated={handleContentGenerated}
          />
        )}
        {activeTab === 'library' && (
          <ContentLibrary workspaceId={workspaceId} />
        )}
      </div>
    </div>
  );
};
