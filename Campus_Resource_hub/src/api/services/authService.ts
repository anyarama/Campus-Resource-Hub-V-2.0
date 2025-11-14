/**
 * Authentication Service
 * Handles user authentication and session management
 */

import { apiClient, ApiResponse } from '../client';
import type { User, LoginCredentials, SignupData } from '../types';

interface AuthResponse {
  user: User;
  message?: string;
}

/**
 * Login with email and password
 */
export async function login(credentials: LoginCredentials): Promise<ApiResponse<AuthResponse>> {
  const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
  
  // Store user data in session storage on successful login
  if (response.data?.user) {
    apiClient.setCurrentUser(response.data.user);
  }
  
  return response;
}

/**
 * Sign up a new user
 */
export async function signup(data: SignupData): Promise<ApiResponse<AuthResponse>> {
  const payload = {
    name: data.full_name || data.username || data.name || '',
    email: data.email,
    password: data.password,
    role: data.role ?? 'student',
    department: data.department || undefined,
  };

  const response = await apiClient.post<AuthResponse>('/auth/register', payload);
  
  if (response.data?.user) {
    apiClient.setCurrentUser(response.data.user);
  }
  
  return response;
}

/**
 * Logout current user
 */
export async function logout(): Promise<ApiResponse> {
  const response = await apiClient.post('/auth/logout');
  
  // Clear session storage and CSRF token
  apiClient.clearSession();
  
  return response;
}

/**
 * Get current authenticated user
 */
export async function getCurrentUser(): Promise<ApiResponse<User>> {
  return apiClient.get<User>('/auth/me');
}

/**
 * Update current user profile
 */
export async function updateProfile(data: Partial<User>): Promise<ApiResponse<User>> {
  const response = await apiClient.put<User>('/auth/profile', data);
  
  // Update user data in session storage
  if (response.data) {
    apiClient.setCurrentUser(response.data);
  }
  
  return response;
}

/**
 * Change password
 */
export async function changePassword(data: {
  current_password: string;
  new_password: string;
}): Promise<ApiResponse> {
  return apiClient.put('/auth/password', data);
}

/**
 * Request password reset
 */
export async function requestPasswordReset(email: string): Promise<ApiResponse> {
  return apiClient.post('/auth/password-reset', { email });
}

/**
 * Get user from session storage
 */
export function getUserFromStorage(): User | null {
  return apiClient.getCurrentUser();
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return apiClient.isAuthenticated();
}

/**
 * Check if user has specific role
 */
export function hasRole(role: 'student' | 'staff' | 'admin'): boolean {
  const user = getUserFromStorage();
  if (!user) return false;
  
  const roleHierarchy = { student: 1, staff: 2, admin: 3 };
  const userLevel = roleHierarchy[user.role];
  const requiredLevel = roleHierarchy[role];
  
  return userLevel >= requiredLevel;
}

/**
 * Check if user is admin
 */
export function isAdmin(): boolean {
  return hasRole('admin');
}

/**
 * Check if user is staff or higher
 */
export function isStaff(): boolean {
  return hasRole('staff');
}
