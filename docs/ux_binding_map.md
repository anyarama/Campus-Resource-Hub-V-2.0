# UX Binding Map

**Document Purpose:** Screen-by-screen mapping of UI components to backend API endpoints, showing current integration status and required bindings.

**Status Legend:**
- ✅ = Backend endpoint exists
- ❌ = Not integrated (UI exists but not calling API)
- 🚫 = Missing (No backend endpoint)
- 📝 = Partially integrated

---

## 1. Authentication Flow (Login App)

### 1.1 Login Screen (`Campus_Resource_hub_login/src/components/AuthLogin.tsx`)

| UI Element | Action | Method | Endpoint | Request Schema | Response Schema | Auth | Status |
|------------|--------|--------|----------|----------------|-----------------|------|--------|
| Email input | Form field | - | - | - | - | Public | ✅ |
| Password input | Form field | - | - | - | - | Public | ✅ |
| "Login" button | Submit login | POST | `/api/auth/login` | `{email, password}` | `{user: User, message}` | Public | ❌ |
| "Forgot password?" link | Navigate | - | - | - | - | Public | 🚫 |

**Current Code (Lines 48-52):**
```typescript
const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault();
  console.log('Login attempt:', { email, password });
  // TODO: Integrate with backend API
};
```

**Required Integration:**
```typescript
import { login } from '../api/services/authService';

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  const response = await login(email, password);
  if (response.success) {
    // Store session cookie (automatic via credentials: 'include')
    window.location.href = '/dashboard';
  } else {
    setError(response.message);
  }
};
```

### 1.2 Sign Up Screen (`Campus_Resource_hub_login/src/components/AuthSignUp.tsx`)

| UI Element | Action | Method | Endpoint | Request Schema | Response Schema | Auth | Status |
|------------|--------|--------|----------|----------------|-----------------|------|--------|
| Full name input | Form field | - | - | - | - | Public | ✅ |
| Email input | Form field | - | - | - | - | Public | ✅ |
| Password input | Form field | - | - | - | - | Public | ✅ |
| Confirm password | Form field | - | - | - | - | Public | ✅ |
| Role selector | Form field | - | - | - | - | Public | ✅ |
| "Sign Up" button | Submit registration | POST | `/api/auth/register` | `{name, email, password, role}` | `{user: User, message}` | Public | ❌ |

**Required Integration:** Similar to login - use `register()` from authService.

---

## 2. Dashboard Screen (`Campus_Resource_hub/src/components/pages/Dashboard.tsx`)

### 2.1 KPI Cards (Lines 40-67 - Hardcoded)

| UI Element | Data Source | Method | Endpoint | Response Schema | Auth | Status |
|------------|-------------|--------|----------|-----------------|------|--------|
| Total Bookings KPI | Mock data | GET | `/api/bookings/my-bookings?status=all` | `{bookings: Booking[], total, pagination}` | Student+ | ❌ |
| Active Users KPI | Mock data | GET | `/api/admin/analytics` | `{metrics: {active_users, ...}}` | Admin | ❌ |
| Resources KPI | Mock data | GET | `/api/resources?status=active` | `{resources: [], total}` | Student+ | ❌ |
| Utilization KPI | Mock data | GET | `/api/admin/analytics` | `{metrics: {utilization_rate, ...}}` | Admin | ❌ |

### 2.2 Charts Section

| UI Element | Data Source | Method | Endpoint | Response Schema | Auth | Status |
|------------|-------------|--------|----------|-----------------|------|--------|
| Bookings Over Time chart | Hardcoded `bookingsData` | GET | `/api/admin/analytics?metric=bookings&period=monthly` | `{data: [{month, count}]}` | Admin | ❌ |
| Category Breakdown chart | Hardcoded `categoryData` | GET | `/api/admin/analytics?metric=category_distribution` | `{data: [{category, count}]}` | Admin | ❌ |

### 2.3 Upcoming Bookings List (Lines 113-172 - Hardcoded)

