/**
 * API Client Configuration
 * Centralized HTTP client with CSRF protection, session management, and error handling
 * 
 * Security Features:
 * - Automatic CSRF token fetching and caching
 * - Session-based authentication (cookies)
 * - Request/response interceptors
 * - Automatic token refresh on expiry
 * - Comprehensive error handling
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean>;
  skipCSRF?: boolean; // Skip CSRF token for specific requests
  skipAuth?: boolean; // Skip authentication check
}

interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
  status: number;
}

interface ApiError {
  message: string;
  status: number;
  code?: string;
  details?: any;
}

class ApiClient {
  private baseURL: string;
  private csrfToken: string | null = null;
  private csrfTokenExpiry: number | null = null;
  private isFetchingCSRF: Promise<string> | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  /**
   * Get CSRF token from cache or fetch new one
   */
  private async getCSRFToken(forceRefresh: boolean = false): Promise<string> {
    // Return cached token if valid
    if (
      !forceRefresh &&
      this.csrfToken &&
      this.csrfTokenExpiry &&
      Date.now() < this.csrfTokenExpiry
    ) {
      return this.csrfToken;
    }

    // If already fetching, wait for that request
    if (this.isFetchingCSRF) {
      return this.isFetchingCSRF;
    }

    // Fetch new CSRF token
    this.isFetchingCSRF = this.fetchCSRFToken();
    try {
      const token = await this.isFetchingCSRF;
      return token;
    } finally {
      this.isFetchingCSRF = null;
    }
  }

  /**
   * Fetch CSRF token from backend
   */
  private async fetchCSRFToken(): Promise<string> {
    try {
      const response = await fetch(`${this.baseURL}/auth/csrf-token`, {
        method: 'GET',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to fetch CSRF token');
      }

      const data = await response.json();
      this.csrfToken = data.csrf_token;
      // Token expires in 1 hour, cache for 55 minutes to be safe
      this.csrfTokenExpiry = Date.now() + 55 * 60 * 1000;
      
      return this.csrfToken as string;
    } catch (error) {
      console.error('CSRF token fetch error:', error);
      throw error;
    }
  }

  /**
   * Clear CSRF token cache (call on logout)
   */
  clearCSRFToken(): void {
    this.csrfToken = null;
    this.csrfTokenExpiry = null;
  }

  /**
   * Get current user from session storage
   */
  getCurrentUser(): any | null {
    const userStr = sessionStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Set current user in session storage
   */
  setCurrentUser(user: any): void {
    sessionStorage.setItem('user', JSON.stringify(user));
  }

  /**
   * Clear user session
   */
  clearSession(): void {
    sessionStorage.removeItem('user');
    this.clearCSRFToken();
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getCurrentUser();
  }

  /**
   * Build URL with query parameters
   */
  private buildURL(endpoint: string, params?: Record<string, any>): string {
    const url = new URL(`${this.baseURL}${endpoint}`);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }
    
    return url.toString();
  }

  /**
   * Build request headers (with optional CSRF token)
   */
  private async buildHeaders(
    method: string,
    skipCSRF: boolean = false,
    customHeaders: HeadersInit = {}
  ): Promise<HeadersInit> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...customHeaders,
    };

    // Add CSRF token for mutation requests
    const requiresCSRF = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method.toUpperCase());
    if (requiresCSRF && !skipCSRF) {
      try {
        const csrfToken = await this.getCSRFToken();
        headers['X-CSRF-Token'] = csrfToken;
      } catch (error) {
        console.error('Failed to get CSRF token:', error);
        // Continue without CSRF token - request will likely fail but we'll handle error
      }
    }

    return headers;
  }

  /**
   * Handle API response and errors
   */
  private async handleResponse<T>(
    response: Response,
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const status = response.status;
    
    // Try to parse JSON response
    let data: any;
    try {
      data = await response.json();
    } catch {
      // Non-JSON response or empty body
      data = null;
    }

    // Handle successful responses
    if (response.ok) {
      return {
        data: data?.data || data, // Backend may wrap in {data: ...}
        message: data?.message,
        status,
      };
    }

    // Handle error responses
    const error = data?.error || data?.message || response.statusText || 'An error occurred';

    // Handle 401 Unauthorized - session expired
    if (status === 401) {
      this.clearSession();
      
      // Redirect to login if not already there
      if (!options.skipAuth && window.location.pathname !== '/login') {
        // Store intended destination
        sessionStorage.setItem('redirectAfterLogin', window.location.pathname);
        window.location.href = '/login';
      }
    }

    // Handle 400 Bad Request - might be CSRF token expired
    if (status === 400 && error.toLowerCase().includes('csrf')) {
      console.warn('CSRF token expired, refreshing...');
      // Token might be expired, clear cache
      this.clearCSRFToken();
    }

    // Handle 403 Forbidden - insufficient permissions
    if (status === 403) {
      console.error('Access denied:', error);
    }

    // Handle 429 Too Many Requests - rate limiting
    if (status === 429) {
      console.warn('Rate limit exceeded:', error);
    }

    return {
      error,
      message: data?.message,
      status,
      data: data,
    };
  }

  /**
   * Generic request method with retry logic
   */
  private async request<T = any>(
    endpoint: string,
    options: RequestOptions = {},
    retryCount: number = 0
  ): Promise<ApiResponse<T>> {
    const { params, headers: customHeaders, skipCSRF, skipAuth, ...fetchOptions } = options;
    const method = fetchOptions.method || 'GET';
    
    const url = this.buildURL(endpoint, params);
    const headers = await this.buildHeaders(method, skipCSRF, customHeaders);

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        headers,
        credentials: 'include', // Essential for session cookies
      });

      const result = await this.handleResponse<T>(response, endpoint, options);

      // Retry once if CSRF token was invalid (status 400 with CSRF error)
      if (
        result.status === 400 &&
        result.error?.toLowerCase().includes('csrf') &&
        retryCount === 0
      ) {
        console.log('Retrying request with fresh CSRF token...');
        // Force refresh CSRF token
        await this.getCSRFToken(true);
        // Retry the request
        return this.request<T>(endpoint, options, retryCount + 1);
      }

      return result;
    } catch (error) {
      console.error('API Request Error:', error);
      
      // Network error or fetch failed
      return {
        error: error instanceof Error ? error.message : 'Network error. Please check your connection.',
        status: 0,
      };
    }
  }

  /**
   * GET request
   */
  async get<T = any>(
    endpoint: string,
    params?: Record<string, any>
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET', params });
  }

  /**
   * POST request
   */
  async post<T = any>(
    endpoint: string,
    body?: any,
    options?: RequestOptions
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
      ...options,
    });
  }

  /**
   * PUT request
   */
  async put<T = any>(
    endpoint: string,
    body?: any,
    options?: RequestOptions
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body),
      ...options,
    });
  }

  /**
   * PATCH request
   */
  async patch<T = any>(
    endpoint: string,
    body?: any,
    options?: RequestOptions
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(body),
      ...options,
    });
  }

  /**
   * DELETE request
   */
  async delete<T = any>(
    endpoint: string,
    params?: Record<string, any>
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE', params });
  }

  /**
   * Upload file (multipart/form-data) with CSRF protection
   */
  async upload<T = any>(
    endpoint: string,
    formData: FormData,
    retryCount: number = 0
  ): Promise<ApiResponse<T>> {
    const url = this.buildURL(endpoint);
    
    try {
      // Get CSRF token
      const csrfToken = await this.getCSRFToken();
      
      // Don't set Content-Type header - browser will set it with boundary
      const headers: HeadersInit = {
        'X-CSRF-Token': csrfToken,
      };

      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: formData,
        credentials: 'include',
      });

      const result = await this.handleResponse<T>(response, endpoint);

      // Retry once if CSRF token was invalid
      if (
        result.status === 400 &&
        result.error?.toLowerCase().includes('csrf') &&
        retryCount === 0
      ) {
        console.log('Retrying upload with fresh CSRF token...');
        await this.getCSRFToken(true);
        return this.upload<T>(endpoint, formData, retryCount + 1);
      }

      return result;
    } catch (error) {
      console.error('File Upload Error:', error);
      return {
        error: error instanceof Error ? error.message : 'File upload failed. Please try again.',
        status: 0,
      };
    }
  }

  /**
   * Initialize client (fetch CSRF token on app startup)
   */
  async initialize(): Promise<void> {
    try {
      await this.getCSRFToken();
      console.log('API client initialized with CSRF token');
    } catch (error) {
      console.warn('Failed to initialize CSRF token:', error);
      // Not fatal - token will be fetched on first mutation request
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient(API_BASE_URL);

// Export types
export type { ApiResponse, ApiError, RequestOptions };
