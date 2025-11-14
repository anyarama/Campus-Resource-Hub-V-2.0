# Campus Resource Hub - API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:5000`  
**Total Endpoints:** 49

---

## Table of Contents

1. [Security Overview](#security-overview)
2. [Authentication](#authentication)
3. [Resources Management](#resources-management)
4. [Bookings System](#bookings-system)
5. [Messaging System](#messaging-system)
6. [Reviews System](#reviews-system)
7. [Admin Dashboard](#admin-dashboard)
8. [Health Check](#health-check)
9. [Error Codes](#error-codes)
10. [Security Requirements](#security-requirements)

---

## Security Overview

### 🔒 Security Status: PRODUCTION-READY

All API endpoints are protected by multiple layers of security implemented in Phase 0:

| Security Feature | Status | Documentation |
|------------------|--------|---------------|
| **CSRF Protection** | ✅ Active | All POST/PUT/PATCH/DELETE require `X-CSRF-Token` header |
| **Rate Limiting** | ✅ Active | Endpoint-specific limits prevent abuse |
| **Security Headers** | ✅ Active | CSP, HSTS, X-Frame-Options, etc. |
| **Session Security** | ✅ Active | HTTPOnly, Secure cookies (production) |
| **Input Validation** | ✅ Active | All inputs sanitized and validated |
| **Audit Logging** | ✅ Active | Security events logged |

**📖 Detailed Security Guide:** See `docs/API_SECURITY_GUIDE.md` for comprehensive security documentation.

### Quick Security Checklist

Before making API requests, ensure you:
- ✅ Use HTTPS in production
- ✅ Obtain CSRF token from `/api/auth/csrf-token`
- ✅ Include `X-CSRF-Token` header in all state-changing requests
- ✅ Handle rate limit errors (429) gracefully
- ✅ Store session cookies securely (HTTPOnly)
- ✅ Never expose credentials in logs or error messages

---

## Authentication

All authenticated endpoints require a valid session cookie. Login first to receive the session.

### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123",
  "role": "student",
  "department": "Computer Science"
}

Response: 201 Created
{
  "message": "User registered successfully",
  "user": { ... }
}
```

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePassword123"
}

Response: 200 OK
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "student"
  }
}
```

### Get Current User
```http
GET /api/auth/me
Authorization: Required (Session Cookie)

Response: 200 OK
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "student",
  "status": "active"
}
```

### Update Profile
```http
PATCH /api/auth/me
Authorization: Required
Content-Type: application/json

{
  "name": "John Smith",
  "department": "Engineering"
}

Response: 200 OK
```

### Change Password
```http
POST /api/auth/change-password
Authorization: Required
Content-Type: application/json

{
  "current_password": "OldPassword123",
  "new_password": "NewPassword456"
}

Response: 200 OK
```

### Logout
```http
POST /api/auth/logout
Authorization: Required

Response: 200 OK
```

### Check Email Availability
```http
POST /api/auth/check-email
Content-Type: application/json

{
  "email": "test@example.com"
}

Response: 200 OK
{
  "available": true
}
```

---

## Resources Management

### List Resources
```http
GET /api/resources?status=published&category=study_room&page=1&per_page=20

Response: 200 OK
{
  "resources": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 50,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

### Get Single Resource
```http
GET /api/resources/1

Response: 200 OK
{
  "id": 1,
  "title": "Study Room A",
  "description": "Quiet study room...",
  "category": "study_room",
  "location": "Library, 2nd Floor",
  "capacity": 8,
  "status": "published",
  "average_rating": 4.5,
  "review_count": 12
}
```

### Create Resource
```http
POST /api/resources
Authorization: Required
Content-Type: application/json

{
  "title": "Study Room B",
  "description": "Spacious study room with whiteboard",
  "category": "study_room",
  "location": "Library, 3rd Floor",
  "capacity": 10,
  "requires_approval": true,
  "status": "draft"
}

Response: 201 Created
```

### Update Resource
```http
PUT /api/resources/1
Authorization: Required (Owner or Admin)
Content-Type: application/json

{
  "title": "Updated Title",
  "capacity": 12
}

Response: 200 OK
```

### Delete Resource
```http
DELETE /api/resources/1
Authorization: Required (Owner or Admin)

Response: 200 OK
```

### Publish Resource
```http
POST /api/resources/1/publish
Authorization: Required (Owner or Admin)

Response: 200 OK
```

### Search Resources
```http
GET /api/resources/search?q=study&category=study_room

Response: 200 OK
{
  "query": "study",
  "count": 5,
  "results": [...]
}
```

### Get Categories
```http
GET /api/resources/categories

Response: 200 OK
{
  "categories": [
    "study_room",
    "equipment",
    "facility",
    "vehicle",
    "technology",
    "sports",
    "event_space",
    "other"
  ]
}
```

### Get My Resources
```http
GET /api/resources/my-resources?status=published
Authorization: Required

Response: 200 OK
{
  "count": 3,
  "resources": [...]
}
```

### Get Popular Resources
```http
GET /api/resources/popular?limit=10

Response: 200 OK
{
  "count": 10,
  "resources": [...]
}
```

---

## Bookings System

### Create Booking
```http
POST /api/bookings
Authorization: Required
Content-Type: application/json

{
  "resource_id": 1,
  "start_datetime": "2025-01-15T10:00:00Z",
  "end_datetime": "2025-01-15T12:00:00Z",
  "notes": "Need for group study"
}

Response: 201 Created
{
  "message": "Booking created successfully",
  "booking": { ... }
}
```

### List My Bookings
```http
GET /api/bookings?status=pending&page=1&per_page=20
Authorization: Required

Response: 200 OK
{
  "bookings": [...],
  "pagination": { ... }
}
```

### Get Booking Details
```http
GET /api/bookings/1
Authorization: Required

Response: 200 OK
{
  "id": 1,
  "resource_id": 5,
  "status": "pending",
  "start_datetime": "2025-01-15T10:00:00Z",
  "end_datetime": "2025-01-15T12:00:00Z"
}
```

### Approve Booking
```http
POST /api/bookings/1/approve
Authorization: Required (Resource Owner, Staff, or Admin)
Content-Type: application/json

{
  "approval_notes": "Approved for use"
}

Response: 200 OK
```

### Reject Booking
```http
POST /api/bookings/1/reject
Authorization: Required (Resource Owner, Staff, or Admin)
Content-Type: application/json

{
  "rejection_reason": "Resource not available"
}

Response: 200 OK
```

### Cancel Booking
```http
POST /api/bookings/1/cancel
Authorization: Required (Requester, Resource Owner, or Admin)
Content-Type: application/json

{
  "cancellation_reason": "Plans changed"
}

Response: 200 OK
```

### Get Pending Approvals
```http
GET /api/bookings/pending
Authorization: Required (Resource Owner, Staff, or Admin)

Response: 200 OK
{
  "count": 5,
  "bookings": [...]
}
```

### Check Availability
```http
POST /api/bookings/check-availability
Authorization: Required
Content-Type: application/json

{
  "resource_id": 1,
  "start_datetime": "2025-01-15T10:00:00Z",
  "end_datetime": "2025-01-15T12:00:00Z"
}

Response: 200 OK
{
  "available": true,
  "message": "Time slot is available"
}
```

---

## Messaging System

### List Threads
```http
GET /api/messages?page=1&per_page=20
Authorization: Required

Response: 200 OK
{
  "threads": [
    {
      "thread_id": "thread_1_2",
      "other_user_id": 2,
      "latest_message": "Hello...",
      "latest_timestamp": "2025-01-15T10:00:00Z",
      "unread_count": 3
    }
  ],
  "pagination": { ... }
}
```

### Get Thread Messages
```http
GET /api/messages/thread/thread_1_2?page=1&per_page=50
Authorization: Required

Response: 200 OK
{
  "messages": [...],
  "pagination": { ... }
}
```

### Send Message
```http
POST /api/messages
Authorization: Required
Content-Type: application/json

{
  "receiver_id": 2,
  "content": "Hello, is this available?",
  "resource_id": 5
}

Response: 201 Created
```

### Mark Message as Read
```http
PUT /api/messages/1/read
Authorization: Required

Response: 200 OK
```

### Get Unread Count
```http
GET /api/messages/unread-count
Authorization: Required

Response: 200 OK
{
  "unread_count": 5
}
```

### Search Messages
```http
GET /api/messages/search?q=available&limit=50
Authorization: Required

Response: 200 OK
{
  "query": "available",
  "count": 3,
  "messages": [...]
}
```

---

## Reviews System

### Get Resource Reviews
```http
GET /api/reviews/resources/1/reviews?page=1&per_page=20

Response: 200 OK
{
  "reviews": [...],
  "average_rating": 4.5,
  "total_reviews": 12,
  "pagination": { ... }
}
```

### Submit Review
```http
POST /api/reviews
Authorization: Required
Content-Type: application/json

{
  "resource_id": 1,
  "rating": 5,
  "comment": "Excellent resource!",
  "booking_id": 10
}

Response: 201 Created
```

### Update Review
```http
PUT /api/reviews/1
Authorization: Required (Reviewer only, within 7 days)
Content-Type: application/json

{
  "rating": 4,
  "comment": "Updated review"
}

Response: 200 OK
```

### Delete Review
```http
DELETE /api/reviews/1
Authorization: Required (Reviewer or Admin)

Response: 200 OK
```

### Flag Review
```http
POST /api/reviews/1/flag
Authorization: Required

Response: 200 OK
```

### Get My Reviews
```http
GET /api/reviews/my-reviews?page=1&per_page=20
Authorization: Required

Response: 200 OK
{
  "reviews": [...],
  "pagination": { ... }
}
```

---

## Admin Dashboard

### Get System Analytics
```http
GET /api/admin/analytics
Authorization: Required (Admin only)

Response: 200 OK
{
  "users": {
    "total": 150,
    "active": 140,
    "by_role": {
      "students": 120,
      "staff": 25,
      "admins": 5
    },
    "new_this_week": 10
  },
  "resources": { ... },
  "bookings": { ... },
  "messages": { ... },
  "reviews": { ... }
}
```

### List All Users
```http
GET /api/admin/users?role=student&status=active&page=1&per_page=20
Authorization: Required (Admin only)

Response: 200 OK
{
  "users": [...],
  "pagination": { ... }
}
```

### Update User Role
```http
PUT /api/admin/users/1/role
Authorization: Required (Admin only)
Content-Type: application/json

{
  "role": "staff"
}

Response: 200 OK
```

### Update User Status
```http
PUT /api/admin/users/1/status
Authorization: Required (Admin only)
Content-Type: application/json

{
  "status": "suspended"
}

Response: 200 OK
```

### Get Resources for Moderation
```http
GET /api/admin/resources?status=draft&page=1&per_page=20
Authorization: Required (Admin only)

Response: 200 OK
```

### Get Flagged Reviews
```http
GET /api/admin/reviews/flagged?page=1&per_page=20
Authorization: Required (Admin only)

Response: 200 OK
```

### Hide Review
```http
POST /api/admin/reviews/1/hide
Authorization: Required (Admin only)
Content-Type: application/json

{
  "moderation_notes": "Inappropriate content"
}

Response: 200 OK
```

### Unhide Review
```http
POST /api/admin/reviews/1/unhide
Authorization: Required (Admin only)

Response: 200 OK
```

### Get Activity Report
```http
GET /api/admin/reports/activity?days=30
Authorization: Required (Admin only)

Response: 200 OK
{
  "period": "Last 30 days",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-01-31T00:00:00Z",
  "activity": {
    "new_users": 25,
    "new_resources": 40,
    "bookings_created": 120,
    "messages_sent": 450,
    "reviews_submitted": 35
  }
}
```

---

## Health Check

### Get Health Status
```http
GET /api/health

Response: 200 OK
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:00:00Z"
}
```

### Get Database Health
```http
GET /api/health/db

Response: 200 OK
{
  "status": "healthy",
  "database": "connected"
}
```

---

## Error Codes

### Standard HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (e.g., booking overlap) |
| 500 | Internal Server Error | Server error occurred |

### Error Response Format

```json
{
  "error": "Error Type",
  "message": "Detailed error message"
}
```

---

## Authentication & Authorization

### Role Hierarchy
- **Student** - Basic user access
- **Staff** - Enhanced permissions (booking approvals)
- **Admin** - Full system access

### Permission Matrix

| Endpoint | Student | Staff | Admin |
|----------|---------|-------|-------|
| Create Resource | ✅ | ✅ | ✅ |
| Approve Booking | ❌ | ✅ | ✅ |
| Manage Users | ❌ | ❌ | ✅ |
| View Analytics | ❌ | ❌ | ✅ |
| Moderate Content | ❌ | ❌ | ✅ |

---

## Security Requirements

### CSRF Protection 🔒

**Status:** ✅ ACTIVE - All state-changing requests require CSRF tokens

#### 1. Obtain CSRF Token

**Endpoint:** `GET /api/auth/csrf-token`

```bash
curl http://localhost:5000/api/auth/csrf-token
```

**Response:**
```json
{
  "csrf_token": "ImFhY2RlZjEyMzQ1Njc4OTAi..."
}
```

#### 2. Include Token in Requests

All POST, PUT, PATCH, DELETE requests must include the CSRF token in the header:

```bash
curl -X POST http://localhost:5000/api/resources \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: ImFhY2RlZjEyMzQ1Njc4OTAi..." \
  -H "Cookie: session=..." \
  -d '{"title": "New Resource"}'
```

**Alternative Header:** `X-CSRFToken` (both formats accepted)

#### 3. CSRF Error Response

**Missing or Invalid Token:**
```json
{
  "error": "CSRF Validation Failed",
  "message": "CSRF token missing or invalid. Please refresh and try again.",
  "status": 403
}
```

**HTTP Status:** `403 Forbidden`

### Rate Limiting 🚦

**Status:** ✅ ACTIVE - Endpoint-specific limits enforced

| Endpoint | Method | Rate Limit | Purpose |
|----------|--------|------------|---------|
| `/api/auth/register` | POST | 5 per 15 minutes | Prevent account spam |
| `/api/auth/login` | POST | 10 per 15 minutes | Brute force protection |
| `/api/auth/change-password` | POST | 3 per hour | High-sensitivity operation |
| `/api/resources` | POST | 20 per hour | Prevent resource spam |
| `/api/bookings` | POST | 10 per hour | Prevent booking abuse |
| `/api/messages` | POST | 30 per hour | Prevent message spam |
| `/api/reviews` | POST | 5 per hour | Prevent review manipulation |
| `/api/admin/*` | ALL | 100 per hour | Admin operations |
| **All Other Endpoints** | ALL | 50/hour, 200/day | General protection |

#### Rate Limit Headers

All responses include rate limit information:

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1642089600
```

#### Rate Limit Exceeded Response

```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Please try again later.",
  "retry_after": "60 seconds",
  "status": 429
}
```

**HTTP Status:** `429 Too Many Requests`

### Security Headers 🛡️

**Status:** ✅ ACTIVE - All responses include security headers

| Header | Value | Protection |
|--------|-------|------------|
| `Content-Security-Policy` | `default-src 'self'; ...` | XSS, injection attacks |
| `Strict-Transport-Security` | `max-age=31536000` | SSL stripping (prod only) |
| `X-Content-Type-Options` | `nosniff` | MIME sniffing attacks |
| `X-Frame-Options` | `DENY` | Clickjacking |
| `X-XSS-Protection` | `1; mode=block` | Legacy XSS protection |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Privacy protection |

### Session Security 🍪

All session cookies include security flags:

| Flag | Development | Production | Purpose |
|------|-------------|------------|---------|
| `HTTPOnly` | ✅ True | ✅ True | Prevent JavaScript access |
| `Secure` | ❌ False | ✅ True | HTTPS-only transmission |
| `SameSite` | Lax | Strict | CSRF protection |
| `Max-Age` | 30 days | 30 days | "Remember Me" duration |

---

## Pagination

All list endpoints support pagination with the following parameters:
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 20, max: 100)

Response includes pagination metadata:
```json
{
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 50,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## Data Validation

### Bookings
- Minimum duration: 15 minutes
- Maximum duration: 7 days
- Minimum advance time: 30 minutes

### Reviews
- Rating: 1-5 stars (integer)
- Comment: 10-2000 characters (optional)
- Edit window: 7 days

### Messages
- Content: 1-5000 characters
- Cannot message self

---

## Best Practices

1. **Authentication**: Always include session cookie for protected endpoints
2. **Error Handling**: Check response status codes and error messages
3. **Pagination**: Use pagination for list endpoints to improve performance
4. **Datetime Format**: Use ISO 8601 format (e.g., `2025-01-15T10:00:00Z`)
5. **Validation**: Validate data client-side before sending to API

---

## Support

For API issues or questions, contact the development team or refer to the source code repository.

**Last Updated:** 2025-01-12
