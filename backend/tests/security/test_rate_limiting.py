"""
Rate Limiting Security Tests
Tests for Flask-Limiter configuration and rate limit enforcement on auth endpoints.
"""

import pytest
from backend.app import create_app
from backend.extensions import db
from backend.models.user import User


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    app = create_app('testing')
    
    # Create tables
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user in the database."""
    with app.app_context():
        user = User(
            name='Test User',
            email='test@example.com',
            role='student'
        )
        user.set_password('TestPass123')
        db.session.add(user)
        db.session.commit()
        
        # Return user data (not the object itself since it's session-bound)
        return {
            'id': user.id,
            'email': user.email,
            'name': user.name
        }


class TestRateLimitConfiguration:
    """Test rate limiter is properly configured."""
    
    def test_rate_limiter_enabled(self, app):
        """Verify Flask-Limiter is enabled in the app."""
        from backend.extensions import limiter
        
        assert limiter is not None
        assert limiter._app is not None
    
    def test_default_limits_configured(self, app):
        """Verify default rate limits are set."""
        from backend.extensions import limiter
        
        # Check default limits exist
        assert limiter._default_limits is not None
        assert len(limiter._default_limits) > 0


class TestRegisterEndpointRateLimit:
    """Test rate limiting on /api/auth/register endpoint (5 per 15 minutes)."""
    
    def test_register_allows_requests_under_limit(self, client):
        """Verify requests under the rate limit are allowed."""
        # Make 5 requests (should all succeed or fail with validation errors, not 429)
        for i in range(5):
            response = client.post('/api/auth/register', json={
                'name': f'User {i}',
                'email': f'user{i}@example.com',
                'password': 'TestPass123'
            })
            
            # Should not return 429
            assert response.status_code != 429
    
    def test_register_blocks_requests_over_limit(self, client):
        """Verify requests exceeding rate limit are blocked with 429."""
        # Make 6 requests (6th should be rate limited)
        for i in range(5):
            client.post('/api/auth/register', json={
                'name': f'User {i}',
                'email': f'user{i}@example.com',
                'password': 'TestPass123'
            })
        
        # 6th request should be rate limited
        response = client.post('/api/auth/register', json={
            'name': 'User 6',
            'email': 'user6@example.com',
            'password': 'TestPass123'
        })
        
        assert response.status_code == 429
    
    def test_register_rate_limit_error_format(self, client):
        """Verify rate limit error response has correct format."""
        # Exhaust rate limit
        for i in range(5):
            client.post('/api/auth/register', json={
                'name': f'User {i}',
                'email': f'user{i}@example.com',
                'password': 'TestPass123'
            })
        
        # Trigger rate limit
        response = client.post('/api/auth/register', json={
            'name': 'User 6',
            'email': 'user6@example.com',
            'password': 'TestPass123'
        })
        
        assert response.status_code == 429
        data = response.get_json()
        
        assert 'error' in data
        assert data['error'] == 'Too Many Requests'
        assert 'message' in data
        assert 'rate limit' in data['message'].lower()
        assert 'status' in data
        assert data['status'] == 429


class TestLoginEndpointRateLimit:
    """Test rate limiting on /api/auth/login endpoint (10 per 15 minutes)."""
    
    def test_login_allows_requests_under_limit(self, client, test_user):
        """Verify requests under the rate limit are allowed."""
        # Make 10 login attempts (should all get 401 or 200, not 429)
        for i in range(10):
            response = client.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'TestPass123'
            })
            
            # Should not return 429
            assert response.status_code != 429
    
    def test_login_blocks_requests_over_limit(self, client, test_user):
        """Verify requests exceeding rate limit are blocked with 429."""
        # Make 11 login attempts (11th should be rate limited)
        for i in range(10):
            client.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'TestPass123'
            })
        
        # 11th request should be rate limited
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPass123'
        })
        
        assert response.status_code == 429
    
    def test_login_rate_limit_error_format(self, client, test_user):
        """Verify rate limit error response has correct format."""
        # Exhaust rate limit
        for i in range(10):
            client.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'TestPass123'
            })
        
        # Trigger rate limit
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPass123'
        })
        
        assert response.status_code == 429
        data = response.get_json()
        
        assert 'error' in data
        assert data['error'] == 'Too Many Requests'
        assert 'retry_after' in data


class TestChangePasswordEndpointRateLimit:
    """Test rate limiting on /api/auth/change-password endpoint (3 per hour)."""
    
    def test_change_password_allows_requests_under_limit(self, client, test_user):
        """Verify requests under the rate limit are allowed."""
        # Login first to get session
        client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPass123'
        })
        
        # Make 3 password change attempts (should all get 400 or 200, not 429)
        for i in range(3):
            response = client.post('/api/auth/change-password', json={
                'current_password': 'TestPass123',
                'new_password': f'NewPass{i}23'
            })
            
            # Should not return 429
            assert response.status_code != 429
    
    def test_change_password_blocks_requests_over_limit(self, client, test_user):
        """Verify requests exceeding rate limit are blocked with 429."""
        # Login first
        client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPass123'
        })
        
        # Make 4 password change attempts (4th should be rate limited)
        for i in range(3):
            client.post('/api/auth/change-password', json={
                'current_password': 'TestPass123',
                'new_password': f'NewPass{i}23'
            })
        
        # 4th request should be rate limited
        response = client.post('/api/auth/change-password', json={
            'current_password': 'TestPass123',
            'new_password': 'NewPass423'
        })
        
        assert response.status_code == 429


class TestRateLimitErrorHandler:
    """Test custom 429 error handler."""
    
    def test_rate_limit_response_includes_retry_after(self, client):
        """Verify 429 responses include retry_after information."""
        # Exhaust register endpoint limit
        for i in range(5):
            client.post('/api/auth/register', json={
                'name': f'User {i}',
                'email': f'user{i}@example.com',
                'password': 'TestPass123'
            })
        
        # Trigger rate limit
        response = client.post('/api/auth/register', json={
            'name': 'User 6',
            'email': 'user6@example.com',
            'password': 'TestPass123'
        })
        
        assert response.status_code == 429
        data = response.get_json()
        
        # Check retry_after is present
        assert 'retry_after' in data
    
    def test_rate_limit_response_json_format(self, client):
        """Verify 429 responses are valid JSON."""
        # Exhaust login limit
        for i in range(10):
            client.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'TestPass123'
            })
        
        # Trigger rate limit
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPass123'
        })
        
        assert response.status_code == 429
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        assert data is not None
        assert isinstance(data, dict)


class TestRateLimitIndependence:
    """Test that rate limits are independent across endpoints."""
    
    def test_register_and_login_limits_independent(self, client, test_user):
        """Verify exhausting register limit doesn't affect login limit."""
        # Exhaust register limit
        for i in range(5):
            client.post('/api/auth/register', json={
                'name': f'User {i}',
                'email': f'user{i}@example.com',
                'password': 'TestPass123'
            })
        
        # Verify register is rate limited
        response = client.post('/api/auth/register', json={
            'name': 'User 6',
            'email': 'user6@example.com',
            'password': 'TestPass123'
        })
        assert response.status_code == 429
        
        # Login should still work (not rate limited)
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPass123'
        })
        assert response.status_code != 429
        # Should be 200 (success) or 401 (auth failure), but not 429
        assert response.status_code in [200, 401]


class TestRateLimitSecurity:
    """Test security aspects of rate limiting."""
    
    def test_rate_limit_prevents_brute_force_login(self, client, test_user):
        """Verify rate limiting can prevent brute force attacks on login."""
        # Attempt multiple wrong passwords
        for i in range(10):
            response = client.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': f'WrongPass{i}'
            })
            
            # First 10 should fail with 401
            assert response.status_code == 401
        
        # 11th attempt should be rate limited
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'AnotherWrongPass'
        })
        
        assert response.status_code == 429
    
    def test_rate_limit_prevents_account_enumeration(self, client):
        """Verify rate limiting mitigates account enumeration attacks."""
        # Try to enumerate accounts by registering with many emails
        for i in range(5):
            client.post('/api/auth/register', json={
                'name': f'Test User {i}',
                'email': f'test{i}@example.com',
                'password': 'TestPass123'
            })
        
        # Further enumeration attempts should be blocked
        response = client.post('/api/auth/register', json={
            'name': 'Test User 6',
            'email': 'test6@example.com',
            'password': 'TestPass123'
        })
        
        assert response.status_code == 429
