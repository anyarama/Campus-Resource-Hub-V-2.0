/**
 * Admin Service
 * Handles admin-specific operations
 */

import { apiClient, ApiResponse } from '../client';
import type { 
  User, 
  Resource, 
  Review, 
  SystemAnalytics, 
  ActivityReport,
  UserFilters, 
  PaginatedResponse 
} from '../types';

/**
 * Get system analytics
 */
export async function getAnalytics(): Promise<ApiResponse<SystemAnalytics>> {
  return apiClient.get<SystemAnalytics>('/admin/analytics');
}

/**
 * Get all users with filters (admin only)
 */
export async function getUsers(
  filters?: UserFilters
): Promise<ApiResponse<PaginatedResponse<User>>> {
  return apiClient.get<PaginatedResponse<User>>('/admin/users', filters);
}

/**
 * Update user role (admin only)
 */
export async function updateUserRole(
  userId: number,
  role: 'student' | 'staff' | 'admin'
): Promise<ApiResponse<User>> {
  return apiClient.put<User>(`/admin/users/${userId}/role`, { role });
}

/**
 * Update user status (admin only)
 */
export async function updateUserStatus(
  userId: number,
  status: 'active' | 'inactive' | 'suspended'
): Promise<ApiResponse<User>> {
  return apiClient.put<User>(`/admin/users/${userId}/status`, { status });
}

/**
 * Get all resources for admin management
 */
export async function getAdminResources(
  params?: Record<string, any>
): Promise<ApiResponse<PaginatedResponse<Resource>>> {
  return apiClient.get<PaginatedResponse<Resource>>('/admin/resources', params);
}

/**
 * Get flagged reviews (admin only)
 */
export async function getFlaggedReviews(
  params?: Record<string, any>
): Promise<ApiResponse<PaginatedResponse<Review>>> {
  return apiClient.get<PaginatedResponse<Review>>('/admin/reviews/flagged', params);
}

/**
 * Hide review (admin only)
 */
export async function hideReview(reviewId: number): Promise<ApiResponse> {
  return apiClient.post(`/admin/reviews/${reviewId}/hide`);
}

/**
 * Unhide review (admin only)
 */
export async function unhideReview(reviewId: number): Promise<ApiResponse> {
  return apiClient.post(`/admin/reviews/${reviewId}/unhide`);
}

/**
 * Get activity report
 */
export async function getActivityReport(params?: {
  start_date?: string;
  end_date?: string;
  period?: 'day' | 'week' | 'month';
}): Promise<ApiResponse<ActivityReport>> {
  return apiClient.get<ActivityReport>('/admin/reports/activity', params);
}
