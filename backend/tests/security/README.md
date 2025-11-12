# Security Test Suite Documentation

This directory contains comprehensive security tests for the Campus Resource Hub backend.

## Overview

The security test suite validates all security features implemented in Phase 0: Security Hardening.

## Test Files

### 1. `test_csrf_protection.py`
**Purpose:** Validates CSRF (Cross-Site Request Forgery) protection

**Coverage:**
- CSRF token generation and validation
- CSRF enforcement on POST, PUT, DELETE requests
- CSRF exemption for GET requests
- Token expiration and session binding
- Different header format support (X-CSRF-Token, X-CSRFToken)
- Cross-session token validation

**Key Test Classes:**
- `TestCSRFTokenEndpoint` - Token generation
- `TestCSRFProtectionPOST` - POST request protection
- `TestCSRFProtectionPUT` - PUT request protection
- `TestCSRFProtectionDELETE` - DELETE request protection
- `TestCSRFHeaderVariations` - Header format variations
- `TestCSRFSecurityBoundaries` - Edge cases and boundaries
- `TestCSRFWithAuthentication` - Integration with auth

**Run Command:**
```bash
pytest backend/tests/security/test_csrf_protection.py -v
```

### 2. `test_rate_limiting.py`
**Purpose:** Validates rate limiting to prevent brute force and abuse

**Coverage:**
- Registration endpoint rate limit (5 per 15 minutes)
- Login endpoint rate limit (10 per 15 minutes)
- Password change endpoint rate limit (3 per hour)
- Rate limit error responses (429 status)
- Independent rate limits per endpoint
- Brute force attack prevention

**Key Test Classes:**
- `TestRateLimitConfiguration` - Limiter setup
- `TestRegisterEndpointRateLimit` - Registration limits
- `TestLoginEndpointRateLimit` - Login limits
- `TestChangePasswordEndpointRateLimit` - Password change limits
- `TestRateLimitIndependence` - Cross-endpoint independence
- `TestRateLimitSecurity` - Attack prevention

**Run Command:**
```bash
pytest backend/tests/security/test_rate_limiting.py -v
```

### 3. `test_security_headers.py`
**Purpose:** Validates HTTP security headers configuration

**Coverage:**
- Strict-Transport-Security (HSTS)
- X-Content-Type-Options: nosniff
- X-Frame-Options: SAMEORIGIN
- X-XSS-Protection
- Referrer-Policy
- Content-Security-Policy (CSP)
- Feature-Policy/Permissions-Policy

**Key Test Classes:**
- `TestSecurityHeadersPresence` - Header presence validation
- `TestContentSecurityPolicy` - CSP configuration
- `TestFeaturePolicy` - Feature policy configuration
- `TestClickjackingProtection` - Clickjacking defenses
- `TestMIMESniffingProtection` - MIME sniffing prevention
- `TestXSSProtection` - XSS protection headers

**Run Command:**
```bash
pytest backend/tests/security/test_security_headers.py -v
```

### 4. `test_secret_management.py`
**Purpose:** Validates secure secret management and configuration

**Coverage:**
- SECRET_KEY validation (length, entropy, patterns)
- DATABASE_URL validation (production vs development)
- CORS_ORIGINS validation (HTTPS, localhost restrictions)
- ProductionConfig validation and enforcement
- .gitignore and .env.example completeness
- Secret generation utilities

**Key Test Classes:**
- `TestSecretsValidatorSecretKey` - SECRET_KEY validation
- `TestSecretsValidatorDatabaseURL` - Database URL validation
- `TestSecretsValidatorCORSOrigins` - CORS validation
- `TestSecretsValidatorEnvironmentConfig` - Full config validation
- `TestProductionConfigValidation` - Production enforcement
- `TestSecretsInGitignore` - Git security
- `TestEnvExampleFile` - Documentation completeness

**Run Command:**
```bash
pytest backend/tests/security/test_secret_management.py -v
```

### 5. `test_input_validation.py`
**Purpose:** Validates input validation and sanitization

**Coverage:**
- Email validation
- Password strength validation
- String validation (length, null bytes, special chars)
- Integer validation
- Choice validation
- HTML sanitization (XSS prevention)
- SQL LIKE sanitization
- Filename sanitization (path traversal prevention)
- Request data validation with schemas

**Key Test Classes:**
- `TestEmailValidation` - Email format and security
- `TestPasswordValidation` - Password strength rules
- `TestStringValidation` - Generic string validation
- `TestHTMLSanitization` - XSS prevention
- `TestFilenameSanitization` - Path traversal prevention
- `TestInjectionPrevention` - SQL injection, XSS, path traversal

**Run Command:**
```bash
pytest backend/tests/security/test_input_validation.py -v
```

### 6. `test_baseline_security.py`
**Purpose:** Comprehensive integration tests for all security features

**Coverage:**
- Complete security workflows (registration, login, authenticated requests)
- Cross-feature integration (CSRF + rate limiting, validation + headers)
- Security error handling
- Authorization with security features
- Content Security Policy integration
- Input sanitization across endpoints
- Security configuration validation
- Comprehensive security audit

**Key Test Classes:**
- `TestComprehensiveSecurityWorkflow` - End-to-end workflows
- `TestCrossFeatureSecurityIntegration` - Feature interaction
- `TestSecurityErrorHandling` - Error security
- `TestAuthorizationWithSecurity` - Auth + security
- `TestInputSanitizationIntegration` - Sanitization integration
- `TestComprehensiveSecurityAudit` - Full security audit
- `TestSecurityBestPractices` - Best practices compliance

**Run Command:**
```bash
pytest backend/tests/security/test_baseline_security.py -v
```

