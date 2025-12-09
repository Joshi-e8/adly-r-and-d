import React from 'react';
import { useAuthStore } from '@/stores/authStore';
import { Navigate, useNavigate } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();
  
  // Mock workspace ID - in real app this would come from user's workspaces
  const workspaceId = 'demo-workspace-123';

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">ADLY</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, {user?.first_name} {user?.last_name}
              </span>
              <button
                onClick={logout}
                className="btn-secondary text-sm"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Welcome to ADLY Dashboard
            </h2>
            <p className="text-lg text-gray-600 mb-8">
              Create AI-powered video ads like Creatify.ai with Arabic-first support
            </p>
            
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="card text-center">
                <h3 className="text-2xl font-bold text-primary-600">0</h3>
                <p className="text-gray-600">Active Campaigns</p>
              </div>
              <div className="card text-center">
                <h3 className="text-2xl font-bold text-primary-600">0</h3>
                <p className="text-gray-600">Generated Videos</p>
              </div>
              <div className="card text-center">
                <h3 className="text-2xl font-bold text-primary-600">0</h3>
                <p className="text-gray-600">Connected Stores</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={() => navigate(`/content/${workspaceId}`)}
                className="btn-primary"
              >
                🎥 Create AI Video Ads
              </button>
              <button className="btn-secondary">
                🏪 Connect Your Store
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};