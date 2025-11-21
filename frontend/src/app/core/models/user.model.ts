export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name?: string;
  role: 'admin' | 'hr_manager' | 'recruiter' | 'manager' | 'employee';
  role_display?: string;
  profile_picture?: string;
  bio?: string;
  phone?: string;
  employee?: number;
  employee_name?: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface TokenRefresh {
  refresh: string;
}

export interface TokenRefreshResponse {
  access: string;
}

