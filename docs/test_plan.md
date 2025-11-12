# Test Plan

**Document Purpose:** Comprehensive testing strategy covering unit, integration, E2E, security, and performance testing for the Campus Resource Hub.

**Date:** November 12, 2025  
**Project:** Campus Resource Hub - AiDD 2025 Capstone  
**AiDD Compliance:** Section 10 (Testing & Validation Requirements)

---

## Executive Summary

**Testing Approach:** Pyramid model - many unit tests, fewer integration tests, minimal E2E tests

**Current Coverage:** < 10% (minimal tests exist)  
**Target Coverage:** 
- Unit: 80%
- Integration: 70%
- E2E: Critical paths only

**AiDD Requirements Status:**
- ✅ Unit tests for booking logic (minimal, needs expansion)
- ❌ DAL unit tests (missing)
- ❌ Auth integration test (missing)
- ❌ E2E booking scenario (missing)
- ❌ SQL injection tests (missing)

**Timeline:** Integrate testing throughout Phases 1-2 per roadmap_phased.md

---

## 1. Unit Testing Strategy

### 1.1 Backend Unit Tests (pytest)

#### 1.1.1 Model Layer Tests
**Location:** `backend/tests/test_models.py`

**User Model Tests:**
```python
def test_user_password_hashing():
    user = User(email='test@example.com', full_name='Test User')
    user.set_password('SecurePass123!')
    assert user.password_hash is not None
    assert user.check_password('SecurePass123!') is True
    assert user.check_password('WrongPassword') is False

def test_user_role_validation():
    user = User(email='test@example.com', role='student')
    assert user.role in ['student', 'staff', 'admin']
```

**Resource Model Tests:**
```python
def test_resource_creation():
    resource = Resource(
        name='Test Room',
        owner_id=1,
        category='study_room',
        status='draft'
    )
    assert resource.status == 'draft'
    assert resource.category == 'study_room'

def test_resource_average_rating_calculation():
    # Test cached rating calculation
    pass
```

**Coverage Target:** 90% for models

---

#### 1.1.2 Service Layer Tests
**Location:** `backend/tests/test_services/`

**Auth Service Tests:**
```python
def test_register_user_success():
    user, error = auth_service.register_user(
        name='Test User',
        email='test@example.com',
        password='SecurePass123!',
        role='student'
    )
    assert user is not None
    assert error is None
    assert user.email == 'test@example.com'

def test_register_duplicate_email():
    # First registration
    auth_service.register_user('Test', 'test@example.com', 'Pass123!', 'student')
    # Second registration with same email
    user, error = auth_service.register_user('Test2', 'test@example.com', 'Pass456!', 'student')
    assert user is None
    assert 'already exists' in error.lower()

def test_login_invalid_credentials():
    user, error = auth_service.login('wrong@example.com', 'WrongPass')
    assert user is None
    assert error is not None
```

**Booking Service Tests (AiDD Required):**
```python
def test_booking_conflict_detection():
    # Create first booking: 2PM-4PM
    booking1 = booking_service.create_booking(
        resource_id=1,
        user_id=1,
        start_time=datetime(2025, 11, 15, 14, 0),
        end_time=datetime(2025, 11, 15, 16, 0)
    )
    assert booking1 is not None
    
    # Try overlapping booking: 3PM-5PM
    booking2, error = booking_service.create_booking(
        resource_id=1,
        user_id=2,
        start_time=datetime(2025, 11, 15, 15, 0),
        end_time=datetime(2025, 11, 15, 17, 0)
    )
    assert booking2 is None
    assert 'conflict' in error.lower()

def test_booking_status_transitions():
    booking = booking_service.create_booking(...)
    assert booking.status == 'pending'
    
    booking_service.approve_booking(booking.id, admin_id=1)
    assert booking.status == 'approved'
    
    booking_service.cancel_booking(booking.id)
    assert booking.status == 'cancelled'
```

**Coverage Target:** 85% for services

---

#### 1.1.3 Data Access Layer Tests (AiDD Required)
**Location:** `backend/tests/test_repositories/`