| UI Element | Action | Method | Endpoint | Request/Response | Auth | Status |
|------------|--------|--------|----------|------------------|------|--------|
| Booking cards list | Load on mount | GET | `/api/bookings/my-bookings?status=approved&upcoming=true` | `{bookings: Booking[]}` | Student+ | ❌ |
| "Book Now" button | Navigate to resources | - | - | - | Student+ | ✅ |
| "View All" button | Navigate to My Bookings | - | - | - | Student+ | ✅ |

### 2.4 Recent Activity List (Lines 141-199 - Hardcoded)

| UI Element | Data Source | Method | Endpoint | Response Schema | Auth | Status |
|------------|-------------|--------|----------|-----------------|------|--------|
| Activity feed | Hardcoded array | GET | `/api/admin/activity?limit=6` | `{activities: Activity[]}` | Admin | 🚫 |

**Gap:** No `/api/admin/activity` endpoint exists. Need to create or aggregate from bookings/reviews/messages.

---

## 3. Resources Screen (`Campus_Resource_hub/src/components/pages/Resources.tsx`)

### 3.1 Resource Grid (Lines 48-117 - Hardcoded Array)

| UI Element | Action | Method | Endpoint | Request/Response | Auth | Status |
|------------|--------|--------|----------|------------------|------|--------|
| Resource grid | Load on mount | GET | `/api/resources` | `{resources: Resource[], pagination}` | Student+ | ❌ |
| Resource card image | Display | - | Use `resource.images[0]` from response | - | Student+ | ✅ |
| Resource card - View button | Open detail page | GET | `/api/resources/{id}` | `{resource: Resource}` | Student+ | ❌ |
| Resource card - Edit button | Open edit modal | GET | `/api/resources/{id}` | `{resource: Resource}` | Staff+ | ❌ |
| Resource card - Duplicate | Duplicate resource | POST | `/api/resources` | Request: `{...resourceData}` | Staff+ | ❌ |

**Current Code (Line 48):**
```typescript
const resources = [
  {
    id: 1,
    image: 'https://images.unsplash.com/...',
    category: 'Library',
    // ... 9 hardcoded resources
  }
];
```

**Required Integration:**
```typescript
import { getResources } from '../api/services/resourcesService';

useEffect(() => {
  const fetchResources = async () => {
    const response = await getResources(filters);
    if (response.success) {
      setResources(response.data.resources);
    }
  };
  fetchResources();
}, [filters]);
```

### 3.2 Search & Filters

| UI Element | Action | Method | Endpoint | Request Schema | Response | Auth | Status |
|------------|--------|--------|----------|----------------|----------|------|--------|
| Search input | Debounced search | GET | `/api/resources?search={query}` | Query param: `search` | `{resources: [], pagination}` | Student+ | ❌ |
| Category checkboxes | Filter by category | GET | `/api/resources?category={cat}` | Query param: `category` | `{resources: [], pagination}` | Student+ | ❌ |
| Location dropdown | Filter by location | GET | `/api/resources?location={loc}` | Query param: `location` | `{resources: [], pagination}` | Student+ | ❌ |
| Availability toggle | Show only available | GET | `/api/resources?available=true` | Query param: `available` | `{resources: [], pagination}` | Student+ | ❌ |
| Min rating filter | Filter by rating | GET | `/api/resources?min_rating={rating}` | Query param: `min_rating` | `{resources: [], pagination}` | Student+ | ❌ |
| "Create Resource" button | Open create modal | POST | `/api/resources` | `{name, category, location, ...}` | `{resource: Resource}` | Staff+ | ❌ |

**API Service Status:** ✅ `resourcesService.ts` has all methods defined (getResources, createResource, etc.) but **NOT CALLED** in components.

---

## 4. My Bookings Screen (`Campus_Resource_hub/src/components/pages/MyBookings.tsx`)

### 4.1 Upcoming Tab (Lines 31-92 - Hardcoded)

