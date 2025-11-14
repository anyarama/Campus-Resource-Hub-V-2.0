/**
 * Authentication Context
 * Provides global authentication state and methods for the application
 * 
 * Features:
 * - Login/Logout functionality
 * - Session persistence
 * - User role checking
 * - Auto-redirect on session expiry
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '../api/client';
import { authService } from '../api';
import type { User, LoginCredentials, SignupData } from '../api/types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<boolean>;
  signup: (data: SignupData) => Promise<boolean>;
  logout: () => Promise<void>;
  updateUser: (user: User) => void;
  clearError: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isStaff: boolean;
  hasRole: (role: 'student' | 'staff' | 'admin') => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Initialize auth state from session storage on mount
   */
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Initialize API client (fetch CSRF token)
        await apiClient.initialize();

        // Check if user data exists in session storage
        const storedUser = apiClient.getCurrentUser();
        if (storedUser) {
          // Verify session is still valid by fetching current user
          const response = await authService.getCurrentUser();
          if (response.data) {
            setUser(response.data);
            apiClient.setCurrentUser(response.data);
          } else {
            // Session expired, clear local data
            apiClient.clearSession();
            setUser(null);
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        // Clear any stale session data
        apiClient.clearSession();
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  /**
   * Login user with email and password
   */
  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      const response = await authService.login(credentials);

      if (response.error) {
        setError(response.error);
        return false;
      }

      if (response.data?.user) {
        setUser(response.data.user);
        apiClient.setCurrentUser(response.data.user);
        return true;
      }

      setError('Login failed. Please try again.');
      return false;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Sign up new user
   */
  const signup = async (data: SignupData): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      const response = await authService.signup(data);

      if (response.error) {
        setError(response.error);
        return false;
      }

      if (response.data?.user) {
        setUser(response.data.user);
        apiClient.setCurrentUser(response.data.user);
        return true;
      }

      setError('Signup failed. Please try again.');
      return false;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Signup failed';
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Logout current user
   */
  const logout = async (): Promise<void> => {
    setLoading(true);

    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
      // Continue with logout even if API call fails
    } finally {
      setUser(null);
      apiClient.clearSession();
      setLoading(false);
      
      // Redirect to login page
      window.location.href = '/login';
    }
  };

  /**
   * Update user data (after profile changes)
   */
  const updateUser = (updatedUser: User): void => {
    setUser(updatedUser);
    apiClient.setCurrentUser(updatedUser);
  };

  /**
   * Clear error message
   */
  const clearError = (): void => {
    setError(null);
  };

  /**
   * Check if user has specific role
   */
  const hasRole = (role: 'student' | 'staff' | 'admin'): boolean => {
    if (!user) return false;

    const roleHierarchy: Record<string, number> = {
      student: 1,
      staff: 2,
      admin: 3,
    };

    const userLevel = roleHierarchy[user.role];
    const requiredLevel = roleHierarchy[role];

    return userLevel >= requiredLevel;
  };

  const value: AuthContextType = {
    user,
    loading,
    error,
    login,
    signup,
    logout,
    updateUser,
    clearError,
    isAuthenticated: !!user,
    isAdmin: hasRole('admin'),
    isStaff: hasRole('staff'),
    hasRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to use authentication context
 * Must be used within AuthProvider
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}

/**
 * HOC to require authentication for a component
 */
export function withAuth<P extends object>(
  Component: React.ComponentType<P>
): React.ComponentType<P> {
  return function AuthenticatedComponent(props: P) {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
      return <div>Loading...</div>;
    }

    if (!isAuthenticated) {
      // Store intended destination
      sessionStorage.setItem('redirectAfterLogin', window.location.pathname);
      window.location.href = '/login';
      return null;
    }

    return <Component {...props} />;
  };
}

/**
 * HOC to require specific role for a component
 */
export function withRole<P extends object>(
  Component: React.ComponentType<P>,
  requiredRole: 'student' | 'staff' | 'admin'
): React.ComponentType<P> {
  return function RoleProtectedComponent(props: P) {
    const { isAuthenticated, hasRole, loading } = useAuth();

    if (loading) {
      return <div>Loading...</div>;
    }

    if (!isAuthenticated) {
      sessionStorage.setItem('redirectAfterLogin', window.location.pathname);
      window.location.href = '/login';
      return null;
    }

    if (!hasRole(requiredRole)) {
      return (
        <div>
          <h1>Access Denied</h1>
          <p>You do not have permission to access this page.</p>
        </div>
      );
    }

    return <Component {...props} />;
  };
}
