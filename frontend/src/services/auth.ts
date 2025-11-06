/**
 * Authentication Service
 */
import api from '@/lib/api';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
}

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_email_verified: boolean;
  date_joined: string;
  last_login: string;
  profile?: any;
}

export interface AuthResponse {
  access: string;
  refresh: string;
}

export const authService = {
  /**
   * Login user and store tokens
   */
  async login(credentials: LoginCredentials): Promise<User> {
    const response = await api.post<AuthResponse>('/auth/login/', credentials);
    const { access, refresh } = response.data;

    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);

    // Get user details
    const userResponse = await api.get<User>('/auth/me/');
    localStorage.setItem('user', JSON.stringify(userResponse.data));

    return userResponse.data;
  },

  /**
   * Register new user
   */
  async register(data: RegisterData): Promise<{ user: User; message: string }> {
    const response = await api.post('/auth/register/', data);
    return response.data;
  },

  /**
   * Logout user and clear tokens
   */
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  /**
   * Get current user from localStorage or API
   */
  async getCurrentUser(): Promise<User | null> {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      return JSON.parse(storedUser);
    }

    try {
      const response = await api.get<User>('/auth/me/');
      localStorage.setItem('user', JSON.stringify(response.data));
      return response.data;
    } catch (error) {
      return null;
    }
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await api.patch<User>('/auth/profile/', data);
    localStorage.setItem('user', JSON.stringify(response.data));
    return response.data;
  },

  /**
   * Change password
   */
  async changePassword(data: {
    old_password: string;
    new_password: string;
    confirm_password: string;
  }): Promise<{ message: string }> {
    const response = await api.put('/auth/change-password/', data);
    return response.data;
  },
};