| UI Element | Action | Method | Endpoint | Request/Response | Auth | Status |
|------------|--------|--------|----------|------------------|------|--------|
| Upcoming bookings list | Load on mount | GET | `/api/bookings/my-bookings?status=approved&upcoming=true` | `{bookings: Booking[]}` | Student+ | ❌ |
| "Message" button | Open message thread | GET/POST | `/api/messages?thread_id=...` | `{messages: Message[]}` | Student+ | ❌ |
| "Cancel" button | Cancel booking | DELETE | `/api/bookings/{id}` | `{message}` | Student+ | ❌ |

### 4.2 Pending Tab

| UI Element | Action | Method | Endpoint | Request/Response | Auth | Status |
|------------|--------|--------|----------|------------------|------|--------|
| Pending bookings list | Load on mount | GET | `/api/bookings/my-bookings?status=pending` | `{bookings: Booking[]}` | Student+ | ❌ |

### 4.3 Past Tab

| UI Element | Action | Method | Endpoint | Request/Response | Auth | Status |
|------------|--------|--------|----------|------------------|------|--------|
| Past bookings list | Load on mount | GET | `/api/bookings/my-bookings?status=approved&past=true` | `{bookings: Booking[]}` | Student+ | ❌ |
| "Book Again" button | Navigate to resource | GET | `/api/resources/{id}` | `{resource: Resource}` | Student+ | ❌ |

### 4.4 Cancelled/Rejected Tab

| UI Element | Action | Method | Endpoint | Request/Response | Auth | Status |
|------------|--------|--------|----------|------------------|------|--------|
| Cancelled/rejected list | Load on mount | GET | `/api/bookings/my-bookings?status=cancelled,rejected` | `{bookings: Booking[]}` | Student+ | ❌ |

**Current Code (Line 31):**
```typescript
const bookings: Booking[] = [
  {
    id: 1,
    resourceName: 'Wells Library - Study Room 3A',
    // ... hardcoded bookings
  }
];
```

**Required Integration:**
```typescript
import { getMyBookings } from '../api/services/bookingsService';

useEffect(() => {
  const fetchBookings = async () => {
    const response = await getMyBookings({ status: activeTab });
    if (response.success) {
      setBookings(response.data.bookings);
    }
  };
  fetchBookings();
}, [activeTab]);
```

---

## 5. Messages Screen (App.tsx Lines 179-186 - Placeholder)

| UI Element | Action | Method | Endpoint | Request/Response | Auth | Status |
|------------|--------|--------|----------|------------------|------|--------|
| Thread list | Load on mount | GET | `/api/messages/threads` | `{threads: Thread[]}` | Student+ | 🚫 |
| Message list | Load thread | GET | `/api/messages?thread_id={id}` | `{messages: Message[]}` | Student+ | ❌ |
| Send message | Send | POST | `/api/messages` | `{recipient_id, content, thread_id}` | Student+ | ❌ |
| Mark as read | Update | PATCH | `/api/messages/{id}/read` | `{message}` | Student+ | ❌ |

**Current State:** Placeholder only - "Messages feature coming soon..."

**Gap:** `/api/messages/threads` endpoint missing. Backend has individual message CRUD but no thread aggregation endpoint.

---

## 6. Reviews Screen (App.tsx Lines 187-194 - Placeholder)

| UI Element | Action | Method | Endpoint | Request/Response | Auth | Status |
|------------|--------|--------|----------|------------------|------|--------|
| Review list | Load on mount | GET | `/api/reviews?user_id={current_user}` | `{reviews: Review[]}` | Student+ | ❌ |
| Create review | Submit review | POST | `/api/reviews` | `{resource_id, rating, comment}` | Student+ | ❌ |
| Edit review | Update | PUT | `/api/reviews/{id}` | `{rating, comment}` | Student+ | ❌ |
| Delete review | Delete | DELETE | `/api/reviews/{id}` | `{message}` | Student+ | ❌ |
| Flag review | Report | POST | `/api/reviews/{id}/flag` | `{reason}` | Student+ | ❌ |

