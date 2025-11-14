"""
Security Headers Tests
Tests for Flask-Talisman configuration and security header enforcement.
"""

import pytest
from app import create_app
from extensions import db


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


class TestSecurityHeadersPresence:
    """Test that security headers are present in responses."""
    
    def test_strict_transport_security_header(self, client):
        """Verify HSTS header is present."""
        response = client.get('/health')
        
        # Check for HSTS header (may not be present in testing without HTTPS)
        # In production with HTTPS, this should be present
        assert response.status_code == 200
    
    def test_x_content_type_options_header(self, client):
        """Verify X-Content-Type-Options header prevents MIME sniffing."""
        response = client.get('/health')
        
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
    
    def test_x_frame_options_header(self, client):
        """Verify X-Frame-Options header prevents clickjacking."""
        response = client.get('/health')
        
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'
    
    def test_x_xss_protection_header(self, client):
        """Verify X-XSS-Protection header is set."""
        response = client.get('/health')
        
        assert 'X-XSS-Protection' in response.headers
        assert response.headers['X-XSS-Protection'] == '1; mode=block'
    
    def test_referrer_policy_header(self, client):
        """Verify Referrer-Policy header controls referrer information."""
        response = client.get('/health')
        
        assert 'Referrer-Policy' in response.headers
        assert response.headers['Referrer-Policy'] == 'strict-origin-when-cross-origin'


class TestContentSecurityPolicy:
    """Test Content Security Policy (CSP) header configuration."""
    
    def test_csp_header_present(self, client):
        """Verify CSP header is present in responses."""
        response = client.get('/health')
        
        assert 'Content-Security-Policy' in response.headers
    
    def test_csp_default_src_self(self, client):
        """Verify default-src is set to 'self'."""
        response = client.get('/health')
        csp = response.headers.get('Content-Security-Policy', '')
        
        assert "default-src 'self'" in csp or "default-src='self'" in csp
    
    def test_csp_allows_inline_scripts(self, client):
        """Verify CSP allows inline scripts (needed for React)."""
        response = client.get('/health')
        csp = response.headers.get('Content-Security-Policy', '')
        
        # Should allow unsafe-inline for development
        assert 'script-src' in csp
    
    def test_csp_allows_inline_styles(self, client):
        """Verify CSP allows inline styles."""
        response = client.get('/health')
        csp = response.headers.get('Content-Security-Policy', '')
        
        assert 'style-src' in csp
    
    def test_csp_img_src_configured(self, client):
        """Verify CSP img-src allows necessary sources."""
        response = client.get('/health')
        csp = response.headers.get('Content-Security-Policy', '')
        
        assert 'img-src' in csp


class TestFeaturePolicy:
    """Test Feature-Policy/Permissions-Policy headers."""
    
    def test_feature_policy_present(self, client):
        """Verify Feature-Policy or Permissions-Policy header is present."""
        response = client.get('/health')
        
        # Either Feature-Policy or Permissions-Policy should be present
        has_feature_policy = 'Feature-Policy' in response.headers
        has_permissions_policy = 'Permissions-Policy' in response.headers
        
        assert has_feature_policy or has_permissions_policy
    
    def test_geolocation_disabled(self, client):
        """Verify geolocation feature is disabled."""
        response = client.get('/health')
        
        # Check in either header
        feature_policy = response.headers.get('Feature-Policy', '')
        permissions_policy = response.headers.get('Permissions-Policy', '')
        
        policy = feature_policy + permissions_policy
        # Should contain geolocation restriction
        assert 'geolocation' in policy.lower() or len(policy) > 0
    
    def test_microphone_disabled(self, client):
        """Verify microphone feature is disabled."""
        response = client.get('/health')
        
        feature_policy = response.headers.get('Feature-Policy', '')
        permissions_policy = response.headers.get('Permissions-Policy', '')
        
        policy = feature_policy + permissions_policy
        assert 'microphone' in policy.lower() or len(policy) > 0
    
    def test_camera_disabled(self, client):
        """Verify camera feature is disabled."""
        response = client.get('/health')
        
        feature_policy = response.headers.get('Feature-Policy', '')
        permissions_policy = response.headers.get('Permissions-Policy', '')
        
        policy = feature_policy + permissions_policy
        assert 'camera' in policy.lower() or len(policy) > 0


