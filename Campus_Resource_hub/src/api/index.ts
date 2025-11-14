/**
 * API Services Index
 * Central export point for all API services
 */

// Export API client
export { apiClient } from './client';
export type { ApiResponse, ApiError, RequestOptions } from './client';

// Export types
export type {
  User,
  Resource,
  Booking,
  Message,
  MessageThread,
  Review,
  SystemAnalytics,
  ActivityReport,
  PaginationParams,
  PaginatedResponse,
  ResourceFilters,
  BookingFilters,
  UserFilters,
  ReviewFilters,
  LoginCredentials,
  SignupData,
  ResourceFormData,
  BookingFormData,
  MessageFormData,
  ReviewFormData,
} from './types';

// Export auth service
export * as authService from './services/authService';

// Export resource service
export * as resourcesService from './services/resourcesService';

// Export bookings service
export * as bookingsService from './services/bookingsService';

// Export messages service
export * as messagesService from './services/messagesService';

// Export reviews service
export * as reviewsService from './services/reviewsService';

// Export admin service
export * as adminService from './services/adminService';