```python
def test_user_repository_create():
    user_repo = UserRepository()
    user = user_repo.create(
        full_name='Test User',
        email='test@example.com',
        password_hash='hashed',
        role='student'
    )
    assert user.id is not None
    assert user_repo.get_by_id(user.id) is not None

def test_resource_repository_pagination():
    resource_repo = ResourceRepository()
    resources, total = resource_repo.get_all(page=1, per_page=10)
    assert len(resources) <= 10
    assert total >= 0

def test_booking_repository_conflict_query():
    # Test the SQL query for conflict detection
    conflicts = booking_repo.find_conflicts(
        resource_id=1,
        start_time=datetime(...),
        end_time=datetime(...)
    )
    assert isinstance(conflicts, list)
```

**Coverage Target:** 80% for repositories

---

### 1.2 Frontend Unit Tests (Jest + React Testing Library)

#### 1.2.1 Component Tests
**Location:** `Campus_Resource_hub/src/components/__tests__/`

```typescript
// ResourceCard.test.tsx
describe('Resource Card', () => {
  it('renders resource information correctly', () => {
    const resource = {
      id: 1,
      name: 'Study Room A',
      category: 'study_room',
      location: 'Library Floor 2',
      status: 'available'
    };
    
    render(<ResourceCard resource={resource} />);
    expect(screen.getByText('Study Room A')).toBeInTheDocument();
    expect(screen.getByText('Library Floor 2')).toBeInTheDocument();
  });
  
  it('displays availability status badge', () => {
    const resource = { ...mockResource, status: 'unavailable' };
    render(<ResourceCard resource={resource} />);
    expect(screen.getByText('Unavailable')).toBeInTheDocument();
  });
});

// Login.test.tsx
describe('Login Component', () => {
  it('shows validation error for empty email', async () => {
    render(<AuthLogin />);
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    expect(await screen.findByText(/email is required/i)).toBeInTheDocument();
  });
  
  it('calls login API on form submit', async () => {
    const mockLogin = jest.fn().mockResolvedValue({ success: true });
    render(<AuthLogin />);
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'Password123!' }
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => expect(mockLogin).toHaveBeenCalled());
  });
});
```

**Coverage Target:** 70% for components

---

## 2. Integration Testing

### 2.1 API Integration Tests
**Location:** `backend/tests/test_integration/`

#### 2.1.1 Auth Flow Integration (AiDD Required)
```python
def test_full_auth_flow(client):
    # 1. Register
    response = client.post('/api/auth/register', json={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'SecurePass123!',
        'role': 'student'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['user']['email'] == 'test@example.com'
    
    # 2. Login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'SecurePass123!'
    })
    assert response.status_code == 200
    assert 'Set-Cookie' in response.headers
    
    # 3. Access protected endpoint
    response = client.get('/api/bookings/my-bookings')
    assert response.status_code == 200
    
    # 4. Logout
    response = client.post('/api/auth/logout')
    assert response.status_code == 200
    
    # 5. Try accessing protected endpoint after logout
    response = client.get('/api/bookings/my-bookings')
    assert response.status_code == 401
```

#### 2.1.2 Booking Workflow Integration
```python
def test_complete_booking_workflow(client, auth_headers):
    # 1. Browse resources
    response = client.get('/api/resources')
    assert response.status_code == 200
    resources = response.get_json()['resources']
    resource_id = resources[0]['id']
    
    # 2. Check availability
    response = client.get(f'/api/bookings/check-availability', json={
        'resource_id': resource_id,
        'start_time': '2025-11-15T14:00:00',
        'end_time': '2025-11-15T16:00:00'
    })
    assert response.status_code == 200
    assert response.get_json()['available'] is True
    
    # 3. Create booking
    response = client.post('/api/bookings', json={
        'resource_id': resource_id,
        'start_time': '2025-11-15T14:00:00',
        'end_time': '2025-11-15T16:00:00',
        'notes': 'Group study session'
    }, headers=auth_headers)
    assert response.status_code == 201
    booking_id = response.get_json()['booking']['id']
    
    # 4. View in my bookings
    response = client.get('/api/bookings/my-bookings', headers=auth_headers)
    assert response.status_code == 200
    bookings = response.get_json()['bookings']
    assert any(b['id'] == booking_id for b in bookings)
    
    # 5. Cancel booking
    response = client.delete(f'/api/bookings/{booking_id}', headers=auth_headers)
    assert response.status_code == 200
```

