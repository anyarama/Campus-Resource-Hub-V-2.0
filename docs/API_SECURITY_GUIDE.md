# Campus Resource Hub - API Security Guide

**Version:** 1.0.0  
**Last Updated:** January 12, 2025  
**Status:** Production-Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [CSRF Protection](#csrf-protection)
4. [Rate Limiting](#rate-limiting)
5. [Security Headers](#security-headers)
6. [Input Validation](#input-validation)
7. [Secret Management](#secret-management)
8. [Error Handling](#error-handling)
9. [Security Best Practices](#security-best-practices)
10. [Compliance & Standards](#compliance--standards)

---

## Overview

The Campus Resource Hub API implements multiple layers of security to protect against common web vulnerabilities and ensure secure operations. All security features have been implemented in Phase 0 and are actively tested.

### Security Status

| Feature | Status | Phase | Priority |
|---------|--------|-------|----------|
| CSRF Protection | ✅ Active | Phase 0 | CRITICAL |
| Rate Limiting | ✅ Active | Phase 0 | CRITICAL |
| Security Headers | ✅ Active | Phase 0 | HIGH |
| Input Validation | ✅ Active | Phase 0 | HIGH |
| Secret Management | ✅ Active | Phase 0 | CRITICAL |
| Session Security | ✅ Active | Phase 0 | HIGH |
| Audit Logging | ✅ Active | Phase 0 | MEDIUM |
| HTTPS Enforcement | ⚠️ Production Only | Phase 0 | CRITICAL |

---

## Authentication & Authorization

### Authentication Method

**Session-Based Authentication** using Flask-Login:
- Secure session cookies with HTTPOnly flag
- SameSite cookie policy (Lax for dev, Strict for production)
- Automatic session timeout after inactivity
- "Remember Me" functionality with secure cookies (30-day expiration)

### Authentication Flow

```
1. User Registration
   POST /api/auth/register
   → Rate Limited: 5 attempts per 15 minutes
   → CSRF Protected
   → Returns: User object + Session cookie

2. User Login
   POST /api/auth/login
   → Rate Limited: 10 attempts per 15 minutes
   → CSRF Protected
   → Returns: User object + Session cookie

3. Authenticated Requests
   All subsequent requests
   → Include session cookie automatically
   → Browser handles cookie storage/transmission

4. Logout
   POST /api/auth/logout
   → Clears session
   → Invalidates session cookie
```

### Authorization Levels

#### Role Hierarchy

```
Admin > Staff > Student
```

#### Permission Matrix

| Resource | Student | Staff | Admin |
|----------|---------|-------|-------|
| **Authentication** |
| Register Account | ✅ | ✅ | ✅ |
| Login | ✅ | ✅ | ✅ |
| View Own Profile | ✅ | ✅ | ✅ |
| Update Own Profile | ✅ | ✅ | ✅ |
| Change Password | ✅ | ✅ | ✅ |
| **Resources** |
| View Published Resources | ✅ | ✅ | ✅ |
| Create Resource | ✅ | ✅ | ✅ |
| Edit Own Resource | ✅ | ✅ | ✅ |
| Delete Own Resource | ✅ | ✅ | ✅ |
| Edit Any Resource | ❌ | ❌ | ✅ |
| Delete Any Resource | ❌ | ❌ | ✅ |
| **Bookings** |
| Create Booking | ✅ | ✅ | ✅ |
| View Own Bookings | ✅ | ✅ | ✅ |
| Approve Bookings | ❌ | ✅ | ✅ |
| Reject Bookings | ❌ | ✅ | ✅ |
| Cancel Own Booking | ✅ | ✅ | ✅ |
| Cancel Any Booking | ❌ | ❌ | ✅ |
| **Messages** |
| Send Messages | ✅ | ✅ | ✅ |
| View Own Messages | ✅ | ✅ | ✅ |
| **Reviews** |
| Submit Review | ✅ | ✅ | ✅ |
| Edit Own Review (7 days) | ✅ | ✅ | ✅ |
| Delete Own Review | ✅ | ✅ | ✅ |
| Flag Review | ✅ | ✅ | ✅ |
| Hide/Unhide Reviews | ❌ | ❌ | ✅ |
| **Admin Functions** |
| View Analytics | ❌ | ❌ | ✅ |
| Manage Users | ❌ | ❌ | ✅ |
| Update User Roles | ❌ | ❌ | ✅ |
| Suspend Users | ❌ | ❌ | ✅ |
| Moderate Content | ❌ | ❌ | ✅ |

### Session Security Configuration

```python
# Development
SESSION_COOKIE_HTTPONLY = True       # Prevents JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'     # CSRF protection
SESSION_COOKIE_SECURE = False        # HTTP allowed in dev

# Production
SESSION_COOKIE_HTTPONLY = True       # Prevents JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'   # Strict CSRF protection
SESSION_COOKIE_SECURE = True         # HTTPS only
```

---

## CSRF Protection

### Implementation

**Library:** Flask-WTF CSRFProtect  
**Status:** ✅ ACTIVE on all state-changing requests

### Configuration

```python
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = 3600  # 1 hour token lifetime
WTF_CSRF_CHECK_DEFAULT = True
WTF_CSRF_METHODS = ['POST', 'PUT', 'DELETE', 'PATCH']
WTF_CSRF_HEADERS = ['X-CSRFToken', 'X-CSRF-Token']
```

### Protected Endpoints

**All state-changing operations require CSRF tokens:**
- POST, PUT, PATCH, DELETE requests
- GET requests are NOT CSRF protected (read-only)

### Usage Workflow

#### 1. Obtain CSRF Token

```bash
GET /api/auth/csrf-token
```

**Response:**
```json
{
  "csrf_token": "ImFhY2RlZjEyMzQ1Njc4OTAi..."
}
```

#### 2. Include Token in Requests

**Header Method (Recommended):**
```bash
curl -X POST https://api.example.com/api/resources \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: ImFhY2RlZjEyMzQ1Njc4OTAi..." \
  -H "Cookie: session=..." \
  -d '{"title": "New Resource"}'
```

**Alternative Header Name:**
```bash
-H "X-CSRFToken: ImFhY2RlZjEyMzQ1Njc4OTAi..."
```

#### 3. Token Lifecycle

- **Fetch:** Once per session or on app load
- **Reuse:** Token valid for 1 hour
- **Refresh:** Obtain new token after expiration or on 403 error
- **Storage:** Store in memory/state (never localStorage for security)

### Error Response

**Invalid/Missing CSRF Token:**
```json
{
  "error": "CSRF Validation Failed",
  "message": "CSRF token missing or invalid. Please refresh and try again.",
  "status": 403
}
```

**Response Code:** `403 Forbidden`

### Frontend Integration Example

```typescript
// api/client.ts
let csrfToken: string | null = null;

// Initialize on app load
export async function initCSRF() {
  const response = await fetch('/api/auth/csrf-token', {
    credentials: 'include'
  });
  const data = await response.json();
  csrfToken = data.csrf_token;
}

// Include in all state-changing requests
export async function apiPost(url: string, data: any) {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };
  
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken;
  }
  
  return fetch(url, {
    method: 'POST',
    headers,
    credentials: 'include',
    body: JSON.stringify(data)
  });
}
```

### Security Benefits

- ✅ Prevents Cross-Site Request Forgery attacks
- ✅ Token is session-specific and time-limited
- ✅ No token reuse across sessions
- ✅ Automatic validation on all state-changing operations

---

## Rate Limiting

### Implementation

**Library:** Flask-Limiter  
**Strategy:** Fixed-window rate limiting  
**Key Function:** IP address-based tracking  
**Status:** ✅ ACTIVE

### Configuration

```python
# Global defaults (applies to all unspecified endpoints)
default_limits=["200 per day", "50 per hour"]

# Storage (Development)
storage_uri="memory://"

# Storage (Production - Recommended)
storage_uri="redis://localhost:6379"
```

### Endpoint-Specific Limits

| Endpoint | Limit | Rationale |
|----------|-------|-----------|
| **Authentication** |
| `POST /api/auth/register` | 5 per 15 minutes | Prevent account spam |
| `POST /api/auth/login` | 10 per 15 minutes | Brute force protection |
| `POST /api/auth/change-password` | 3 per hour | High-sensitivity operation |
| **Resources** |
| `POST /api/resources` | 20 per hour | Prevent resource spam |
| **Bookings** |
| `POST /api/bookings` | 10 per hour | Prevent booking abuse |
| **Messages** |
| `POST /api/messages` | 30 per hour | Prevent message spam |
| **Reviews** |
| `POST /api/reviews` | 5 per hour | Prevent review manipulation |
| **Admin Operations** |
| Admin endpoints | 100 per hour | Trusted users, higher limit |
| **Default (All Others)** |
| All other endpoints | 50 per hour<br>200 per day | General API protection |

### Rate Limit Headers

**Response includes rate limit information:**

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1642089600
```

### Error Response

**Rate Limit Exceeded:**
```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Please try again later.",
  "retry_after": "60 seconds",
  "status": 429
}
```

**Response Code:** `429 Too Many Requests`

### Attack Mitigation

| Attack Type | Mitigation | Effectiveness |
|-------------|------------|---------------|
| Brute Force Login | 10 attempts/15min | 🟢 HIGH |
| Account Enumeration | 5 attempts/15min | 🟢 HIGH |
| Password Spray | 10 attempts/15min | 🟢 HIGH |
| Resource Creation Spam | 20/hour | 🟢 HIGH |
| Booking Abuse | 10/hour | 🟢 HIGH |
| Review Manipulation | 5/hour | 🟢 HIGH |
| DoS Attacks | 50/hour + 200/day | 🟡 MEDIUM |

### Production Recommendations

⚠️ **For production deployments:**

1. **Use Redis Storage** (Required for multi-instance deployments)
   ```python
   storage_uri="redis://localhost:6379"
   ```

2. **Consider User-Based Tracking** (for authenticated endpoints)
   ```python
   key_func=get_user_id  # Track by user ID instead of IP
   ```

3. **IP Whitelist** (for trusted services/IPs)
   ```python
   limiter.exempt("192.168.1.0/24")  # Internal network
   ```

4. **Sliding Window Strategy** (smoother rate limiting)
   ```python
   strategy="moving-window"  # Instead of "fixed-window"
   ```

---

## Security Headers

### Implementation

**Library:** Flask-Talisman  
**Status:** ✅ ACTIVE

### Headers Applied

#### 1. Content Security Policy (CSP)

```
Content-Security-Policy: 
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self';
  connect-src 'self';
  frame-ancestors 'none';
```

**Protection Against:**
- Cross-Site Scripting (XSS)
- Data injection attacks
- Malicious iframe embedding

#### 2. Strict-Transport-Security (HSTS)

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

**Production Only:** Enforces HTTPS for 1 year  
**Protection Against:** SSL stripping attacks

#### 3. X-Content-Type-Options

```
X-Content-Type-Options: nosniff
```

**Protection Against:** MIME type sniffing attacks

#### 4. X-Frame-Options

```
X-Frame-Options: DENY
```

**Protection Against:** Clickjacking attacks

#### 5. X-XSS-Protection

```
X-XSS-Protection: 1; mode=block
```

**Protection Against:** Legacy XSS attacks (browser-level)

#### 6. Referrer-Policy

```
Referrer-Policy: strict-origin-when-cross-origin
```

**Privacy Protection:** Limits referrer information leakage

### Configuration by Environment

#### Development
```python
TALISMAN_FORCE_HTTPS = False  # Allow HTTP
SESSION_COOKIE_SECURE = False
```

#### Production
```python
TALISMAN_FORCE_HTTPS = True   # Enforce HTTPS
SESSION_COOKIE_SECURE = True  # HTTPS-only cookies
SESSION_COOKIE_SAMESITE = 'Strict'
```

---

## Input Validation

### Validation Rules

#### 1. Authentication

**Registration:**
```python
- name: 3-100 characters, alphanumeric + spaces
- email: Valid email format, max 120 characters
- password: Min 8 characters, complexity requirements
- role: Enum ['student', 'staff', 'admin']
- department: Max 100 characters
```

**Login:**
```python
- email: Required, valid email format
- password: Required
```

#### 2. Resources

**Creation/Update:**
```python
- title: Required, 3-200 characters
- description: Max 5000 characters
- category: Enum [study_room, equipment, facility, vehicle, ...]
- location: Max 200 characters
- capacity: Integer, min 1, max 1000
- images: Max 5 files, 16MB each, allowed extensions
```

#### 3. Bookings

**Creation:**
```python
- resource_id: Required, valid integer
- start_datetime: Required, ISO 8601 format, min 30 min from now
- end_datetime: Required, must be after start_datetime
- duration: Min 15 minutes, max 7 days
- notes: Max 1000 characters
```

#### 4. Messages

**Send Message:**
```python
- receiver_id: Required, cannot be self
- content: Required, 1-5000 characters
- resource_id: Optional, valid integer
```

#### 5. Reviews

**Submit Review:**
```python
- resource_id: Required, must exist
- rating: Required, integer 1-5
- comment: Optional, 10-2000 characters
- booking_id: Optional, must be own completed booking
```

### Sanitization

**All user input is sanitized to prevent:**
- SQL Injection (via parameterized queries)
- XSS attacks (via Jinja2 auto-escaping)
- Path traversal (file upload validation)
- Command injection (no shell execution)

### File Upload Security

```python
# Configuration
MAX_CONTENT_LENGTH = 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Validation Process
1. Check file extension
2. Verify MIME type
3. Scan file size
4. Generate random filename (prevent overwrites)
5. Store in isolated upload directory
6. No code execution in upload dir
```

---

## Secret Management

### Environment Variables

**Critical Secrets (Must be set):**

```bash
# .env file (NEVER commit to version control)

# Critical
SECRET_KEY=<64+ character random hex string>
DATABASE_URL=postgresql://user:pass@host:5432/db

# Optional (for AI features)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Configuration
FLASK_ENV=production|development|testing
CORS_ORIGINS=https://example.com,https://www.example.com
```

### Secret Key Generation

**Generate secure random key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Result:** 64-character hexadecimal string

### Production Validation

**Automatic validation on startup:**

```python
# Checks performed in ProductionConfig:
✅ SECRET_KEY is set and length >= 64 characters
✅ SECRET_KEY doesn't contain weak patterns (dev, test, demo)
✅ DATABASE_URL is set and not SQLite
✅ CORS_ORIGINS don't include localhost
✅ CORS_ORIGINS use HTTPS (not HTTP)
```

**If validation fails:** Application will not start

### Security Best Practices

```bash
# ✅ DO:
- Use environment variables for all secrets
- Generate cryptographically random secrets
- Rotate secrets regularly (quarterly)
- Use different secrets per environment
- Store production secrets in secure vault (AWS Secrets Manager, HashiCorp Vault)

# ❌ DON'T:
- Commit .env file to version control
- Use default/example secrets
- Share secrets via email/chat
- Hardcode secrets in source code
- Reuse secrets across environments
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "error": "Error Type",
  "message": "Human-readable error message",
  "status": 400
}
```

### HTTP Status Codes

| Code | Error | Usage |
|------|-------|-------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid parameters or validation error |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions or CSRF failure |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource conflict (booking overlap) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error (logged) |

### Error Examples

#### 1. Authentication Required (401)
```json
{
  "error": "Unauthorized",
  "message": "Authentication is required to access this resource.",
  "status": 401
}
```

#### 2. CSRF Validation Failed (403)
```json
{
  "error": "CSRF Validation Failed",
  "message": "CSRF token missing or invalid. Please refresh and try again.",
  "status": 403
}
```

#### 3. Rate Limit Exceeded (429)
```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Please try again later.",
  "retry_after": "60 seconds",
  "status": 429
}
```

#### 4. Validation Error (400)
```json
{
  "error": "Validation Error",
  "message": "Password must be at least 8 characters long",
  "status": 400
}
```

### Security-Sensitive Error Handling

**Principle:** Never leak sensitive information in error messages

```python
# ❌ BAD: Reveals email existence
"Email already registered"

# ✅ GOOD: Generic message
"Invalid credentials"

# ❌ BAD: Reveals system details
"PostgreSQL connection error on server db-prod-01"

# ✅ GOOD: Generic message
"An internal server error occurred"
```

---

## Security Best Practices

### For API Consumers

#### 1. HTTPS Only
```
✅ https://api.example.com/api/resources
❌ http://api.example.com/api/resources
```

#### 2. Store Credentials Securely
- Never store passwords in plain text
- Use secure credential storage (Keychain, Secret Service)
- Never log sensitive data

#### 3. Handle CSRF Tokens Properly
```typescript
// ✅ DO: Store in memory/state
let csrfToken = response.csrf_token;

// ❌ DON'T: Store in localStorage (XSS risk)
localStorage.setItem('csrf', token);
```

#### 4. Implement Proper Error Handling
```typescript
try {
  const response = await apiCall();
  if (response.status === 429) {
    // Respect rate limit, wait before retry
    await sleep(60000);
  } else if (response.status === 403) {
    // Refresh CSRF token
    await initCSRF();
  }
} catch (error) {
  // Handle network errors
}
```

#### 5. Validate Responses
```typescript
// Always validate API responses
if (!response.ok) {
  const error = await response.json();
  throw new Error(error.message);
}
```

### For API Developers

#### 1. Never Disable Security Features
```python
# ❌ NEVER do this in production
WTF_CSRF_ENABLED = False
TALISMAN_FORCE_HTTPS = False
```

#### 2. Use Parameterized Queries
```python
# ✅ DO: Parameterized query (safe)
User.query.filter_by(email=email).first()

# ❌ DON'T: String concatenation (SQL injection risk)
db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

#### 3. Log Security Events
```python
# Log all authentication attempts
logger.info(f"Login attempt for {email}", extra={
    'ip_address': get_client_ip(),
    'success': True/False
})
```

#### 4. Keep Dependencies Updated
```bash
# Regularly update dependencies
pip install --upgrade flask flask-wtf flask-limiter

# Check for vulnerabilities
pip-audit
```

#### 5. Regular Security Audits
```bash
# Run security tests before deployment
pytest backend/tests/security/ -v

# Use security linters
bandit -r backend/
```

---

## Compliance & Standards

### OWASP Top 10 (2021) Coverage

| Risk | Mitigation | Implementation |
|------|------------|----------------|
| A01: Broken Access Control | ✅ RBAC, permission checks | `@admin_required`, `@login_required` |
| A02: Cryptographic Failures | ✅ Bcrypt password hashing, HTTPS | Password hashing, SSL in prod |
| A03: Injection | ✅ Parameterized queries, input validation | SQLAlchemy ORM, validators |
| A04: Insecure Design | ✅ Security by design | Phase 0 security focus |
| A05: Security Misconfiguration | ✅ Secure defaults, validation | Production config validation |
| A06: Vulnerable Components | ⚠️ Regular updates needed | `requirements.txt` |
| A07: Auth Failures | ✅ Rate limiting, strong passwords | Flask-Limiter, Bcrypt |
| A08: Software/Data Integrity | ✅ Input validation, CSP | Validators, security headers |
| A09: Logging Failures | ✅ Audit logging | Logger utility |
| A10: SSRF | ✅ Input validation, no external requests | Validators |

### CWE Coverage

- ✅ **CWE-79:** XSS Prevention (CSP, auto-escaping)
- ✅ **CWE-89:** SQL Injection Prevention (ORM, parameterized queries)
- ✅ **CWE-200:** Information Exposure (generic error messages)
- ✅ **CWE-307:** Brute Force Protection (rate limiting)
- ✅ **CWE-352:** CSRF Protection (CSRF tokens)
- ✅ **CWE-521:** Weak Password Requirements (enforced complexity)
- ✅ **CWE-614:** Sensitive Cookie (HTTPOnly, Secure flags)

### NIST 800-63B Alignment

- ✅ Password complexity requirements
- ✅ Rate limiting on authentication
- ✅ Secure session management
- ✅ Multi-factor authentication ready (future enhancement)

---

## Security Testing

### Automated Tests

```bash
# Run all security tests
pytest backend/tests/security/ -v

# Specific test suites
pytest backend/tests/security/test_csrf_protection.py -v
pytest backend/tests/security/test_rate_limiting.py -v
pytest backend/tests/security/test_security_headers.py -v
pytest backend/tests/security/test_input_validation.py -v
pytest backend/tests/security/test_secret_management.py -v
```

### Test Coverage

| Security Feature | Test Cases | Coverage |
|------------------|------------|----------|
| CSRF Protection | 16 tests | 100% |
| Rate Limiting | 13 tests | 100% |
| Security Headers | 12 tests | 100% |
| Input Validation | 15+ tests | 95% |
| Secret Management | 8 tests | 100% |
| Authentication | 20+ tests | 90% |

---

## Support & Contact

For security issues or questions:

1. **Security Vulnerabilities:** Report privately to security team
2. **API Questions:** Refer to `backend/API_DOCUMENTATION.md`
3. **Implementation Details:** Review Phase 0 completion docs

---

**Last Security Audit:** January 12, 2025  
**Next Audit Due:** April 12, 2025  
**Security Status:** ✅ PRODUCTION-READY
