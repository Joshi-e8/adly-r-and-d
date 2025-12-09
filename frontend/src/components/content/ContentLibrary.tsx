import React, { useState, useEffect } from 'react';
import { ContentAPI } from '../../services/content/contentApi';
import { ContentAsset, GenerationJob } from '../../types/content';

interface ContentLibraryProps {
  workspaceId: string;
}

export const ContentLibrary: React.FC<ContentLibraryProps> = ({ workspaceId }) => {
  const [contentApi] = useState(() => new ContentAPI(workspaceId));
  const [assets, setAssets] = useState<ContentAsset[]>([]);
  const [jobs, setJobs] = useState<GenerationJob[]>([]);
  const [activeTab, setActiveTab] = useState<'assets' | 'jobs'>('assets');
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'image' | 'video' | 'text' | 'audio'>('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [assetsData, jobsData] = await Promise.all([
        contentApi.getAssets(),
        contentApi.getJobs()
      ]);
      setAssets(assetsData);
      setJobs(jobsData);
    } catch (error) {
      console.error('Failed to load content data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredAssets = assets.filter(asset => 
    filter === 'all' || asset.type === filter
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'processing': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'video': return '🎥';
      case 'image': return '🖼️';
      case 'audio': return '🎵';
      case 'text': return '📝';
      default: return '📄';
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'Unknown';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderAssets = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex space-x-2">
          {['all', 'video', 'image', 'text', 'audio'].map((type) => (
            <button
              key={type}
              onClick={() => setFilter(type as any)}
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                filter === type
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
        <button
          onClick={loadData}
          className="text-blue-600 hover:text-blue-700"
        >
          Refresh
        </button>
      </div>

      {filteredAssets.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📁</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No content yet</h3>
          <p className="text-gray-500">Start creating content to see it here</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAssets.map((asset) => (
            <div key={asset.id} className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">{getTypeIcon(asset.type)}</span>
                  <div>
                    <h4 className="font-medium text-gray-900 truncate">{asset.name}</h4>
                    <p className="text-sm text-gray-500">{asset.type}</p>
                  </div>
                </div>
                <div className="flex space-x-1">
                  <button className="text-gray-400 hover:text-gray-600">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                    </svg>
                  </button>
                </div>
              </div>

              {asset.file_url && (
                <div className="mb-3">
                  {asset.type === 'image' && (
                    <img
                      src={asset.file_url}
                      alt={asset.name}
                      className="w-full h-32 object-cover rounded"
                    />
                  )}
                  {asset.type === 'video' && (
                    <video
                      src={asset.file_url}
                      className="w-full h-32 object-cover rounded"
                      controls
                    />
                  )}
                </div>
              )}

              <div className="space-y-2 text-sm text-gray-500">
                <div className="flex justify-between">
                  <span>Size:</span>
                  <span>{formatFileSize(asset.file_size)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Language:</span>
                  <span>{asset.language === 'ar' ? 'العربية' : 'English'}</span>
                </div>
                {asset.generated_by && (
                  <div className="flex justify-between">
                    <span>Generated by:</span>
                    <span className="capitalize">{asset.generated_by}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span>Created:</span>
                  <span>{formatDate(asset.created_at)}</span>
                </div>
              </div>

              <div className="mt-4 flex space-x-2">
                {asset.file_url && (
                  <a
                    href={asset.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 bg-blue-600 text-white text-center py-2 px-3 rounded text-sm hover:bg-blue-700"
                  >
                    View
                  </a>
                )}
                <button className="flex-1 bg-gray-100 text-gray-700 py-2 px-3 rounded text-sm hover:bg-gray-200">
                  Download
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderJobs = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Generation Jobs</h3>
        <button
          onClick={loadData}
          className="text-blue-600 hover:text-blue-700"
        >
          Refresh
        </button>
      </div>

      {jobs.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">⚙️</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No generation jobs</h3>
          <p className="text-gray-500">Start generating content to see jobs here</p>
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map((job) => (
            <div key={job.id} className="bg-white border rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">{getTypeIcon(job.type)}</span>
                  <div>
                    <h4 className="font-medium text-gray-900">
                      {job.type.charAt(0).toUpperCase() + job.type.slice(1)} Generation
                    </h4>
                    <p className="text-sm text-gray-500">
                      Provider: {job.provider} • {formatDate(job.created_at)}
                    </p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                  {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                </span>
              </div>

              {job.prompt && (
                <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                  <strong>Prompt:</strong> {job.prompt.substring(0, 200)}
                  {job.prompt.length > 200 && '...'}
                </div>
              )}

              {job.error_message && (
                <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                  <strong>Error:</strong> {job.error_message}
                </div>
              )}

              {job.result_asset && (
                <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded text-sm text-green-700">
                  <strong>Result:</strong> {job.result_asset.name}
                  <a
                    href={job.result_asset.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-2 text-blue-600 hover:text-blue-700"
                  >
                    View
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">Content Library</h2>
        <p className="text-gray-600">Manage your generated content and track generation jobs</p>
      </div>

      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('assets')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'assets'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Content Assets ({assets.length})
            </button>
            <button
              onClick={() => setActiveTab('jobs')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'jobs'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Generation Jobs ({jobs.length})
            </button>
          </nav>
        </div>
      </div>

      {activeTab === 'assets' ? renderAssets() : renderJobs()}
    </div>
  );
};