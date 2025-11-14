/**
 * Bookings Service
 * Handles booking management operations
 */

import { apiClient, ApiResponse } from '../client';
import type { Booking, BookingFilters, PaginatedResponse, BookingFormData } from '../types';

/**
 * Get paginated list of bookings with filters
 */
export async function getBookings(
  filters?: BookingFilters
): Promise<ApiResponse<PaginatedResponse<Booking>>> {
  return apiClient.get<PaginatedResponse<Booking>>('/bookings', filters);
}

/**
 * Get booking by ID
 */
export async function getBooking(id: number): Promise<ApiResponse<Booking>> {
  return apiClient.get<Booking>(`/bookings/${id}`);
}

/**
 * Create new booking
 */
export async function createBooking(data: BookingFormData): Promise<ApiResponse<Booking>> {
  return apiClient.post<Booking>('/bookings', data);
}

/**
 * Update booking
 */
export async function updateBooking(
  id: number,
  data: Partial<BookingFormData>
): Promise<ApiResponse<Booking>> {
  return apiClient.put<Booking>(`/bookings/${id}`, data);
}

/**
 * Cancel booking
 */
export async function cancelBooking(id: number): Promise<ApiResponse> {
  return apiClient.post(`/bookings/${id}/cancel`);
}

/**
 * Confirm booking (staff/admin only)
 */
export async function confirmBooking(id: number): Promise<ApiResponse> {
  return apiClient.post(`/bookings/${id}/confirm`);
}

/**
 * Complete booking
 */
export async function completeBooking(id: number): Promise<ApiResponse> {
  return apiClient.post(`/bookings/${id}/complete`);
}

/**
 * Get current user's bookings
 */
export async function getMyBookings(
  filters?: Omit<BookingFilters, 'user_id'>
): Promise<ApiResponse<PaginatedResponse<Booking>>> {
  return apiClient.get<PaginatedResponse<Booking>>('/bookings', filters);
}
