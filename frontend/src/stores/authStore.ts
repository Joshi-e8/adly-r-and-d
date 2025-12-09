import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, LoginRequest, RegisterRequest } from '@/types/auth';
import { authAPI } from '@/services/api';
import toast from 'react-hot-toast';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  verifyEmail: (email: string, token: string) => Promise<void>;
  fetchProfile: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (data: LoginRequest) => {
        set({ isLoading: true });
        try {
          const response = await authAPI.login(data);
          const { access_token, refresh_token, user } = response.data;
          
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          
          set({ 
            user, 
            isAuthenticated: true, 
            isLoading: false 
          });
          
          toast.success('Login successful!');
        } catch (error: any) {
          set({ isLoading: false });
          const message = error.response?.data?.detail || 'Login failed';
          toast.error(message);
          throw error;
        }
      },

      register: async (data: RegisterRequest) => {
        set({ isLoading: true });
        try {
          await authAPI.register(data);
          set({ isLoading: false });
          toast.success('Registration successful! Please check your email for verification.');
        } catch (error: any) {
          set({ isLoading: false });
          const message = error.response?.data?.detail || 'Registration failed';
          toast.error(message);
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ 
          user: null, 
          isAuthenticated: false 
        });
        toast.success('Logged out successfully');
      },

      verifyEmail: async (email: string, token: string) => {
        set({ isLoading: true });
        try {
          await authAPI.verifyEmail({ email, token });
          set({ isLoading: false });
          toast.success('Email verified successfully!');
        } catch (error: any) {
          set({ isLoading: false });
          const message = error.response?.data?.detail || 'Verification failed';
          toast.error(message);
          throw error;
        }
      },

      fetchProfile: async () => {
        try {
          const response = await authAPI.getProfile();
          set({ 
            user: response.data, 
            isAuthenticated: true 
          });
        } catch (error) {
          set({ 
            user: null, 
            isAuthenticated: false 
          });
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      },

      updateProfile: async (data: Partial<User>) => {
        set({ isLoading: true });
        try {
          const response = await authAPI.updateProfile(data);
          set({ 
            user: response.data, 
            isLoading: false 
          });
          toast.success('Profile updated successfully!');
        } catch (error: any) {
          set({ isLoading: false });
          const message = error.response?.data?.detail || 'Update failed';
          toast.error(message);
          throw error;
        }
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({ 
        user: state.user, 
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
);