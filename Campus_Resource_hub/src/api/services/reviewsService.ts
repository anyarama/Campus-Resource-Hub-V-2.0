/**
 * Reviews Service
 * Handles review management operations
 */

import { apiClient, ApiResponse } from '../client';
import type { Review, ReviewFilters, PaginatedResponse, ReviewFormData } from '../types';

/**
 * Get paginated list of reviews with filters
 * Note: Backend doesn't have a general reviews list endpoint
 * Use getResourceReviews() to get reviews for a specific resource
 */
export async function getReviews(
  filters?: ReviewFilters
): Promise<ApiResponse<PaginatedResponse<Review>>> {
  // Backend doesn't support general review listing
  // This is kept for API compatibility
  console.warn('getReviews() not supported by backend. Use getResourceReviews() instead.');
  return Promise.resolve({
    data: { items: [], total: 0, page: 1, per_page: 20, total_pages: 0 },
    success: true,
    status: 200
  });
}

/**
 * Get review by ID
 * Note: Backend doesn't have single review fetch endpoint
 * Reviews are fetched as part of resource data
 */
export async function getReview(id: number): Promise<ApiResponse<Review>> {
  // Backend doesn't support single review fetch
  console.warn('getReview() not supported by backend. Reviews are fetched with resource data.');
  return Promise.reject({
    success: false,
    status: 404,
    error: 'Not found'
  });
}

/**
 * Get reviews for a specific resource
 */
export async function getResourceReviews(
  resourceId: number,
  params?: ReviewFilters
): Promise<ApiResponse<PaginatedResponse<Review>>> {
  return apiClient.get<PaginatedResponse<Review>>(`/reviews/resources/${resourceId}/reviews`, params);
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
