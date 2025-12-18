import axios from 'axios';
import { AuthResponse, LoginRequest, RegisterRequest, User } from '@/types/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          error.config.headers.Authorization = `Bearer ${access}`;
          return api.request(error.config);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data: RegisterRequest) => api.post<{ message: string; user_id: string; otp?: string }>('/auth/register/', data),
  login: (data: LoginRequest) => api.post<AuthResponse>('/auth/login/', data),
  verifyEmail: (data: { token: string; email?: string; user_id?: string }) => api.post<{ message: string }>('/auth/verify-email/', data),
  getProfile: () => api.get<User>('/auth/profile/'),
  updateProfile: (data: Partial<User>) => api.patch<User>('/auth/profile/', data),
  get2FAQRCode: () => api.get<{ qr_code: string; secret: string; is_enabled: boolean }>('/auth/2fa/qr-code/'),
  setup2FA: (data: { token: string }) => api.post<{ message: string; backup_codes: string[] }>('/auth/2fa/setup/', data),
  disable2FA: () => api.post<{ message: string }>('/auth/2fa/disable/'),
};


export default api;