## Running Tests

### Run All Security Tests
```bash
# From project root
pytest backend/tests/security/ -v

# With coverage
pytest backend/tests/security/ -v --cov=backend --cov-report=html

# With detailed output
pytest backend/tests/security/ -v --tb=short
```

### Run Specific Test File
```bash
pytest backend/tests/security/test_csrf_protection.py -v
```

### Run Specific Test Class
```bash
pytest backend/tests/security/test_csrf_protection.py::TestCSRFTokenEndpoint -v
```

### Run Specific Test Method
```bash
pytest backend/tests/security/test_csrf_protection.py::TestCSRFTokenEndpoint::test_csrf_token_endpoint_returns_token -v
```

### Run with Coverage
```bash
# Generate HTML coverage report
pytest backend/tests/security/ --cov=backend --cov-report=html

# View report at htmlcov/index.html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Environment Setup

### Prerequisites
```bash
# Install test dependencies
pip install -r backend/requirements.txt

# Install development dependencies
pip install pytest pytest-cov pytest-mock
```

### Environment Variables
Tests use the `testing` configuration which:
- Uses SQLite in-memory database
- Disables CSRF for easier integration testing
- Disables rate limiting for controlled testing
- Uses test-specific SECRET_KEY

### Running Tests in Docker
```bash
# Build and run tests in container
docker-compose run backend pytest tests/security/ -v
```

## Test Coverage Goals

### Current Coverage
- **CSRF Protection:** 95%+ coverage
- **Rate Limiting:** 90%+ coverage
- **Security Headers:** 90%+ coverage
- **Secret Management:** 95%+ coverage
- **Input Validation:** 95%+ coverage
- **Baseline Integration:** 85%+ coverage

### Target Coverage
- Overall security module coverage: **90%+**
- Critical security functions: **100%**

## Security Test Checklist

Use this checklist when adding new endpoints or features:

- [ ] CSRF protection on state-changing endpoints (POST, PUT, DELETE, PATCH)
- [ ] Rate limiting on authentication endpoints
- [ ] Security headers on all responses
- [ ] Input validation for all user inputs
- [ ] HTML sanitization for any rich text
- [ ] Filename sanitization for file uploads
- [ ] No sensitive data in error responses
- [ ] No information disclosure in error messages
- [ ] Proper authorization checks
- [ ] Logging of security events
- [ ] Tests for new security features
- [ ] Documentation updated

## Common Test Patterns

### Testing CSRF Protection
```python
def test_csrf_required(client):
    # Get CSRF token
    csrf_response = client.get('/api/auth/csrf-token')
    csrf_token = csrf_response.get_json()['csrf_token']
    
    # Request without CSRF should fail
    response = client.post('/endpoint', json={})
    assert response.status_code == 403
    
    # Request with CSRF should succeed
    response = client.post('/endpoint',
        json={},
        headers={'X-CSRF-Token': csrf_token}
    )
    assert response.status_code != 403
```

### Testing Rate Limiting
```python
def test_rate_limit(client):
    # Make requests up to limit
    for i in range(5):
        response = client.post('/endpoint', json={})
        assert response.status_code != 429
    
    # Next request should be rate limited
    response = client.post('/endpoint', json={})
    assert response.status_code == 429
```

### Testing Input Validation
```python
def test_input_validation(client):
    # Test with malicious input
    response = client.post('/endpoint',
        json={'name': '<script>alert("XSS")</script>'}
    )
    
    # Should reject or sanitize
    assert response.status_code in [200, 400]
    if response.status_code == 200:
        # Verify sanitization
        data = response.get_json()
        assert '<script>' not in str(data)
```

## Continuous Integration

### GitHub Actions
Add to `.github/workflows/security-tests.yml`:
```yaml
name: Security Tests

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
      - name: Run security tests
        run: |
          cd backend
          pytest tests/security/ -v --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Security Testing Best Practices

1. **Test Both Positive and Negative Cases**
   - Valid inputs should succeed
   - Invalid/malicious inputs should fail safely

2. **Test Edge Cases**
   - Empty strings
   - Null bytes
   - Maximum lengths
   - Special characters

3. **Test Cross-Feature Interactions**
   - CSRF + Rate Limiting
   - Auth + CSRF
   - Validation + Sanitization

4. **Test Error Conditions**
   - Error responses should not leak information
   - Security headers present even on errors

5. **Keep Tests Independent**
   - Each test should be self-contained
   - Use fixtures for common setup
   - Clean up test data

6. **Update Tests with Code Changes**
   - Add tests for new endpoints
   - Update tests when security features change
   - Keep test documentation current

## Troubleshooting

### Tests Failing After Code Changes
1. Check if security features were accidentally disabled
2. Verify configuration in `backend/config.py`
3. Check if new endpoints need security decorators
4. Review error messages for clues

### Rate Limiting Tests Intermittent
- Rate limits may persist between test runs
- Use isolated test clients
- Add small delays if necessary
- Check limiter storage backend

### CSRF Tests Failing
- Verify WTF_CSRF_ENABLED in testing config
- Check session configuration
- Ensure CSRF token is fresh for each test
- Verify header format (X-CSRF-Token vs X-CSRFToken)

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Flask-WTF CSRF Documentation](https://flask-wtf.readthedocs.io/en/stable/csrf.html)
- [Flask-Limiter Documentation](https://flask-limiter.readthedocs.io/)
- [Flask-Talisman Documentation](https://github.com/GoogleCloudPlatform/flask-talisman)

## Maintainers

For questions or issues with security tests, contact the development team.

## Last Updated

2025-01-12
