"""
Test Suite: Admin API Testing & Security
Phase 1 - Task 5

This test suite covers:
1. RBAC enforcement - All endpoints reject non-admin users (403)
2. User management - Role and status changes with edge cases
3. Analytics - System-wide statistics
4. User listing - Pagination and filtering
5. Resource moderation - Admin resource management
6. Review moderation - Hide/unhide/flagged reviews
7. Activity reports - Time-based activity data
8. Rate limiting - 100 admin actions per hour
9. CSRF protection - All mutation endpoints
10. Security headers - X-Content-Type-Options

Total expected tests: ~35
"""

import pytest
from flask import Flask
from models.user import User
from models.resource import Resource
from models.booking import Booking
from models.message import Message
from models.review import Review
from extensions import db
from datetime import datetime, timedelta


# ============================================================================
# Helper Functions
# ============================================================================

def login_user(client, email: str, password: str) -> str:
    """
    Helper function to log in a user and return CSRF token.
    
    Args:
        client: Flask test client
        email: User email
        password: User password
    
    Returns:
        str: CSRF token (empty string if CSRF is disabled)
    """
    response = client.post('/api/auth/login', json={
        'email': email,
        'password': password
    })
    assert response.status_code == 200
    # Return empty string if csrf_token not in response (CSRF disabled in tests)
    return response.json.get('csrf_token', '')


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    from app import create_app
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'test-secret-key-for-testing-only',
        'RATELIMIT_ENABLED': True,
        'RATELIMIT_STORAGE_URL': 'memory://'
    })
    
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
def student_user(app):
    """Create a student user for testing."""
    with app.app_context():
        user = User(
            name='Test Student',
            email='student@test.com',
            password='Password123!',
            role='student'
        )
        db.session.add(user)
        db.session.commit()
        
        return {
            'id': user.id,
            'email': user.email,
            'password': 'Password123!',
            'role': 'student'
        }


@pytest.fixture
def staff_user(app):
    """Create a staff user for testing."""
    with app.app_context():
        user = User(
            name='Test Staff',
            email='staff@test.com',
            password='Password123!',
            role='staff'
        )
        db.session.add(user)
        db.session.commit()
        
        return {
            'id': user.id,
            'email': user.email,
            'password': 'Password123!',
            'role': 'staff'
        }


@pytest.fixture
def admin_user(app):
    """Create an admin user for testing."""
    with app.app_context():
        user = User(
            name='Test Admin',
            email='admin@test.com',
            password='AdminPass123!',
            role='admin'
        )
        db.session.add(user)
        db.session.commit()
        
        return {
            'id': user.id,
            'email': user.email,
            'password': 'AdminPass123!',
            'role': 'admin'
        }


@pytest.fixture
def test_resource(app, staff_user):
    """Create a test resource."""
    with app.app_context():
        resource = Resource(
            owner_id=staff_user['id'],
            title='Test Resource',
            description='Test description',
            location='Test Location'
        )
        resource.status = 'published'  # Set status after creation
        db.session.add(resource)
        db.session.commit()
        return resource.id


@pytest.fixture
def test_review(app, student_user, test_resource):
    """Create a test review."""
    with app.app_context():
        review = Review(
            resource_id=test_resource,
            reviewer_id=student_user['id'],
            rating=5,
            comment='Great resource!'
        )
        # is_flagged and is_hidden default to False automatically
        db.session.add(review)
        db.session.commit()
        return review.id


# ============================================================================
# Test: RBAC Enforcement - Non-Admin Rejection
# ============================================================================