#### 2.1.3 Admin Workflow Integration
```python
def test_admin_moderation_workflow(client, admin_headers):
    # 1. Get flagged reviews
    response = client.get('/api/admin/reviews?flagged=true', headers=admin_headers)
    assert response.status_code == 200
    
    # 2. Approve/hide review
    response = client.put('/api/admin/reviews/1/hide', headers=admin_headers)
    assert response.status_code == 200
    
    # 3. View analytics
    response = client.get('/api/admin/analytics', headers=admin_headers)
    assert response.status_code == 200
```

**Coverage Target:** 70% of critical paths

---

### 2.2 Database Integration Tests

```python
def test_transaction_rollback_on_error():
    # Test that failed bookings don't leave partial data
    with pytest.raises(Exception):
        booking_service.create_booking_with_payment(...)
    
    # Verify no booking was created
    assert Booking.query.filter_by(user_id=1).count() == 0

def test_cascade_delete():
    # Create user with bookings
    user = User(...)
    booking = Booking(user_id=user.id, ...)
    db.session.add_all([user, booking])
    db.session.commit()
    
    # Delete user
    db.session.delete(user)
    db.session.commit()
    
    # Verify booking still exists (no cascade)
    assert Booking.query.get(booking.id) is not None
```

---

## 3. End-to-End (E2E) Testing

### 3.1 E2E Test Framework: Playwright
**Location:** `e2e/tests/`

#### 3.1.1 Critical User Journey (AiDD Required)
```typescript
// e2e/tests/booking-flow.spec.ts
test('student can complete full booking flow', async ({ page }) => {
  // 1. Navigate to login
  await page.goto('http://localhost:3000');
  
  // 2. Login
  await page.fill('[name="email"]', 'student@example.com');
  await page.fill('[name="password"]', 'Password123!');
  await page.click('button:has-text("Login")');
  
  // 3. Verify dashboard loaded
  await expect(page).toHaveURL(/dashboard/);
  await expect(page.locator('h1')).toContainText('Dashboard');
  
  // 4. Navigate to resources
  await page.click('text=Resources');
  await expect(page).toHaveURL(/resources/);
  
  // 5. Search for resource
  await page.fill('[placeholder*="Search"]', 'Study Room');
  await page.keyboard.press('Enter');
  
  // 6. Click on first resource
  await page.click('.resource-card:first-child');
  
  // 7. Create booking
  await page.click('button:has-text("Book Now")');
  await page.fill('[name="start_time"]', '2025-11-15T14:00');
  await page.fill('[name="end_time"]', '2025-11-15T16:00');
  await page.click('button:has-text("Confirm Booking")');
  
  // 8. Verify success
  await expect(page.locator('.toast-success')).toBeVisible();
  
  // 9. Check in My Bookings
  await page.click('text=My Bookings');
  await expect(page.locator('.booking-card')).toContainText('Study Room');
});
```

#### 3.1.2 Authentication E2E
```typescript
test('registration and login flow', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // Register
  await page.click('text=Sign Up');
  await page.fill('[name="name"]', 'New User');
  await page.fill('[name="email"]', `test${Date.now()}@example.com`);
  await page.fill('[name="password"]', 'SecurePass123!');
  await page.fill('[name="confirmPassword"]', 'SecurePass123!');
  await page.selectOption('[name="role"]', 'student');
  await page.click('button:has-text("Sign Up")');
  
  // Verify redirect to dashboard
  await expect(page).toHaveURL(/dashboard/);
});
```

#### 3.1.3 Admin E2E
```typescript
test('admin can moderate content', async ({ page }) => {
  // Login as admin
  await loginAsAdmin(page);
  
  // Navigate to moderation
  await page.click('text=Admin');
  await page.click('text=Moderation');
  
  // Hide flagged review
  await page.click('.review-item:first-child button:has-text("Hide")');
  await expect(page.locator('.toast-success')).toBeVisible();
});
```

**Coverage Target:** 5-10 critical paths

---

## 4. Security Testing

