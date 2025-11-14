/**
 * API Types and Interfaces
 * Shared types for API requests and responses
 */

// API Response and Error Types
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
  status: number;
}

export interface ApiError {
  message: string;
  status: number;
  code?: string;
  details?: any;
}

// User Types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: 'student' | 'staff' | 'admin';
  department?: string;
  phone?: string;
  status: 'active' | 'inactive' | 'suspended';
  created_at: string;
  updated_at: string;
}

// Resource Types
export interface Resource {
  id: number;
  name: string;
  type: 'room' | 'equipment' | 'facility' | 'other';
  description?: string;
  location: string;
  capacity?: number;
  available: boolean;
  image_url?: string;
  amenities?: string[];
  hourly_rate?: number;
  campus?: string;
  building?: string;
  floor?: string;
  contact_email?: string;
  created_at: string;
  updated_at: string;
}

// Booking Types
export interface Booking {
  id: number;
  user_id: number;
  resource_id: number;
  start_time: string;
  end_time: string;
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed';
  purpose?: string;
  notes?: string;
  attendees_count?: number;
  total_cost?: number;
  created_at: string;
  updated_at: string;
  user?: User;
  resource?: Resource;
}

// Message Types
export interface Message {
  id: number;
  sender_id: number;
  recipient_id: number;
  thread_id: string;
  subject: string;
  body: string;
  read: boolean;
  created_at: string;
  sender?: User;
  recipient?: User;
}

export interface MessageThread {
  thread_id: string;
  subject: string;
  participant_id: number;
  participant_name: string;
  last_message: string;
  last_message_time: string;
  unread_count: number;
}

// Review Types
export interface Review {
  id: number;
  user_id: number;
  resource_id: number;
  booking_id?: number;
  rating: number;
  comment?: string;
  is_flagged: boolean;
  is_hidden: boolean;
  created_at: string;
  updated_at: string;
  user?: User;
  resource?: Resource;
}

// Admin Types
export interface SystemAnalytics {
  total_users: number;
  total_resources: number;
  total_bookings: number;
  active_bookings: number;
  total_messages: number;
  total_reviews: number;
  avg_rating: number;
  user_breakdown: {
    students: number;
    staff: number;
    admins: number;
  };
  resource_breakdown: Record<string, number>;
  booking_status_breakdown: Record<string, number>;
  recent_activity: number;
}

export interface ActivityReport {
  period: string;
  metrics: {
    new_users: number;
    new_bookings: number;
    new_reviews: number;
    new_messages: number;
    cancelled_bookings: number;
  };
}

// Pagination Types
export interface PaginationParams {
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Filter Types
export interface ResourceFilters extends PaginationParams {
  type?: string;
  available?: boolean;
  location?: string;
  min_capacity?: number;
  max_capacity?: number;
  search?: string;
}

export interface BookingFilters extends PaginationParams {
  status?: string;
  resource_id?: number;
  start_date?: string;
  end_date?: string;
}

export interface UserFilters extends PaginationParams {
  role?: string;
  status?: string;
  department?: string;
  search?: string;
}

export interface ReviewFilters extends PaginationParams {
  resource_id?: number;
  rating?: number;
  is_flagged?: boolean;
}

// Form Data Types
export interface LoginCredentials {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface SignupData {
  email: string;
  username: string;
  password: string;
  full_name: string;
  role?: 'student' | 'staff';
  department?: string;
  phone?: string;
  name?: string;
}

export interface ResourceFormData {
  name: string;
  type: 'room' | 'equipment' | 'facility' | 'other';
  description?: string;
  location: string;
  capacity?: number;
  available?: boolean;
  amenities?: string[];
  hourly_rate?: number;
  campus?: string;
  building?: string;
  floor?: string;
  contact_email?: string;
}

export interface BookingFormData {
  resource_id: number;
  start_time: string;
  end_time: string;
  purpose?: string;
  notes?: string;
  attendees_count?: number;
}

export interface MessageFormData {
  recipient_id: number;
  subject: string;
  body: string;
  thread_id?: string;
}

export interface ReviewFormData {
  resource_id: number;
  booking_id?: number;
  rating: number;
  comment?: string;
}