class TestAdminRBAC:
    """Test that all admin endpoints reject non-admin users (403 Forbidden)"""
    
    def test_analytics_requires_admin(self, client, app, student_user):
        """Test that GET /api/admin/analytics requires admin role."""
        login_user(client, student_user['email'], student_user['password'])
        
        response = client.get('/api/admin/analytics')
        
        assert response.status_code == 403
        assert 'Forbidden' in response.json.get('error', '')
        assert 'Admin role required' in response.json.get('message', '')
    
    def test_get_users_requires_admin(self, client, app, student_user):
        """Test that GET /api/admin/users requires admin role."""
        login_user(client, student_user['email'], student_user['password'])
        
        response = client.get('/api/admin/users')
        
        assert response.status_code == 403
        assert 'Forbidden' in response.json.get('error', '')
    
    def test_update_user_role_requires_admin(self, client, app, student_user, staff_user):
        """Test that PUT /api/admin/users/:id/role requires admin role."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        response = client.put(
            f'/api/admin/users/{staff_user["id"]}/role',
            json={'role': 'admin'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 403
        assert 'Forbidden' in response.json.get('error', '')
    
    def test_update_user_status_requires_admin(self, client, app, student_user, staff_user):
        """Test that PUT /api/admin/users/:id/status requires admin role."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        response = client.put(
            f'/api/admin/users/{staff_user["id"]}/status',
            json={'status': 'suspended'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 403
        assert 'Forbidden' in response.json.get('error', '')
    
    def test_get_resources_moderation_requires_admin(self, client, app, student_user):
        """Test that GET /api/admin/resources requires admin role."""
        login_user(client, student_user['email'], student_user['password'])
        
        response = client.get('/api/admin/resources')
        
        assert response.status_code == 403
        assert 'Forbidden' in response.json.get('error', '')
    
    def test_get_flagged_reviews_requires_admin(self, client, app, student_user):
        """Test that GET /api/admin/reviews/flagged requires admin role."""
        login_user(client, student_user['email'], student_user['password'])
        
        response = client.get('/api/admin/reviews/flagged')
        
        assert response.status_code == 403
        assert 'Forbidden' in response.json.get('error', '')
    
    def test_hide_review_requires_admin(self, client, app, student_user, test_review):
        """Test that POST /api/admin/reviews/:id/hide requires admin role."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        response = client.post(
            f'/api/admin/reviews/{test_review}/hide',
            json={'moderation_notes': 'Test'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 403
        assert 'Forbidden' in response.json.get('error', '')
    
    def test_unhide_review_requires_admin(self, client, app, student_user, test_review):
        """Test that POST /api/admin/reviews/:id/unhide requires admin role."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        response = client.post(
            f'/api/admin/reviews/{test_review}/unhide',
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 403
        assert 'Forbidden' in response.json.get('error', '')
    
    def test_activity_report_requires_admin(self, client, app, student_user):
        """Test that GET /api/admin/reports/activity requires admin role."""
        login_user(client, student_user['email'], student_user['password'])
        
        response = client.get('/api/admin/reports/activity')
        
        assert response.status_code == 403
        assert 'Forbidden' in response.json.get('error', '')
    
    def test_staff_cannot_access_admin_endpoints(self, client, app, staff_user):
        """Test that staff users also cannot access admin endpoints."""
        login_user(client, staff_user['email'], staff_user['password'])
        
        response = client.get('/api/admin/analytics')
        
        assert response.status_code == 403
        assert 'Forbidden' in response.json.get('error', '')


# ============================================================================
# Test: System Analytics
# ============================================================================

class TestSystemAnalytics:
    """Test system-wide analytics endpoint"""
    
    def test_get_analytics_success(self, client, app, admin_user):
        """Test that admin can retrieve system analytics."""
        login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.get('/api/admin/analytics')
        
        assert response.status_code == 200
        analytics = response.json
        
        # Check structure
        assert 'users' in analytics
        assert 'resources' in analytics
        assert 'bookings' in analytics
        assert 'messages' in analytics
        assert 'reviews' in analytics
        
        # Check user stats
        assert 'total' in analytics['users']
        assert 'active' in analytics['users']
        assert 'by_role' in analytics['users']
        
        # Check resources stats
        assert 'total' in analytics['resources']
        assert 'published' in analytics['resources']
    
    def test_analytics_has_security_headers(self, client, app, admin_user):
        """Test that analytics response has security headers."""
        login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.get('/api/admin/analytics')
        
        assert response.status_code == 200
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'


# ============================================================================
# Test: User Management
# ============================================================================

class TestUserManagement:
    """Test user role and status management"""
    
    def test_update_user_role_success(self, client, app, admin_user, student_user):
        """Test that admin can update user role."""
        csrf_token = login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.put(
            f'/api/admin/users/{student_user["id"]}/role',
            json={'role': 'staff'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 200
        assert 'User role updated successfully' in response.json.get('message', '')
        assert response.json['user']['role'] == 'staff'
    
    def test_update_user_role_requires_csrf(self, client, app, admin_user, student_user):
        """Test that role update requires CSRF token."""
        login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.put(
            f'/api/admin/users/{student_user["id"]}/role',
            json={'role': 'staff'}
        )
        
        assert response.status_code == 400
    
    def test_update_user_role_invalid_role(self, client, app, admin_user, student_user):
        """Test that invalid roles are rejected."""
        csrf_token = login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.put(
            f'/api/admin/users/{student_user["id"]}/role',
            json={'role': 'superadmin'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'Invalid role' in response.json.get('message', '')
    
    def test_admin_cannot_change_own_role(self, client, app, admin_user):
        """Test that admin cannot demote themselves."""
        csrf_token = login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.put(
            f'/api/admin/users/{admin_user["id"]}/role',
            json={'role': 'student'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 403
        assert 'cannot change your own role' in response.json.get('message', '')
    
    def test_update_user_status_success(self, client, app, admin_user, student_user):
        """Test that admin can update user status."""
        csrf_token = login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.put(
            f'/api/admin/users/{student_user["id"]}/status',
            json={'status': 'suspended'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 200
        assert 'User status updated successfully' in response.json.get('message', '')
        assert response.json['user']['status'] == 'suspended'
    
    def test_admin_cannot_change_own_status(self, client, app, admin_user):
        """Test that admin cannot suspend themselves."""
        csrf_token = login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.put(
            f'/api/admin/users/{admin_user["id"]}/status',
            json={'status': 'suspended'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 403
        assert 'cannot change your own status' in response.json.get('message', '')


# ============================================================================
# Test: User Listing
# ============================================================================

class TestUserListing:
    """Test user listing with pagination and filtering"""
    
    def test_get_users_list_success(self, client, app, admin_user):
        """Test that admin can get list of all users."""
        login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.get('/api/admin/users')
        
        assert response.status_code == 200
        assert 'users' in response.json
        assert 'pagination' in response.json
        assert isinstance(response.json['users'], list)
    
    def test_get_users_filter_by_role(self, client, app, admin_user):
        """Test filtering users by role."""
        login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.get('/api/admin/users?role=student')
        
        assert response.status_code == 200
        assert 'users' in response.json
        # All returned users should be students
        for user in response.json['users']:
            assert user['role'] == 'student'


# ============================================================================
# Test: Resource Moderation
# ============================================================================

class TestResourceModeration:
    """Test resource moderation endpoints"""
    
    def test_get_resources_for_moderation(self, client, app, admin_user):
        """Test that admin can get resources for moderation."""
        login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.get('/api/admin/resources')
        
        assert response.status_code == 200
        assert 'resources' in response.json
        assert 'pagination' in response.json
    
    def test_get_resources_filter_by_status(self, client, app, admin_user):
        """Test filtering resources by status."""
        login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.get('/api/admin/resources?status=published')
        
        assert response.status_code == 200
        assert 'resources' in response.json


# ============================================================================
# Test: Review Moderation
# ============================================================================

class TestReviewModeration:
    """Test review moderation endpoints"""
    
    def test_get_flagged_reviews(self, client, app, admin_user):
        """Test that admin can get flagged reviews."""
        login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.get('/api/admin/reviews/flagged')
        
        assert response.status_code == 200
        assert 'reviews' in response.json or 'pagination' in response.json
    
    def test_hide_review_success(self, client, app, admin_user, test_review):
        """Test that admin can hide a review."""
        csrf_token = login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.post(
            f'/api/admin/reviews/{test_review}/hide',
            json={'moderation_notes': 'Inappropriate content'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 200
        assert 'Review hidden successfully' in response.json.get('message', '')
    
    def test_hide_review_requires_csrf(self, client, app, admin_user, test_review):
        """Test that hiding review requires CSRF token."""
        login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.post(
            f'/api/admin/reviews/{test_review}/hide',
            json={'moderation_notes': 'Test'}
        )
        
        assert response.status_code == 400
    
    def test_unhide_review_success(self, client, app, admin_user, test_review):
        """Test that admin can unhide a review."""
        # First hide it
        csrf_token = login_user(client, admin_user['email'], admin_user['password'])
        client.post(
            f'/api/admin/reviews/{test_review}/hide',
            json={'moderation_notes': 'Test'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        # Then unhide it
        response = client.post(
            f'/api/admin/reviews/{test_review}/unhide',
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 200
        assert 'Review unhidden successfully' in response.json.get('message', '')


# ============================================================================
# Test: Activity Reports
# ============================================================================

class TestActivityReports:
    """Test activity reporting endpoints"""
    
    def test_get_activity_report_success(self, client, app, admin_user):
        """Test that admin can get activity report."""
        login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.get('/api/admin/reports/activity')
        
        assert response.status_code == 200
        assert 'period' in response.json
        assert 'activity' in response.json
        
        # Check activity structure
        activity = response.json['activity']
        assert 'new_users' in activity
        assert 'new_resources' in activity
        assert 'bookings_created' in activity
    
    def test_activity_report_custom_days(self, client, app, admin_user):
        """Test activity report with custom time period."""
        login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.get('/api/admin/reports/activity?days=7')
        
        assert response.status_code == 200
        assert 'Last 7 days' in response.json.get('period', '')


# ============================================================================
# Test: Rate Limiting
# ============================================================================

class TestAdminRateLimiting:
    """Test rate limiting on admin endpoints"""
    
    def test_admin_rate_limit_on_role_updates(self, client, app, admin_user, student_user, staff_user):
        """Test that admin role updates are rate limited (100 per hour)."""
        csrf_token = login_user(client, admin_user['email'], admin_user['password'])
        
        # Make multiple role update requests
        successful_updates = 0
        rate_limited = False
        
        # Try a reasonable number to trigger rate limit
        for i in range(102):
            response = client.put(
                f'/api/admin/users/{student_user["id"]}/role',
                json={'role': 'staff' if i % 2 == 0 else 'student'},
                headers={'X-CSRF-Token': csrf_token}
            )
            
            if response.status_code == 200:
                successful_updates += 1
            elif response.status_code == 429:
                assert 'rate limit' in response.json.get('error', '').lower()
                rate_limited = True
                break
        
        # Should hit rate limit before completing all requests
        assert successful_updates <= 100 or rate_limited
    
    def test_admin_rate_limit_on_status_updates(self, client, app, admin_user, student_user):
        """Test that admin status updates are rate limited."""
        csrf_token = login_user(client, admin_user['email'], admin_user['password'])
        
        successful_updates = 0
        for i in range(102):
            response = client.put(
                f'/api/admin/users/{student_user["id"]}/status',
                json={'status': 'active' if i % 2 == 0 else 'inactive'},
                headers={'X-CSRF-Token': csrf_token}
            )
            
            if response.status_code == 200:
                successful_updates += 1
            elif response.status_code == 429:
                break
        
        assert successful_updates <= 100


# ============================================================================
# Test: Edge Cases
# ============================================================================

class TestAdminEdgeCases:
    """Test edge cases and error handling"""
    
    def test_update_nonexistent_user_role(self, client, app, admin_user):
        """Test updating role of non-existent user."""
        csrf_token = login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.put(
            '/api/admin/users/99999/role',
            json={'role': 'staff'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 404
        assert 'not found' in response.json.get('message', '').lower()
    
    def test_hide_nonexistent_review(self, client, app, admin_user):
        """Test hiding non-existent review."""
        csrf_token = login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.post(
            '/api/admin/reviews/99999/hide',
            json={'moderation_notes': 'Test'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 404
        assert 'not found' in response.json.get('message', '').lower()
    
    def test_update_user_role_missing_role_field(self, client, app, admin_user, student_user):
        """Test that missing role field is rejected."""
        csrf_token = login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.put(
            f'/api/admin/users/{student_user["id"]}/role',
            json={},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'role is required' in response.json.get('message', '')
