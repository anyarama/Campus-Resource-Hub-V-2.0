/**
 * Resources Service
 * Handles resource management operations
 */

import { apiClient, ApiResponse } from '../client';
import type { Resource, ResourceFilters, PaginatedResponse, ResourceFormData } from '../types';

/**
 * Get paginated list of resources with filters
 */
export async function getResources(
  filters?: ResourceFilters
): Promise<ApiResponse<PaginatedResponse<Resource>>> {
  return apiClient.get<PaginatedResponse<Resource>>('/resources', filters);
}

/**
 * Get resource by ID
 */
export async function getResource(id: number): Promise<ApiResponse<Resource>> {
  return apiClient.get<Resource>(`/resources/${id}`);
}

/**
 * Create new resource (staff/admin only)
 */
export async function createResource(data: ResourceFormData): Promise<ApiResponse<Resource>> {
  return apiClient.post<Resource>('/resources', data);
}

/**
 * Update resource (staff/admin only)
 */
export async function updateResource(
  id: number,
  data: Partial<ResourceFormData>
): Promise<ApiResponse<Resource>> {
  return apiClient.put<Resource>(`/resources/${id}`, data);
}

/**
 * Delete resource (admin only)
 */
export async function deleteResource(id: number): Promise<ApiResponse> {
  return apiClient.delete(`/resources/${id}`);
}

/**
 * Upload resource image (staff/admin only)
 */
export async function uploadResourceImage(
  id: number,
  file: File
): Promise<ApiResponse<{ image_url: string }>> {
  const formData = new FormData();
  formData.append('image', file);
  
  return apiClient.upload<{ image_url: string }>(`/resources/${id}/image`, formData);
}

/**
 * Get available time slots for a resource
 */
export async function getAvailableSlots(
  id: number,
  date: string
): Promise<ApiResponse<{ available_slots: string[] }>> {
  return apiClient.get<{ available_slots: string[] }>(`/resources/${id}/availability`, { date });
}

/**
 * Get resource types
 */
export async function getResourceTypes(): Promise<ApiResponse<{ types: string[] }>> {
  return apiClient.get<{ types: string[] }>('/resources/types');
}

/**
 * Search resources by name or description
 */
export async function searchResources(
  query: string
): Promise<ApiResponse<PaginatedResponse<Resource>>> {
  return apiClient.get<PaginatedResponse<Resource>>('/resources', { search: query });
}
