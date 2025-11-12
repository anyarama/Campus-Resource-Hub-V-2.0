# Campus Resource Hub - Frontend Integration Guide

This guide explains how to integrate the React frontend with the Flask backend API. The API client infrastructure is fully implemented and ready to use.

## Table of Contents
- [API Client Architecture](#api-client-architecture)
- [Using API Services](#using-api-services)
- [Authentication Integration](#authentication-integration)
- [Component Integration Examples](#component-integration-examples)
- [Error Handling](#error-handling)
- [Next Steps](#next-steps)

## API Client Architecture

### Overview

The API client is built with a clean, modular architecture:

```
Campus_Resource_hub/src/api/
├── client.ts           # Core HTTP client with interceptors
├── types.ts            # TypeScript interfaces for all entities
├── index.ts            # Central export point
└── services/
    ├── authService.ts      # Authentication & user management
    ├── resourcesService.ts # Resource CRUD operations
    ├── bookingsService.ts  # Booking management
    ├── messagesService.ts  # Messaging functionality
    ├── reviewsService.ts   # Review system
    └── adminService.ts     # Admin operations
```

### Core Features

1. **Automatic Token Management**: Auth tokens are automatically included in requests
2. **Error Handling**: Centralized error handling with user-friendly messages
3. **Type Safety**: Full TypeScript support with comprehensive interfaces
4. **Request Interceptors**: Automatic retry and error handling
5. **Session Management**: Automatic token storage and retrieval

## Using API Services

### Import Pattern

```typescript
// Import specific service
import { authService, resourcesService, bookingsService } from '../api';

// Import types
import type { User, Resource, Booking } from '../api';
```

### Example: Fetching Data

```typescript
import { useState, useEffect } from 'react';
import { resourcesService, type Resource, type PaginatedResponse } from '../api';

function ResourcesList() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchResources() {
      setLoading(true);
      const response = await resourcesService.getResources({
        page: 1,
        per_page: 10,
        type: 'room',
        available: true
      });

      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        setResources(response.data.items);
      }
      
      setLoading(false);
    }

    fetchResources();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {resources.map(resource => (
        <div key={resource.id}>{resource.name}</div>
      ))}
    </div>
  );
}
```

## Authentication Integration

### Login Component Example

```typescript
// Campus_Resource_hub_login/src/components/AuthLogin.tsx
import { useState } from 'react';
import { authService, type LoginCredentials } from '../api';

function LoginForm() {
  const [credentials, setCredentials] = useState<LoginCredentials>({
    email: '',
    password: '',
    remember_me: false
  });
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const response = await authService.login(credentials);

    if (response.error) {
      setError(response.error);
    } else if (response.data?.user) {
      // Login successful - redirect to dashboard
      window.location.href = '/dashboard';
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        value={credentials.email}
        onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={credentials.password}
        onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
        placeholder="Password"
        required
      />
      <label>
        <input
          type="checkbox"
          checked={credentials.remember_me}
          onChange={(e) => setCredentials({ ...credentials, remember_me: e.target.checked })}
        />
        Remember me
      </label>
      {error && <div className="error">{error}</div>}
      <button type="submit">Login</button>
    </form>
  );
}
```

### Protected Route Guard

```typescript
// Campus_Resource_hub/src/components/ProtectedRoute.tsx
import { authService } from '../api';
import { Navigate } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

function ProtectedRoute({ children, requireAdmin = false }: ProtectedRouteProps) {
  const isAuthenticated = authService.isAuthenticated();
  const isAdmin = authService.isAdmin();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && !isAdmin) {
    return <div>Access Denied - Admin privileges required</div>;
  }

  return <>{children}</>;
}
```

### Session Management in App.tsx

```typescript
// Campus_Resource_hub/src/App.tsx
import { useEffect, useState } from 'react';
import { authService, type User } from './api';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      // Try to get user from storage first
      const storedUser = authService.getUserFromStorage();
      
      if (storedUser) {
        setUser(storedUser);
        
        // Verify with backend
        const response = await authService.getCurrentUser();
        if (response.data) {
          setUser(response.data);
        } else if (response.error) {
          // Token expired or invalid
          authService.logout();
          setUser(null);
        }
      }
      
      setLoading(false);
    }

    checkAuth();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      {user ? (
        <DashboardLayout user={user} />
      ) : (
        <LoginPage />
      )}
    </div>
  );
}
```

## Component Integration Examples

### Resources Page Integration

```typescript
// Campus_Resource_hub/src/components/pages/Resources.tsx
import { useState, useEffect } from 'react';
import { resourcesService, type Resource, type ResourceFilters } from '../../api';
import { ResourceCard } from '../ResourceCard';

function Resources() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [filters, setFilters] = useState<ResourceFilters>({
    page: 1,
    per_page: 12,
    type: undefined,
    available: undefined,
    search: ''
  });
  const [loading, setLoading] = useState(false);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    async function fetchResources() {
      setLoading(true);
      const response = await resourcesService.getResources(filters);
      
      if (response.data) {
        setResources(response.data.items);
        setTotalPages(response.data.total_pages);
      }
      
      setLoading(false);
    }

    fetchResources();
  }, [filters]);

  const handleSearch = (query: string) => {
    setFilters({ ...filters, search: query, page: 1 });
  };

  const handleTypeFilter = (type: string) => {
    setFilters({ ...filters, type, page: 1 });
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Search resources..."
        onChange={(e) => handleSearch(e.target.value)}
      />
      
      <select onChange={(e) => handleTypeFilter(e.target.value)}>
        <option value="">All Types</option>
        <option value="room">Rooms</option>
        <option value="equipment">Equipment</option>
        <option value="facility">Facilities</option>
      </select>

      {loading ? (
        <div>Loading...</div>
      ) : (
        <div className="resources-grid">
          {resources.map(resource => (
            <ResourceCard key={resource.id} resource={resource} />
          ))}
        </div>
      )}

      <Pagination 
        currentPage={filters.page || 1}
        totalPages={totalPages}
        onPageChange={(page) => setFilters({ ...filters, page })}
      />
    </div>
  );
}
```

### Create Booking Component

```typescript
// Campus_Resource_hub/src/components/BookingForm.tsx
import { useState } from 'react';
import { bookingsService, type BookingFormData } from '../api';
import { toast } from 'sonner';

interface BookingFormProps {
  resourceId: number;
  onSuccess?: () => void;
}

function BookingForm({ resourceId, onSuccess }: BookingFormProps) {
  const [formData, setFormData] = useState<BookingFormData>({
    resource_id: resourceId,
    start_time: '',
    end_time: '',
    purpose: '',
    notes: '',
    attendees_count: 1
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    const response = await bookingsService.createBooking(formData);

    if (response.error) {
      toast.error(response.error);
    } else if (response.data) {
      toast.success('Booking created successfully!');
      onSuccess?.();
    }

    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="datetime-local"
        value={formData.start_time}
        onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
        required
      />
      <input
        type="datetime-local"
        value={formData.end_time}
        onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
        required
      />
      <input
        type="text"
        placeholder="Purpose"
        value={formData.purpose}
        onChange={(e) => setFormData({ ...formData, purpose: e.target.value })}
      />
      <textarea
        placeholder="Additional notes"
        value={formData.notes}
        onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
      />
      <input
        type="number"
        min="1"
        placeholder="Number of attendees"
        value={formData.attendees_count}
        onChange={(e) => setFormData({ ...formData, attendees_count: parseInt(e.target.value) })}
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create Booking'}
      </button>
    </form>
  );
}
```

### Admin Analytics Dashboard

```typescript
// Campus_Resource_hub/src/components/pages/AdminAnalytics.tsx
import { useState, useEffect } from 'react';
import { adminService, type SystemAnalytics } from '../../api';
import { ChartCard  } from '../ChartCard';
import { KPICard } from '../KPICard';

function AdminAnalytics() {
  const [analytics, setAnalytics] = useState<SystemAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAnalytics() {
      const response = await adminService.getAnalytics();
      
      if (response.data) {
        setAnalytics(response.data);
      }
      
      setLoading(false);
    }

    fetchAnalytics();
  }, []);

  if (loading || !analytics) {
    return <div>Loading analytics...</div>;
  }

  return (
    <div className="analytics-dashboard">
      <div className="kpi-grid">
        <KPICard
          title="Total Users"
          value={analytics.total_users}
          icon="users"
        />
        <KPICard
          title="Total Resources"
          value={analytics.total_resources}
          icon="resources"
        />
        <KPICard
          title="Active Bookings"
          value={analytics.active_bookings}
          icon="calendar"
        />
        <KPICard
          title="Average Rating"
          value={analytics.avg_rating.toFixed(1)}
          icon="star"
        />
      </div>

      <div className="charts-grid">
        <ChartCard
          title="User Breakdown"
          data={analytics.user_breakdown}
          type="pie"
        />
        <ChartCard
          title="Resource Types"
          data={analytics.resource_breakdown}
          type="bar"
        />
        <ChartCard
          title="Booking Status"
          data={analytics.booking_status_breakdown}
          type="doughnut"
        />
      </div>
    </div>
  );
}
```

## Error Handling

### Global Error Handler

```typescript
// Campus_Resource_hub/src/utils/errorHandler.ts
import { toast } from 'sonner';
import type { ApiResponse } from '../api';

export function handleApiError<T>(response: ApiResponse<T>): boolean {
  if (response.error) {
    // Show user-friendly error message
    toast.error(response.error);

    // Log to console for debugging
    console.error('API Error:', {
      error: response.error,
      status: response.status,
      message: response.message
    });

    return true; // Error occurred
  }

  return false; // No error
}

// Usage in components:
const response = await resourcesService.getResource(id);
if (handleApiError(response)) {
  return; // Stop execution if error
}
// Continue with response.data
```

### Network Error Detection

```typescript
function detectNetworkError(status: number): string {
  if (status === 0) {
    return 'Network error. Please check your internet connection.';
  }
  if (status === 401) {
    return 'Session expired. Please log in again.';
  }
  if (status === 403) {
    return 'You do not have permission to perform this action.';
  }
  if (status === 404) {
    return 'The requested resource was not found.';
  }
  if (status >= 500) {
    return 'Server error. Please try again later.';
  }
  return 'An unexpected error occurred.';
}
```

## Next Steps

### Phase 3: Complete Authentication Integration

1. **Connect Login/Signup Pages** ✅ (Examples provided above)
   - Update `Campus_Resource_hub_login/src/components/AuthLogin.tsx`
   - Update `Campus_Resource_hub_login/src/components/AuthSignUp.tsx`

2. **Implement Session Management**
   - Add user context provider
   - Implement logout functionality
   - Handle token expiration

3. **Add Protected Route Guards**
   - Create `ProtectedRoute` component
   - Wrap protected pages
   - Implement role-based guards

### Phase 4: Complete Feature Integration

1. **Resources Page** ✅ (Example provided above)
   - Replace mock data with API calls
   - Add search and filtering
   - Implement pagination

2. **Bookings Page** ✅ (Example provided above)
   - Connect to bookings API
   - Add booking creation form
   - Implement booking management (cancel, update)

3. **Admin Dashboard** ✅ (Example provided above)
   - Connect to admin analytics API
   - Fetch real-time data
   - Add user management functionality

4. **Messages & Reviews**
   - Integrate messaging functionality
   - Add review submission
   - Display reviews for resources

### Phase 7: Testing & Verification

1. **Start Backend Server**
   ```bash
   cd backend
   python -m flask run
   ```

2. **Start Frontend Dev Server**
   ```bash
   cd Campus_Resource_hub
   npm run dev
   ```

3. **Test Each Feature**
   - Login/logout flows
   - Resource browsing
   - Booking creation
   - Admin operations
   - Error scenarios

4. **Browser Testing**
   - Chrome DevTools Network tab
   - Check API requests/responses
   - Verify CORS is working
   - Test authentication persistence

## API Service Reference

### Authentication Service
```typescript
authService.login(credentials)
authService.signup(data)
authService.logout()
authService.getCurrentUser()
authService.updateProfile(data)
authService.changePassword(data)
authService.isAuthenticated()
authService.hasRole('admin')
authService.isAdmin()
authService.isStaff()
```

### Resources Service
```typescript
resourcesService.getResources(filters)
resourcesService.getResource(id)
resourcesService.createResource(data)
resourcesService.updateResource(id, data)
resourcesService.deleteResource(id)
resourcesService.uploadResourceImage(id, file)
resourcesService.getAvailableSlots(id, date)
```

### Bookings Service
```typescript
bookingsService.getBookings(filters)
bookingsService.getMyBookings(filters)
bookingsService.getBooking(id)
bookingsService.createBooking(data)
bookingsService.updateBooking(id, data)
bookingsService.cancelBooking(id)
bookingsService.confirmBooking(id)
bookingsService.completeBooking(id)
```

### Messages Service
```typescript
messagesService.getThreads(params)
messagesService.getThreadMessages(threadId, params)
messagesService.sendMessage(data)
messagesService.markMessageAsRead(id)
messagesService.markThreadAsRead(threadId)
messagesService.getUnreadCount()
```

### Reviews Service
```typescript
reviewsService.getReviews(filters)
reviewsService.getResourceReviews(resourceId, params)
reviewsService.getReview(id)
reviewsService.createReview(data)
reviewsService.updateReview(id, data)
reviewsService.deleteReview(id)
reviewsService.flagReview(id)
```

### Admin Service
```typescript
adminService.getAnalytics()
adminService.getUsers(filters)
adminService.updateUserRole(userId, role)
adminService.updateUserStatus(userId, status)
adminService.getAdminResources(params)
adminService.getFlaggedReviews(params)
adminService.hideReview(reviewId)
adminService.unhideReview(reviewId)
adminService.getActivityReport(params)
```

## Debugging Tips

1. **Check API Base URL**
   ```typescript
   console.log(import.meta.env.VITE_API_BASE_URL);
   ```

2. **Inspect Network Requests**
   - Open Chrome DevTools → Network tab
   - Filter by "Fetch/XHR"
   - Check request headers and response data

3. **Verify CORS Configuration**
   - Check backend `.env` CORS_ORIGINS includes your frontend URL
   - Verify preflight OPTIONS requests succeed

4. **Test Authentication**
   ```typescript
   // In browser console
   sessionStorage.getItem('auth_token')
   sessionStorage.getItem('user')
   ```

## Resources

- **Backend API Documentation**: `/backend/API_DOCUMENTATION.md`
- **Deployment Guide**: `/DEPLOYMENT.md`
- **TypeScript Types**: `/Campus_Resource_hub/src/api/types.ts`

---

**Last Updated**: January 2025  
**Ready for Integration**: All API services implemented and documented
