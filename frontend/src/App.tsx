import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useParams } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from '@/stores/authStore';
import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { ContentCreationPage } from '@/pages/content/ContentCreationPage';
import { AdAccountsPage } from '@/pages/AdAccountsPage';
import { MetaAdsUploadPage } from '@/pages/MetaAdsUploadPage';
import { WorkspacesPage } from '@/pages/WorkspacesPage';
import { ProtectedRoute } from '@/components/ProtectedRoute';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (renamed from cacheTime in v5)
    },
  },
});

function ContentCreationWrapper() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  return <ContentCreationPage workspaceId={workspaceId || ''} />;
}

function App() {
  const { fetchProfile, isAuthenticated } = useAuthStore();

  useEffect(() => {
    // Check if user is logged in on app start
    const token = localStorage.getItem('access_token');
    if (token && !isAuthenticated) {
      fetchProfile();
    }
  }, [fetchProfile, isAuthenticated]);

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
            <Route path="/content/:workspaceId" element={<ProtectedRoute><ContentCreationWrapper /></ProtectedRoute>} />
            <Route path="/ad-accounts/:workspaceId?" element={<ProtectedRoute><AdAccountsPage /></ProtectedRoute>} />
            <Route path="/meta-ads/:workspaceId?" element={<ProtectedRoute><MetaAdsUploadPage /></ProtectedRoute>} />
            <Route path="/workspaces" element={<ProtectedRoute><WorkspacesPage /></ProtectedRoute>} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
          
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