### 4.1 SQL Injection Tests (AiDD Required)
```python
def test_sql_injection_in_search():
    malicious_input = "'; DROP TABLE users; --"
    response = client.get(f'/api/resources?search={malicious_input}')
    assert response.status_code == 200  # Should not error
    
    # Verify table still exists
    assert User.query.count() > 0

def test_sql_injection_in_login():
    response = client.post('/api/auth/login', json={
        'email': "admin@example.com' OR '1'='1",
        'password': 'anything'
    })
    assert response.status_code == 401  # Should fail
```

### 4.2 XSS Protection Tests
```python
def test_xss_in_review_comment():
    response = client.post('/api/reviews', json={
        'resource_id': 1,
        'rating': 5,
        'comment': '<script>alert("XSS")</script>'
    }, headers=auth_headers)
    assert response.status_code == 201
    
    # Verify script tags stripped
    review = response.get_json()['review']
    assert '<script>' not in review['comment']
```

### 4.3 CSRF Protection Tests
```python
def test_csrf_protection_required():
    # Request without CSRF token
    response = client.post('/api/bookings', json={...})
    assert response.status_code == 403
    
    # Request with valid CSRF token
    csrf_token = get_csrf_token(client)
    response = client.post('/api/bookings', 
        json={...},
        headers={'X-CSRF-Token': csrf_token}
    )
    assert response.status_code == 201
```

### 4.4 Authentication & Authorization Tests
```python
def test_unauthorized_access_blocked():
    # No auth header
    response = client.get('/api/bookings/my-bookings')
    assert response.status_code == 401
    
def test_insufficient_permissions():
    # Student trying to access admin endpoint
    response = client.get('/api/admin/users', headers=student_headers)
    assert response.status_code == 403
    
def test_user_can_only_access_own_data():
    # User 1 trying to access User 2's bookings
    response = client.get('/api/bookings/123', headers=user1_headers)
    assert response.status_code == 403
```

---

## 5. Performance Testing

### 5.1 Load Testing (Locust)
**Locationlocustfile.py:**

```python
from locust import HttpUser, task, between

class CampusHubUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        self.client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
    
    @task(3)
    def browse_resources(self):
        self.client.get('/api/resources')
    
    @task(2)
    def view_resource(self):
        self.client.get('/api/resources/1')
    
    @task(1)
    def check_bookings(self):
        self.client.get('/api/bookings/my-bookings')
```

**Performance Targets:**
- Response time p95: < 500ms
- Response time p99: < 1000ms
- Concurrent users: 100
- Error rate: < 1%

### 5.2 Database Performance Tests
```python
def test_n_plus_one_queries():
    with query_counter() as counter:
        resources = Resource.query.all()
        for resource in resources:
            _ = resource.owner.full_name  # Should not trigger N queries
    
    assert counter.count < 10  # Including initial query + joins

def test_pagination_performance():
    # Create 1000 resources
    resources = [Resource(...) for _ in range(1000)]
    db.session.bulk_save_objects(resources)
    
    # Test paginated query
    start = time.time()
    result = resource_repo.get_all(page=1, per_page=20)
    duration = time.time() - start
    
    assert duration < 0.1  # Should be fast with indexes
```

---

## 6. Accessibility Testing

### 6.1 Automated Accessibility Tests
```typescript
// Using jest-axe
import { axe, toHaveNoViolations } from 'jest-axe';

test('Resources page has no accessibility violations', async () => {
  const { container } = render(<Resources />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});

test('Login form is keyboard accessible', () => {
  render(<AuthLogin />);
  const emailInput = screen.getByLabelText(/email/i);
  const passwordInput = screen.getByLabelText(/password/i);
  const submitButton = screen.getByRole('button', { name: /login/i });
  
  // Tab through form
  emailInput.focus();
  userEvent.tab();
  expect(passwordInput).toHaveFocus();
  userEvent.tab();
  expect(submitButton).toHaveFocus();
});
```

---

## 7. Test Data Management

### 7.1 Fixtures
```python
# conftest.py
@pytest.fixture
def sample_user(db):
    user = User(
        full_name='Test User',
        email='test@example.com',
        role='student',
        status='active'
    )
    user.set_password('Password123!')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def sample_resource(db, sample_user):
    resource = Resource(
        name='Test Study Room',
        owner_id=sample_user.id,
        category='study_room',
        location='Library Floor 1',
        status='published'
    )
    db.session.add(resource)
    db.session.commit()
    return resource
```

