/**
 * Reviews Service
 * Handles review management operations
 */

import { apiClient, ApiResponse } from '../client';
import type { Review, ReviewFilters, PaginatedResponse, ReviewFormData } from '../types';

/**
 * Get paginated list of reviews with filters
 */
export async function getReviews(
  filters?: ReviewFilters
): Promise<ApiResponse<PaginatedResponse<Review>>> {
  return apiClient.get<PaginatedResponse<Review>>('/reviews', filters);
}

/**
 * Get review by ID
 */
export async function getReview(id: number): Promise<ApiResponse<Review>> {
  return apiClient.get<Review>(`/reviews/${id}`);
}

/**
 * Get reviews for a specific resource
 */
export async function getResourceReviews(
  resourceId: number,
  params?: ReviewFilters
): Promise<ApiResponse<PaginatedResponse<Review>>> {
  return apiClient.get<PaginatedResponse<Review>>(`/reviews/resource/${resourceId}`, params);
}

/**
 * Create new review
 */
export async function createReview(data: ReviewFormData): Promise<ApiResponse<Review>> {
  return apiClient.post<Review>('/reviews', data);
}

/**
 * Update review
 */
export async function updateReview(
  id: number,
  data: Partial<ReviewFormData>
): Promise<ApiResponse<Review>> {
  return apiClient.put<Review>(`/reviews/${id}`, data);
}

/**
 * Delete review
 */
export async function deleteReview(id: number): Promise<ApiResponse> {
  return apiClient.delete(`/reviews/${id}`);
}

/**
 * Flag review as inappropriate
 */
export async function flagReview(id: number): Promise<ApiResponse> {
  return apiClient.post(`/reviews/${id}/flag`);
}
