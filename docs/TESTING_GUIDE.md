# Testing Guide

> **Campus Resource Hub Testing Documentation**  
> Comprehensive guide to running tests, understanding coverage requirements, and maintaining test quality

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Coverage Requirements](#coverage-requirements)
- [Writing Tests](#writing-tests)
- [CI/CD Pipeline](#cicd-pipeline)
- [Troubleshooting](#troubleshooting)

---

## Overview

### Testing Philosophy

Our testing strategy follows a **layered approach** aligned with the application architecture:

```
┌─────────────────────────────────────────────────┐
│  Integration Tests (E2E User Workflows)         │  ← 15-20% of tests
├─────────────────────────────────────────────────┤
│  API Tests (Route + Service Layer)              │  ← 40-50% of tests
├─────────────────────────────────────────────────┤
│  Security Tests (CSRF, Rate Limiting, etc.)     │  ← 20-25% of tests
├─────────────────────────────────────────────────┤
│  Unit Tests (Utilities, Validators)             │  ← 10-15% of tests
└─────────────────────────────────────────────────┘
```

### Key Principles

1. **Security First**: 95%+ coverage for security-critical code
2. **Business Logic**: 85%+ coverage for API routes and services
3. **Integration**: Full user workflow testing for critical paths
4. **Fast Feedback**: Tests run in < 5 minutes locally
5. **Maintainability**: Clear test names, minimal mocking, DRY principles

---

## Quick Start

### Prerequisites

```bash
# Ensure you're in the backend directory
cd backend

# Install test dependencies
pip install -r requirements.txt
```

### Run All Tests (Recommended)

```bash
# Run comprehensive test suite with coverage
./run_all_tests.sh
```

This script will:
- ✅ Check code formatting (Black)
- ✅ Run linter checks (Ruff)
- ✅ Run type checking (Mypy)
- ✅ Execute all test suites
- ✅ Generate coverage reports

### Quick Test Commands

```bash
# Security tests only (must achieve 95%+)
pytest tests/security/ -v --cov=. --cov-report=term-missing --cov-fail-under=95

# API tests only
pytest tests/api/ -v --cov=routes --cov=services --cov-report=term-missing

# Integration tests only
pytest tests/integration/ -v

# Single test file
pytest tests/api/test_resources_api.py -v

# Single test function
pytest tests/api/test_resources_api.py::test_list_resources -v
```

---

## Test Structure

### Directory Layout

```
backend/tests/
├── __init__.py
├── conftest.py                    # Global fixtures
│
├── security/                      # Security tests (95% coverage)
│   ├── __init__.py
│   ├── conftest.py               # Security-specific fixtures
│   ├── test_csrf_protection.py   # CSRF token validation
│   ├── test_rate_limiting.py     # Rate limit enforcement
│   ├── test_security_headers.py  # HTTP security headers
│   ├── test_input_validation.py  # SQL injection, XSS prevention
│   ├── test_secret_management.py # Secrets handling
│   └── test_baseline_security.py # Core security checks
│
├── api/                          # API endpoint tests
│   ├── __init__.py
│   ├── conftest.py              # API-specific fixtures
│   ├── test_auth_api.py         # Authentication endpoints
│   ├── test_resources_api.py    # Resource CRUD operations
│   ├── test_bookings_api.py     # Booking operations
│   ├── test_messages_api.py     # Messaging system
│   ├── test_reviews_api.py      # Review system
│   └── test_admin_api.py        # Admin operations
│
└── integration/                  # End-to-end workflow tests
    ├── __init__.py
    ├── conftest.py              # Integration fixtures
    ├── test_user_workflows.py   # Student booking workflows
    ├── test_admin_workflows.py  # Admin management workflows
    └── test_concurrent_operations.py  # Multi-user scenarios
```

### Test File Count

- **Total Test Files**: 18
- **Security Tests**: 6 files (core security requirements)
- **API Tests**: 6 files (one per blueprint)
- **Integration Tests**: 3 files (critical user journeys)
- **Configuration**: 3 conftest.py files (fixtures)

---

## Running Tests

### 1. Comprehensive Test Runner Script

**File**: `backend/run_all_tests.sh`

```bash
./run_all_tests.sh
```

**Features:**
- Color-coded output (green = pass, red = fail, yellow = warning)
- Sequential execution: quality checks → security → API → integration
- HTML coverage reports generated in `htmlcov/`
- XML reports for CI/CD systems
- Test summary with file counts and timings

**Exit Codes:**
- `0`: All tests passed, coverage met
- `1`: Quality checks failed (formatting, linting, types)
- `2`: Security tests failed or < 95% coverage
- `3`: API tests failed
- `4`: Integration tests failed
- `5`: Overall coverage < 85%

### 2. Pytest with Markers

We use **pytest markers** to categorize tests:

```python
# In test files
@pytest.mark.security    # Security-critical tests
@pytest.mark.api         # API endpoint tests
@pytest.mark.integration # Integration/E2E tests
@pytest.mark.unit        # Unit tests
@pytest.mark.slow        # Tests taking > 1 second
@pytest.mark.smoke       # Critical path smoke tests
```

**Run by marker:**

```bash
# Security tests only
pytest -m security

# Fast tests only (exclude slow tests)
pytest -m "not slow"

# Smoke tests for quick validation
pytest -m smoke

# Multiple markers
pytest -m "security or api"
```

### 3. Coverage Reports

**Generate HTML coverage report:**

```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html  # View in browser
```

**Terminal coverage report:**

```bash
pytest tests/ --cov=. --cov-report=term-missing
```

**Coverage by component:**

```bash
# Security code coverage
pytest tests/security/ --cov=middleware --cov=utils --cov-report=term

# API routes coverage
pytest tests/api/ --cov=routes --cov=services --cov-report=term

# Repository layer coverage
pytest tests/integration/ --cov=data_access --cov-report=term
```

---

## Coverage Requirements

### Overall Thresholds

| Component | Minimum Coverage | Target Coverage |
|-----------|-----------------|-----------------|
| **Security Critical** | 95% | 98% |
| **API Routes** | 85% | 90% |
| **Services** | 85% | 90% |
| **Repositories** | 80% | 85% |
| **Utilities** | 90% | 95% |
| **Overall** | **85%** | **88%** |

### Configuration Files

**pytest.ini**:
```ini
[pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts =
    -v
    --strict-markers
    --tb=short
    --cov-branch
    --cov-fail-under=85
```

**pyproject.toml**:
```toml
[tool.coverage.run]
source = ["backend"]
omit = ["*/tests/*", "*/test_*.py"]
branch = true

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
fail_under = 85.0
```

### Current Coverage Status

Run this command to see current coverage:

```bash
cd backend
pytest tests/ --cov=. --cov-report=term-missing --cov-fail-under=85
```

**Expected output:**
```
========================= test session starts ==========================
collected 150+ items

tests/security/test_csrf_protection.py ........          [  5%]
tests/security/test_rate_limiting.py .........           [ 12%]
...

----------- coverage: platform linux, python 3.9.x -----------
Name                                   Stmts   Miss  Cover   Missing
--------------------------------------------------------------------
routes/auth.py                           156      8    95%   45, 78-82
routes/resources.py                      203     12    94%   156-159, 201-205
...
--------------------------------------------------------------------
TOTAL                                   5234    445    91%

========================= 152 passed in 45.23s =========================
```

---

## Writing Tests

### 1. Test Structure Pattern

Follow the **AAA pattern** (Arrange, Act, Assert):

```python
def test_create_resource_success(client, auth_headers, csrf_token):
    """Test successful resource creation with valid data."""
    # ARRANGE - Set up test data
    resource_data = {
        "name": "Conference Room A",
        "category": "room",
        "capacity": 20,
        "description": "Main conference room"
    }
    headers = {**auth_headers, "X-CSRF-Token": csrf_token}
    
    # ACT - Perform the action
    response = client.post(
        "/api/resources",
        json=resource_data,
        headers=headers
    )
    
    # ASSERT - Verify the outcome
    assert response.status_code == 201
    assert response.json["data"]["name"] == "Conference Room A"
    assert response.json["data"]["capacity"] == 20
```

### 2. Common Fixtures

**Defined in `conftest.py` files:**

```python
# Application and client fixtures
@pytest.fixture
def app():
    """Create Flask app configured for testing."""
    
@pytest.fixture
def client(app):
    """Test client for making requests."""
    
@pytest.fixture
def db(app):
    """Database fixture with clean state."""

# Authentication fixtures
@pytest.fixture
def student_user(db):
    """Create test student user."""
    
@pytest.fixture
def admin_user(db):
    """Create test admin user."""
    
@pytest.fixture
def auth_headers(client, student_user):
    """Get authentication headers with session."""

# Security fixtures
@pytest.fixture
def csrf_token(client, auth_headers):
    """Get CSRF token for protected requests."""
```

### 3. Security Test Example

```python
import pytest

@pytest.mark.security
def test_csrf_protection_enforced(client, auth_headers):
    """Test that POST requests without CSRF token are rejected."""
    # Attempt POST without CSRF token
    response = client.post(
        "/api/resources",
        json={"name": "Test Resource"},
        headers=auth_headers
    )
    
    # Should be rejected with 400 Bad Request
    assert response.status_code == 400
    assert "CSRF" in response.json.get("error", "")

@pytest.mark.security
def test_rate_limiting_enforced(client):
    """Test that rate limiting blocks excessive requests."""
    endpoint = "/api/auth/login"
    
    # Make requests up to the limit
    for _ in range(10):
        response = client.post(endpoint, json={
            "email": "test@example.com",
            "password": "wrong"
        })
        if response.status_code == 429:
            break
    
    # Verify rate limit was hit
    assert response.status_code == 429
    assert "rate limit" in response.json.get("error", "").lower()
```

### 4. API Test Example

```python
@pytest.mark.api
def test_list_resources_with_filters(client, auth_headers):
    """Test resource listing with category filter."""
    # Create test resources
    resources = [
        {"name": "Room A", "category": "room"},
        {"name": "Room B", "category": "room"},
        {"name": "Projector", "category": "equipment"}
    ]
    
    for res in resources:
        # ... create resources ...
    
    # Filter by category
    response = client.get(
        "/api/resources?category=room",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert len(response.json["data"]) == 2
    assert all(r["category"] == "room" for r in response.json["data"])
```

### 5. Integration Test Example

```python
@pytest.mark.integration
def test_complete_booking_workflow(client, student_user, admin_user):
    """Test complete booking lifecycle: create → approve → complete."""
    # 1. Student creates booking
    booking_data = {
        "resource_id": 1,
        "start_time": "2025-01-15T10:00:00",
        "end_time": "2025-01-15T12:00:00"
    }
    
    response = client.post("/api/bookings", json=booking_data)
    assert response.status_code == 201
    booking_id = response.json["data"]["id"]
    
    # 2. Admin approves booking
    response = client.patch(
        f"/api/admin/bookings/{booking_id}",
        json={"status": "approved"}
    )
    assert response.status_code == 200
    
    # 3. Booking auto-completes after end time
    # ... (simulate time passage or manual completion)
    
    # 4. Verify final state
    response = client.get(f"/api/bookings/{booking_id}")
    assert response.json["data"]["status"] == "completed"
```

### 6. Testing Best Practices

#### ✅ DO

- **Use descriptive test names**: `test_create_resource_with_missing_name_returns_400`
- **Test one thing**: Each test should verify a single behavior
- **Use fixtures**: Don't repeat setup code
- **Clean up**: Use `db.session.rollback()` or transactional fixtures
- **Test edge cases**: Empty inputs, missing fields, invalid types
- **Check error messages**: Verify helpful error messages are returned
- **Use markers**: Tag tests with `@pytest.mark.security`, etc.

#### ❌ DON'T

- **Don't test framework code**: Don't test Flask itself, test your code
- **Avoid excessive mocking**: Mock external services, not your own code
- **Don't share state**: Each test should be independent
- **Don't skip assertions**: Always verify the expected outcome
- **Don't test implementation**: Test behavior, not internal details
- **Don't hardcode sensitive data**: Use fixtures and test data

---

## CI/CD Pipeline

### GitHub Actions Workflow

**File**: `.github/workflows/tests.yml`

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

### Pipeline Jobs

```
┌───────────────────────────────────────────────────┐
│  Job 1: Code Quality (Black, Ruff, Mypy)         │
│  - Formatter check (line length 100)             │
│  - Linter (E, F, W, C, N rules)                  │
│  - Type checking                                  │
│  - Timeout: 10 minutes                           │
└───────────────────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────┐
│  Job 2: Security Tests (95% Coverage Required)   │
│  - CSRF protection tests                         │
│  - Rate limiting tests                           │
│  - Input validation tests                        │
│  - Security headers tests                        │
│  - Timeout: 15 minutes                           │
└───────────────────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────┐
│  Job 3: API Tests (All 49 Endpoints)             │
│  - Auth, Resources, Bookings, Messages           │
│  - Reviews, Admin APIs                           │
│  - Timeout: 20 minutes                           │
└───────────────────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────┐
│  Job 4: Integration Tests (User Workflows)       │
│  - Complete user journeys                        │
│  - Admin workflows                               │
│  - Concurrent operations                         │
│  - Timeout: 20 minutes                           │
└───────────────────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────┐
│  Job 5: Combined Coverage (85% Required)         │
│  - Run all tests together                        │
│  - Generate coverage badge                       │
│  - Upload coverage reports                       │
│  - Comment on PR with results                    │
│  - Timeout: 25 minutes                           │
└───────────────────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────┐
│  Job 6: Test Summary                             │
│  - Aggregate results from all jobs               │
│  - Generate pipeline summary                     │
│  - Fail if any gate fails                        │
└───────────────────────────────────────────────────┘
```

### Coverage Artifacts

After each CI run, the following artifacts are saved:

- `security-coverage-report` (HTML)
- `api-coverage-report` (HTML)
- `integration-coverage-report` (HTML)
- `combined-coverage-report` (HTML)
- `coverage-badge` (SVG)
- Coverage XML files (for integrations)

**Retention**: 30 days

### Pull Request Comments

The pipeline automatically comments on PRs with:
- Coverage percentage change
- Lines covered/missing
- Coverage report link

---

## Pre-Commit Hooks

### Installation

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install
```

### What Runs on Commit

**File**: `.pre-commit-config.yaml`

1. **Black** - Code formatter (line-length=100)
2. **Ruff** - Fast linter (E, F, W, C, N rules)
3. **isort** - Import sorting
4. **Bandit** - Security issue scanner
5. **Mypy** - Static type checking
6. **Pydocstyle** - Docstring checks
7. **File checks** - Trailing whitespace, large files, etc.

### Bypass Pre-Commit (Emergency Only)

```bash
git commit -m "Emergency fix" --no-verify
```

**⚠️ Warning**: Bypassing pre-commit will likely cause CI to fail.

---

## Troubleshooting

### Common Issues

#### 1. Tests Fail Locally But Pass in CI

**Cause**: Different environment or database state

**Solution**:
```bash
# Clean database and caches
rm -f instance/test.db
rm -rf __pycache__ .pytest_cache
pytest tests/ --cache-clear
```

#### 2. Coverage Below Threshold

**Cause**: New code added without tests

**Solution**:
```bash
# Find untested code
pytest tests/ --cov=. --cov-report=term-missing

# Look for "Missing" lines in report
# Add tests for those lines
```

#### 3. Slow Test Suite

**Cause**: Database operations, network calls, or too many tests

**Solution**:
```bash
# Identify slow tests
pytest tests/ --durations=10

# Run only fast tests
pytest tests/ -m "not slow"

# Use database transactions in conftest.py
@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        db.create_all()
        yield db
        db.session.rollback()
        db.drop_all()
```

#### 4. CSRF Token Issues in Tests

**Cause**: CSRF protection enabled in test mode

**Solution**:
```python
# Get CSRF token from endpoint
@pytest.fixture
def csrf_token(client, auth_headers):
    response = client.get("/api/auth/csrf-token", headers=auth_headers)
    return response.json["csrf_token"]

# Use in tests
def test_protected_endpoint(client, auth_headers, csrf_token):
    headers = {**auth_headers, "X-CSRF-Token": csrf_token}
    response = client.post("/api/resources", json=data, headers=headers)
```

#### 5. Import Errors

**Cause**: Python path or module structure issues

**Solution**:
```bash
# Ensure backend directory is in Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"

# Or run from backend directory
cd backend
pytest tests/
```

#### 6. Fixture Not Found

**Cause**: Missing `conftest.py` or fixture not in scope

**Solution**:
```python
# Check conftest.py hierarchy:
# backend/tests/conftest.py       - Global fixtures
# backend/tests/api/conftest.py   - API-specific fixtures

# Verify fixture is defined in correct location
# Use --fixtures flag to list available fixtures
pytest --fixtures
```

---

## Continuous Improvement

### Adding New Tests

1. **Identify test type**: Security, API, Integration, or Unit
2. **Create test file**: Follow naming convention `test_*.py`
3. **Add markers**: Use `@pytest.mark.*` decorators
4. **Write tests**: Follow AAA pattern (Arrange, Act, Assert)
5. **Run locally**: `pytest path/to/test_file.py -v`
6. **Check coverage**: Ensure new code is covered
7. **Commit and push**: Let CI verify

### Test Maintenance

- **Review coverage reports** weekly
- **Update tests** when APIs change
- **Remove obsolete tests** when features are deprecated
- **Refactor common patterns** into fixtures
- **Document complex test scenarios**

### Performance Monitoring

```bash
# Generate test performance report
pytest tests/ --durations=0 > test_timings.txt

# Review slowest tests
head -n 20 test_timings.txt
```

---

## Additional Resources

### Documentation Links

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Flask Testing](https://flask.palletsprojects.com/testing/)
- [GitHub Actions](https://docs.github.com/en/actions)

### Internal Documentation

- `backend/tests/security/README.md` - Security test details
- `docs/API_SECURITY_GUIDE.md` - Security requirements
- `backend/API_DOCUMENTATION.md` - API specifications
- `docs/PHASE1_PLAN.md` - Testing strategy

### Getting Help

1. **Check test output**: Read error messages carefully
2. **Review docs**: Consult this guide and API docs
3. **Run with verbose**: Use `-v` and `--tb=long` flags
4. **Check CI logs**: View detailed GitHub Actions logs
5. **Ask team**: Reach out in #testing channel

---

## Quick Reference

### Essential Commands

```bash
# Run all tests with coverage
./run_all_tests.sh

# Run specific test suite
pytest tests/security/ -v
pytest tests/api/ -v
pytest tests/integration/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test
pytest tests/api/test_resources_api.py::test_create_resource -v

# Run by marker
pytest -m security
pytest -m "api and not slow"

# Show coverage gaps
pytest tests/ --cov=. --cov-report=term-missing

# Profile slow tests
pytest tests/ --durations=10
```

### Coverage Thresholds

- Security: **95%+**
- API/Services: **85%+**
- Overall: **85%+**

### Quality Gates

- ✅ Black formatting
- ✅ Ruff linting
- ✅ Mypy type checking
- ✅ Security tests pass
- ✅ API tests pass
- ✅ Integration tests pass
- ✅ Coverage thresholds met

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Maintained By**: Development Team