### 7.2 Database Seeding for E2E
```python
# scripts/seed_test_data.py
def seed_test_database():
    # Clear existing data
    db.session.query(Booking).delete()
    db.session.query(Resource).delete()
    db.session.query(User).delete()
    
    # Create test users
    users = [
        User(full_name='Student User', email='student@example.com', role='student'),
        User(full_name='Staff User', email='staff@example.com', role='staff'),
        User(full_name='Admin User', email='admin@example.com', role='admin'),
    ]
    for user in users:
        user.set_password('Password123!')
        db.session.add(user)
    
    # Create test resources
    resources = [
        Resource(name=f'Study Room {i}', owner_id=users[1].id, category='study_room')
        for i in range(1, 11)
    ]
    db.session.add_all(resources)
    
    db.session.commit()
```

---

## 8. CI/CD Integration

### 8.1 GitHub Actions Workflow
**.github/workflows/test.yml:**
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd Campus_Resource_hub
          npm install
      - name: Run tests
        run: |
          cd Campus_Resource_hub
          npm test -- --coverage
  
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start services
        run: docker-compose up -d
      - name: Run E2E tests
        run: npx playwright test
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: playwright-report
          path: playwright-report/
```

---

## 9. Test Execution Schedule

### 9.1 Development Phase
- **Pre-commit:** Run relevant unit tests
- **Pre-push:** Run all unit tests
- **Daily:** Run integration tests
- **Before PR merge:** Run full test suite

### 9.2 CI/CD Pipeline
- **On PR:** Unit + Integration tests
- **On merge to main:** Full suite including E2E
- **Nightly:** Performance + security tests
- **Weekly:** Full regression suite

---

## 10. Test Coverage Reports

### 10.1 Coverage Tools
- **Backend:** pytest-cov
- **Frontend:** Jest coverage
- **Reportcodeov**

### 10.2 Coverage Thresholds (Enforce in CI)
```ini
# pytest.ini
[coverage:run]
source = .
omit = tests/*,migrations/*

[coverage:report]
fail_under = 80
```

---

## 11. AiDD Compliance Checklist

**Section 10 Requirements:**

- [ ] ✅ Unit tests for booking logic (conflict detection, status transitions)
- [ ] ❌ Unit tests for Data Access Layer (CRUD operations)
- [ ] ❌ Integration test for auth flow (register → login → protected route)
- [ ] ❌ E2E test for booking scenario
- [ ] ❌ Security tests for SQL injection
- [ ] ✅ README includes test instructions
- [ ] ❌ Tests run with pytest (need to add more tests)

**Current Status:** 2/7 requirements met (29%)  
**Target:** 7/7 requirements (100%) by end of Phase 1

---

## 12. Known Gaps & Remediation

### Current Gaps
1. **No frontend tests** - Need Jest + RTL setup
2. **Minimal backend coverage** - < 10%
3. **No E2E tests** - Need Playwright setup
4. **No security tests** - SQL injection, XSS tests missing
5. **No performance tests** - Need Locust setup

### Remediation Plan (Phase 1)
1. Week 1: Set up test frameworks (Jest, Playwright)
2. Week 1: Write DAL unit tests (P1.9)
3. Week 2: Write auth integration tests (P1.9)
4. Week 2: Write booking E2E test (P1.9)
5. Week 2: Add security tests (P1.8, P1.9)

---

## 13. Success Metrics

**Phase 1 Goals:**
- Unit test coverage > 60%
- Integration test coverage > 50%
- 3+ E2E critical paths
- All AiDD requirements met
- Tests in CI pipeline

**Phase 2 Goals:**
- Unit test coverage > 80%
- Integration test coverage > 70%
- 10+ E2E scenarios
- Performance tests added
- <1% test failure rate

---

## Conclusion

**Testing Strategy:** Bottom-up approach starting with unit tests, building to integration, then E2E

**Priority:** Address AiDD requirements in Phase 1, expand coverage in Phase 2

**Success Criteria:** All tests passing in CI, coverage met, AiDD compliance achieved
