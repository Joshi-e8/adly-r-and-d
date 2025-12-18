import React, { useState } from 'react';
import { Navigate, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

export const VerifyEmailPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation() as { state?: { email?: string; user_id?: string; token?: string } };
  const { isAuthenticated, verifyEmail, isLoading } = useAuthStore();

  const [email, setEmail] = useState<string>(location.state?.email || '');
  const [token, setToken] = useState<string>(location.state?.token || '');
  const userId = location.state?.user_id;

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await verifyEmail({ user_id: userId, email, token });
      navigate('/login');
    } catch {
      // handled in store toast
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-primary-600">ADLY</h1>
          <p className="text-gray-600 mt-2">Verify your email to continue</p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="card">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Email Verification</h2>
            <p className="text-gray-600 mt-2">Enter the 6-digit code sent to your email.</p>
          </div>
          <form onSubmit={onSubmit} className="space-y-4">
            {email ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <div className="input-field bg-gray-50">{email}</div>
              </div>
            ) : (
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <input
                  id="email"
                  type="email"
                  className="input-field"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            )}
            <div>
              <label htmlFor="token" className="block text-sm font-medium text-gray-700 mb-1">Verification Code</label>
              <input
                id="token"
                type="text"
                className="input-field"
                placeholder="Enter 6-digit code"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                maxLength={6}
                required
              />
            </div>
            <button type="submit" className="btn-primary w-full" disabled={isLoading}>
              {isLoading ? 'Verifying…' : 'Verify Email'}
            </button>
            <p className="text-xs text-gray-500 text-center">Didn’t get a code? Check spam or try again later.</p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default VerifyEmailPage;