**Current State:** Placeholder only - "Reviews feature coming soon..."

---

## 7. Admin - Users Screen (`Campus_Resource_hub/src/components/pages/AdminUsers.tsx`)

| UI Element | Action | Method | Endpoint | Request/Response | Auth | Status |
|------------|--------|--------|----------|------------------|------|--------|
| Users table | Load on mount | GET | `/api/admin/users` | `{users: User[], pagination}` | Admin | ❌ |
| Search users | Search | GET | `/api/admin/users?search={query}` | `{users: User[]}` | Admin | ❌ |
| Filter by role | Filter | GET | `/api/admin/users?role={role}` | `{users: User[]}` | Admin | ❌ |
| Change role | Update | PUT | `/api/admin/users/{id}/role` | `{role}` Response: `{user: User}` | Admin | ❌ |
| Change status | Update | PUT | `/api/admin/users/{id}/status` | `{status}` Response: `{user: User}` | Admin | ❌ |

---

## 8. Admin - Analytics Screen (`Campus_Resource_hub/src/components/pages/AdminAnalytics.tsx`)

| UI Element | Action | Method | Endpoint | Request/Response | Auth | Status |
|------------|--------|--------|----------|------------------|------|--------|
| KPI cards | Load on mount | GET | `/api/admin/analytics` | `{metrics: {bookings, users, resources, utilization}}` | Admin | ❌ |
| Date range filter | Apply filter | GET | `/api/admin/analytics?start={date}&end={date}` | `{metrics, charts}` | Admin | ❌ |
| Usage by Category chart | Load on mount | GET | `/api/admin/analytics?metric=category` | `{data: [{category, count}]}` | Admin | ❌ |
| Trend chart | Load on mount | GET | `/api/admin/analytics?metric=trends` | `{data: [{date, bookings, users}]}` | Admin | ❌ |
| Download chart | Export | - | Client-side Chart.js export | - | Admin | ✅ |

**Backend Endpoint:** ✅ `/api/admin/analytics` exists (lines in `backend/routes/admin.py`)

---

## 9. Admin - Moderation Screen (`Campus_Resource_hub/src/components/pages/AdminModeration.tsx`)

| UI Element | Action | Method | Endpoint | Request/Response | Auth | Status |
|------------|--------|--------|----------|------------------|------|--------|
| Flagged reviews list | Load on mount | GET | `/api/admin/reviews?flagged=true` | `{reviews: Review[]}` | Admin | ❌ |
| Approve review | Unflag | PUT | `/api/admin/reviews/{id}/approve` | `{review: Review}` | Admin | ❌ |
| Hide review | Moderate | PUT | `/api/admin/reviews/{id}/hide` | `{review: Review}` | Admin | ❌ |
| Delete review | Delete | DELETE | `/api/reviews/{id}` | `{message}` | Admin | ❌ |

**Backend Endpoints:** ✅ All exist in `backend/routes/admin.py` and `backend/routes/reviews.py`

---

## 10. AI Features (Missing from UI)

### 10.1 AI Concierge (AiDD Requirement)

| UI Element | Action | Method | Endpoint | Request/Response | Auth | Status |
|------------|--------|--------|----------|------------------|------|--------|
| Chat interface | Send query | POST | `/api/ai/concierge` | `{query}` Response: `{response, suggestions}` | Student+ | 🚫 |

**Status:** 🚫 No UI component, no backend endpoint

### 10.2 AI Scheduler (AiDD Requirement)

| UI Element | Action | Method | Endpoint | Request/Response | Auth | Status |
|------------|--------|--------|----------|------------------|------|--------|
| Smart booking interface | Get suggestions | POST | `/api/ai/schedule` | `{resource_id, preferences}` Response: `{suggested_slots}` | Student+ | 🚫 |

**Status:** 🚫 No UI component, no backend endpoint

---

