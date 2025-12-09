export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_verified: boolean;
  has_2fa: boolean;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  otp_token?: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  role: 'owner' | 'member' | 'viewer';
  member_count: number;
  created_at: string;
  updated_at: string;
}