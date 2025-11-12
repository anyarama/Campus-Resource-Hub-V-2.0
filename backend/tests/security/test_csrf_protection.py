"""
CSRF Protection Security Tests
Tests CSRF token generation, validation, and enforcement.
"""

import pytest
from flask import session
from backend.app import create_app
from backend.extensions import db


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


class TestCSRFTokenEndpoint:
    """Test CSRF token generation endpoint."""
    
    def test_csrf_token_endpoint_returns_token(self, client):
        """Test GET /api/auth/csrf-token returns a token."""
        response = client.get('/api/auth/csrf-token')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'csrf_token' in data
        assert len(data['csrf_token']) > 0
    
    def test_csrf_token_is_unique_per_session(self, client):
        """Test each session gets a unique CSRF token."""
        response1 = client.get('/api/auth/csrf-token')
        token1 = response1.get_json()['csrf_token']
        
        # New client simulates new session
        client2 = client.application.test_client()
        response2 = client2.get('/api/auth/csrf-token')
        token2 = response2.get_json()['csrf_token']
        
        assert token1 != token2


class TestCSRFProtectionPOST:
    """Test CSRF protection on POST requests."""
    
    def test_post_without_csrf_token_fails(self, client):
        """Test POST request without CSRF token is rejected."""
        response = client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'SecurePass123'
        })
        
        # Should return 403 CSRF error
        assert response.status_code == 403
        data = response.get_json()
        assert 'CSRF' in data.get('error', '')
    
    def test_post_with_valid_csrf_token_succeeds(self, client):
        """Test POST request with valid CSRF token succeeds."""
        # Get CSRF token
        csrf_response = client.get('/api/auth/csrf-token')
        csrf_token = csrf_response.get_json()['csrf_token']
        
        # Make POST request with CSRF token
        response = client.post('/api/auth/register',
            json={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'SecurePass123'
            },
            headers={'X-CSRF-Token': csrf_token}
        )
        
        # Should succeed (or fail for other reasons, not CSRF)
        assert response.status_code != 403 or 'CSRF' not in response.get_json().get('error', '')
    
    def test_post_with_invalid_csrf_token_fails(self, client):
        """Test POST request with invalid CSRF token is rejected."""
        response = client.post('/api/auth/register',
            json={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'SecurePass123'
            },
            headers={'X-CSRF-Token': 'invalid-token-12345'}
        )
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'CSRF' in data.get('error', '')
    
    def test_post_with_expired_csrf_token_fails(self, client, app):
        """Test POST request with expired CSRF token is rejected."""
        # Get CSRF token
        csrf_response = client.get('/api/auth/csrf-token')
        csrf_token = csrf_response.get_json()['csrf_token']
        
        # Simulate token expiration by modifying session
        # (In real scenario, wait for WTF_CSRF_TIME_LIMIT seconds)
        # For testing, we'll use an old/stale token
        
        with client.session_transaction() as sess:
            sess.clear()  # Clear session to invalidate token
        
        response = client.post('/api/auth/register',
            json={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'SecurePass123'
            },
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 403


class TestCSRFProtectionPUT:
    """Test CSRF protection on PUT requests."""
    
    def test_put_without_csrf_token_fails(self, client):
        """Test PUT request without CSRF token is rejected."""
        response = client.put('/api/auth/me', json={
            'name': 'Updated Name'
        })
        
        assert response.status_code in [401,403]  # Either unauthorized or CSRF error
    
    def test_put_with_valid_csrf_token(self, client):
        """Test PUT request with valid CSRF token."""
        # Get CSRF token
        csrf_response = client.get('/api/auth/csrf-token')
        csrf_token = csrf_response.get_json()['csrf_token']
        
        response = client.put('/api/auth/me',
            json={'name': 'Updated Name'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        # Should not fail due to CSRF (may fail due to auth)
        if response.status_code == 403:
            data = response.get_json()
            assert 'CSRF' not in data.get('error', '')


class TestCSRFProtectionDELETE:
    """Test CSRF protection on DELETE requests."""
    
    def test_delete_without_csrf_token_fails(self, client):
        """Test DELETE request without CSRF token is rejected."""
        response = client.delete('/api/resources/1')
        
        assert response.status_code in [403, 404, 401]


class TestCSRFProtectionGET:
    """Test CSRF protection does NOT apply to GET requests."""
    
    def test_get_without_csrf_token_succeeds(self, client):
        """Test GET requests work without CSRF token."""
        response = client.get('/api/auth/me')
        
        # Should not fail due to CSRF (may fail due to auth with 401)
        assert response.status_code != 403 or 'CSRF' not in response.get_json().get('error', '')
    
    def test_health_check_without_csrf_token(self, client):
        """Test health check endpoint works without CSRF."""
        response = client.get('/health')
        
        assert response.status_code == 200


class TestCSRFHeaderVariations:
    """Test different CSRF header formats."""
    
    def test_csrf_token_in_x_csrf_token_header(self, client):
        """Test CSRF token in X-CSRF-Token header."""
        csrf_response = client.get('/api/auth/csrf-token')
        csrf_token = csrf_response.get_json()['csrf_token']
        
        response = client.post('/api/auth/check-email',
            json={'email': 'test@example.com'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        # Should not fail due to CSRF
        assert response.status_code != 403 or 'CSRF' not in response.get_json().get('error', '')
    
    def test_csrf_token_in_x_csrftoken_header(self, client):
        """Test CSRF token in X-CSRFToken header (no dash)."""
        csrf_response = client.get('/api/auth/csrf-token')
        csrf_token = csrf_response.get_json()['csrf_token']
        
        response = client.post('/api/auth/check-email',
            json={'email': 'test@example.com'},
            headers={'X-CSRFToken': csrf_token}
        )
        
        # Should not fail due to CSRF
        assert response.status_code != 403 or 'CSRF' not in response.get_json().get('error', '')


class TestCSRFSecurityBoundaries:
    """Test CSRF security boundaries and edge cases."""
    
    def test_csrf_token_not_in_response_body(self, client):
        """Test CSRF token is not leaked in regular API responses."""
        response = client.get('/health')
        data = response.get_json()
        
        # CSRF token should not appear in response
        assert 'csrf_token' not in data
        assert 'csrf' not in str(data).lower() or 'csrf_token' in data  # Allow in csrf endpoint
    
    def test_csrf_token_reuse_across_requests(self, client):
        """Test same CSRF token can be reused within session."""
        csrf_response = client.get('/api/auth/csrf-token')
        csrf_token = csrf_response.get_json()['csrf_token']
        
        # First request
        response1 = client.post('/api/auth/check-email',
            json={'email': 'test1@example.com'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        # Second request with same token
        response2 = client.post('/api/auth/check-email',
            json={'email': 'test2@example.com'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        # Both should work
        assert response1.status_code != 403 or 'CSRF' not in response1.get_json().get('error', '')
        assert response2.status_code != 403 or 'CSRF' not in response2.get_json().get('error', '')
    
    def test_csrf_token_from_different_session_fails(self, client):
        """Test CSRF token from one session doesn't work in another."""
        # Get token in first client
        csrf_response = client.get('/api/auth/csrf-token')
        csrf_token = csrf_response.get_json()['csrf_token']
        
        # Create new client (new session)
        client2 = client.application.test_client()
        
        # Try to use first client's token in second client
        response = client2.post('/api/auth/check-email',
            json={'email': 'test@example.com'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 403


class TestCSRFConfigurationSettings:
    """Test CSRF configuration is correct."""
    
    def test_csrf_enabled_in_development(self, app):
        """Test CSRF is enabled in development environment."""
        with app.app_context():
            assert app.config['WTF_CSRF_ENABLED'] is True
    
    def test_csrf_time_limit_set(self, app):
        """Test CSRF time limit is configured."""
        with app.app_context():
            assert app.config['WTF_CSRF_TIME_LIMIT'] is not None
            assert isinstance(app.config['WTF_CSRF_TIME_LIMIT'], int)
            assert app.config['WTF_CSRF_TIME_LIMIT'] > 0
    
    def test_csrf_headers_configured(self, app):
        """Test CSRF headers are configured."""
        with app.app_context():
            assert 'WTF_CSRF_HEADERS' in app.config
            csrf_headers = app.config['WTF_CSRF_HEADERS']
            assert 'X-CSRF-Token' in csrf_headers or 'X-CSRFToken' in csrf_headers


# Integration test with authentication
class TestCSRFWithAuthentication:
    """Test CSRF protection works with authenticated requests."""
    
    def test_authenticated_post_requires_csrf(self, client):
        """Test authenticated POST still requires CSRF token."""
        # This would require setting up a user and logging in first
        # For now, we test that CSRF is checked before auth
        response = client.post('/api/auth/logout', json={})
        
        # Should fail with CSRF error before checking auth
        assert response.status_code == 403


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