## Integration Priority Matrix

### P0 - Critical (Core Functionality)

1. **Authentication Flow** - `/api/auth/login`, `/api/auth/register`
2. **Resources Browse** - `/api/resources` (GET with filters)
3. **My Bookings** - `/api/bookings/my-bookings`
4. **Resource Detail** - `/api/resources/{id}`
5. **Create Booking** - `/api/bookings` (POST)

### P1 - High Priority

6. **Cancel Booking** - `/api/bookings/{id}` (DELETE)
7. **User Profile** - `/api/auth/me` (GET/PATCH)
8. **Create Resource** - `/api/resources` (POST) [Staff only]
9. **Admin Users Table** - `/api/admin/users`
10. **Admin Analytics** - `/api/admin/analytics`

### P2 - Medium Priority

11. **Reviews CRUD** - `/api/reviews/*`
12. **Messages** - `/api/messages/*`
13. **Admin Moderation** - `/api/admin/reviews/*`
14. **Resource Availability Check** - `/api/bookings/check-availability`

### P3 - Low Priority (Nice to Have)

15. **Activity Feed** - `/api/admin/activity` (needs creation)
16. **Forgot Password** - `/api/auth/forgot-password` (needs creation)
17. **Message Thread Aggregation** - `/api/messages/threads` (needs creation)

### P4 - Future (AiDD Requirements)

18. **AI Concierge** - `/api/ai/concierge` (needs full creation)
19. **AI Scheduler** - `/api/ai/schedule` (needs full creation)

---

## Error Handling Requirements

Each API call in components must handle:

1. **Loading states** - Show skeletons/spinners
2. **Success states** - Update UI, show toast notification
3. **Error states** - Show error message, maintain form state
4. **Network errors** - Retry logic, offline indicator
5. **Auth errors** - Redirect to login on 401
6. **Validation errors** - Display field-level errors

**Example Pattern:**
```typescript
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);

const handleAction = async () => {
  setLoading(true);
  setError(null);
  
  const response = await apiCall();
  
  if (response.success) {
    toast.success(response.message);
    // Update local state
  } else {
    setError(response.message);
    toast.error(response.message);
  }
  
  setLoading(false);
};
```

---

## State Management Recommendations

### Global State (Context/Store)

- **AuthContext** - Current user, session status
- **ThemeContext** - Dark mode preference (✅ already exists)

### Local State (Component)

- Resource list, filters, search
- Booking list per tab
- Form data, validation errors
- Loading/error states per API call

### URL State (Query Params)

- Pagination (page, limit)
- Filters (category, location, rating)
- Search query
- Active tab

---

## API Client Configuration Status

**File:** `Campus_Resource_hub/src/api/client.ts`

✅ **Exists:** ApiClient class with methods (get, post, put, delete, upload)
✅ **Session-based auth:** Uses `credentials: 'include'`
✅ **Base URL:** Configurable via env var
❌ **Error handling:** Not wired to toast notifications
❌ **Auth redirect:** No 401 → login redirect
❌ **Retry logic:** Not implemented

**Required Updates:**
```typescript
// Add global error handler
private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
  if (response.status === 401) {
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }
  
  const data = await response.json();
  
  if (!response.ok) {
    toast.error(data.message || 'An error occurred');
  }
  
  return data;
}
```

---

## Summary

**Total UI Screens:** 10 (excluding placeholders)
**Total Backend Endpoints in OpenAPI:** 47 existing + 2 missing (AI)
**Integration Status:**
- ❌ Not integrated: 45/47 endpoints (96%)
- ✅ Integrated: 0/47 endpoints (0%)
- 🚫 Missing endpoints: 4 (threads, activity, forgot-password, 2× AI)

**Critical Gap:** Despite having a fully functional backend with 47 endpoints, **ZERO endpoints are integrated** in the frontend. All data is hardcoded arrays in component files.

**Next Steps:** Implement integration in priority order (P0 → P1 → P2 → P3 → P4).
