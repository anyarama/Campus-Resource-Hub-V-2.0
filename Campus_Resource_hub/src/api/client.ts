/**
 * API Client Configuration
 * Centralized HTTP client with authentication, error handling, and interceptors
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean>;
}

interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
  status: number;
}

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  /**
   * Get authentication token from session storage
   */
  private getAuthToken(): string | null {
    return sessionStorage.getItem('auth_token');
  }

  /**
   * Set authentication token in session storage
   */
  setAuthToken(token: string): void {
    sessionStorage.setItem('auth_token', token);
  }

  /**
   * Remove authentication token from session storage
   */
  clearAuthToken(): void {
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('user');
  }

  /**
   * Check if user has authentication token
   */
  hasAuthToken(): boolean {
    return !!this.getAuthToken();
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
   * Build request headers with authentication
   */
  private buildHeaders(includeAuth: boolean = true): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (includeAuth) {
      const token = this.getAuthToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  /**
   * Handle API response and errors
   */
  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    const status = response.status;
    
    // Try to parse JSON response
    let data: any;
    try {
      data = await response.json();
    } catch {
      data = null;
    }

    // Handle successful responses
    if (response.ok) {
      return {
        data: data,
        status,
      };
    }

    // Handle error responses
    const error = data?.error || data?.message || response.statusText || 'An error occurred';

    // Handle 401 Unauthorized - clear token and redirect to login
    if (status === 401) {
      this.clearAuthToken();
      // Optionally trigger a redirect to login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }

    return {
      error,
      message: data?.message,
      status,
    };
  }

  /**
   * Generic request method
   */
  private async request<T = any>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const { params, headers: customHeaders, ...fetchOptions } = options;
    
    const url = this.buildURL(endpoint, params);
    const headers = {
      ...this.buildHeaders(options.method !== 'GET'),
      ...customHeaders,
    };

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        headers,
        credentials: 'include', // Include cookies for session management
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      console.error('API Request Error:', error);
      return {
        error: 'Network error. Please check your connection.',
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
   * Upload file (multipart/form-data)
   */
  async upload<T = any>(
    endpoint: string,
    formData: FormData
  ): Promise<ApiResponse<T>> {
    const url = this.buildURL(endpoint);
    const token = this.getAuthToken();
    
    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: formData,
        credentials: 'include',
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      console.error('File Upload Error:', error);
      return {
        error: 'File upload failed. Please try again.',
        status: 0,
      };
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient(API_BASE_URL);

// Export types
export type { ApiResponse, RequestOptions };
