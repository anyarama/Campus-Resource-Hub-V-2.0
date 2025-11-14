/**
 * Protected Route Component
 * Wraps routes that require authentication
 * Compatible with custom routing system (no React Router)
 * Note: App.tsx handles redirection logic via useEffect hooks
 */

import React, { ReactNode } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: ReactNode;
  requireRole?: 'student' | 'staff' | 'admin';
  fallback?: ReactNode;
}

/**
 * ProtectedRoute component - requires authentication
 * 
 * Usage:
 * <ProtectedRoute>
 *   <Dashboard />
 * </ProtectedRoute>
 * 
 * With role requirement:
 * <ProtectedRoute requireRole="admin">
 *   <AdminPanel />
 * </ProtectedRoute>
 */
export function ProtectedRoute({ 
  children, 
  requireRole,
  fallback 
}: ProtectedRouteProps) {
  const { isAuthenticated, hasRole, loading } = useAuth();

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-iu-crimson mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If not authenticated, return null - App.tsx will handle redirect to login
  if (!isAuthenticated) {
    return null;
  }

  // Check role requirement if specified
  if (requireRole && !hasRole(requireRole)) {
    return (
      fallback || (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center p-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-4">Access Denied</h1>
            <p className="text-gray-600 mb-6">
              You do not have permission to access this page.
            </p>
            <p className="text-sm text-gray-500">
              Required role: <span className="font-semibold">{requireRole}</span>
            </p>
          </div>
        </div>
      )
    );
  }

  // Render children if authenticated and authorized
  return <>{children}</>;
}

/**
 * Guest Route Component
 * Used for login/signup pages
 * App.tsx handles redirection to dashboard if already authenticated
 */
interface GuestRouteProps {
  children: ReactNode;
}

export function GuestRoute({ children }: GuestRouteProps) {
  const { isAuthenticated, loading } = useAuth();

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-iu-crimson mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If authenticated, return null - App.tsx will handle redirect to dashboard
  if (isAuthenticated) {
    return null;
  }

  // Render children (login/signup pages) if not authenticated
  return <>{children}</>;
}

/**
 * Admin Route Component
 * Convenience component for admin-only routes
 */
interface AdminRouteProps {
  children: ReactNode;
}

export function AdminRoute({ children }: AdminRouteProps) {
  return (
    <ProtectedRoute requireRole="admin" children={children} />
  );
}

/**
 * Staff Route Component
 * Convenience component for staff+ routes (staff and admin)
 */
interface StaffRouteProps {
  children: ReactNode;
}

export function StaffRoute({ children }: StaffRouteProps) {
  return (
    <ProtectedRoute requireRole="staff" children={children} />
  );
}
