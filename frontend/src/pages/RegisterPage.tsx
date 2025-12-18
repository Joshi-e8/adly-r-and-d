import React from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { RegisterForm } from '@/components/RegisterForm';
import { useAuthStore } from '@/stores/authStore';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleRegisterSuccess = (email: string, userId?: string, otp?: string) => {
    navigate('/verify-email', { state: { email, user_id: userId, token: otp } });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-primary-600">ADLY</h1>
          <p className="text-gray-600 mt-2">AI-Powered Video Ad Creation Platform</p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <RegisterForm onSuccess={handleRegisterSuccess} />
      </div>
    </div>
  );
};