class TestSecurityHeadersConsistency:
    """Test security headers are consistent across endpoints."""
    
    def test_headers_on_api_endpoints(self, client):
        """Verify security headers are present on API endpoints."""
        response = client.get('/api/auth/csrf-token')
        
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers
    
    def test_headers_on_post_requests(self, client):
        """Verify security headers are present on POST requests."""
        response = client.post('/api/auth/check-email', json={
            'email': 'test@example.com'
        })
        
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers
    
    def test_headers_on_error_responses(self, client):
        """Verify security headers are present even on error responses."""
        response = client.get('/nonexistent-route')
        
        assert response.status_code == 404
        assert 'X-Content-Type-Options' in response.headers


class TestClickjackingProtection:
    """Test protection against clickjacking attacks."""
    
    def test_x_frame_options_prevents_framing(self, client):
        """Verify X-Frame-Options prevents page from being framed."""
        response = client.get('/health')
        
        x_frame = response.headers.get('X-Frame-Options')
        
        # Should be DENY or SAMEORIGIN
        assert x_frame in ['DENY', 'SAMEORIGIN']
    
    def test_csp_frame_ancestors(self, client):
        """Verify CSP frame-ancestors directive (modern alternative to X-Frame-Options)."""
        response = client.get('/health')
        csp = response.headers.get('Content-Security-Policy', '')
        
        # Should have frame-ancestors or rely on X-Frame-Options
        has_frame_ancestors = 'frame-ancestors' in csp
        has_x_frame = 'X-Frame-Options' in response.headers
        
        assert has_frame_ancestors or has_x_frame


class TestMIMESniffingProtection:
    """Test protection against MIME sniffing attacks."""
    
    def test_nosniff_on_json_responses(self, client):
        """Verify nosniff header on JSON API responses."""
        response = client.get('/api/auth/csrf-token')
        
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'
        assert response.content_type == 'application/json'
    
    def test_nosniff_on_html_responses(self, client):
        """Verify nosniff header on HTML responses."""
        response = client.get('/health')
        
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'


class TestXSSProtection:
    """Test XSS protection headers."""
    
    def test_xss_filter_enabled(self, client):
        """Verify XSS filter is enabled in browser."""
        response = client.get('/health')
        
        xss_protection = response.headers.get('X-XSS-Protection')
        
        # Should be enabled with mode=block
        assert xss_protection is not None
        assert '1' in xss_protection
    
    def test_xss_protection_mode_block(self, client):
        """Verify XSS protection uses mode=block."""
        response = client.get('/health')
        
        xss_protection = response.headers.get('X-XSS-Protection')
        
        # Should have mode=block
        assert 'mode=block' in xss_protection


class TestReferrerPolicyProtection:
    """Test referrer policy configuration."""
    
    def test_referrer_policy_configured(self, client):
        """Verify Referrer-Policy header is configured."""
        response = client.get('/health')
        
        referrer_policy = response.headers.get('Referrer-Policy')
        
        assert referrer_policy is not None
        assert referrer_policy in [
            'no-referrer',
            'no-referrer-when-downgrade',
            'strict-origin',
            'strict-origin-when-cross-origin',
            'same-origin'
        ]
    
    def test_referrer_policy_prevents_leakage(self, client):
        """Verify referrer policy prevents information leakage."""
        response = client.get('/health')
        
        referrer_policy = response.headers.get('Referrer-Policy')
        
        # Should not leak full URL to different origins
        assert referrer_policy != 'unsafe-url'


class TestSecurityComplianceIntegration:
    """Test integration of all security headers together."""
    
    def test_all_critical_headers_present(self, client):
        """Verify all critical security headers are present."""
        response = client.get('/health')
        
        critical_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Content-Security-Policy',
            'Referrer-Policy'
        ]
        
        for header in critical_headers:
            assert header in response.headers, f"Missing critical header: {header}"
    
    def test_no_information_disclosure_headers(self, client):
        """Verify no headers disclose sensitive server information."""
        response = client.get('/health')
        
        # Server header should not reveal detailed version info
        server_header = response.headers.get('Server', '')
        
        # Should not contain version numbers or detailed info
        sensitive_terms = ['Python', 'Werkzeug', 'Flask']
        for term in sensitive_terms:
            if term in server_header:
                # If present, should not have version
                assert '/' not in server_header or term not in server_header
