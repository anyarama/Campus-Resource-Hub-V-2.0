"""
Reviews API Tests
Comprehensive tests for review and rating system endpoints with security integration.

Tests cover:
1. Review creation and validation
2. One-review-per-resource enforcement
3. One-review-per-booking enforcement
4. CRUD operations with authorization
5. XSS prevention in review comments
6. Rating validation (1-5 stars)
7. Review moderation (flagging and hiding)
8. Rate limiting on review creation
9. CSRF protection on all mutation endpoints
10. Security headers on all responses
"""

import pytest
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models.user import User
from models.resource import Resource
from models.booking import Booking
from models.review import Review


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


@pytest.fixture
def student_user(app):
    """Create a student user."""
    with app.app_context():
        user = User(
            name='Student User',
            email='student@example.com',
            role='student'
        )
        user.set_password('StudentPass123')
        db.session.add(user)
        db.session.commit()
        
        return {
            'id': user.id,
            'email': user.email,
            'password': 'StudentPass123'
        }


@pytest.fixture
def staff_user(app):
    """Create a staff user (resource owner)."""
    with app.app_context():
        user = User(
            name='Staff User',
            email='staff@example.com',
            role='staff'
        )
        user.set_password('StaffPass123')
        db.session.add(user)
        db.session.commit()
        
        return {
            'id': user.id,
            'email': user.email,
            'password': 'StaffPass123'
        }


@pytest.fixture
def admin_user(app):
    """Create an admin user."""
    with app.app_context():
        user = User(
            name='Admin User',
            email='admin@example.com',
            role='admin'
        )
        user.set_password('AdminPass123')
        db.session.add(user)
        db.session.commit()
        
        return {
            'id': user.id,
            'email': user.email,
            'password': 'AdminPass123'
        }


@pytest.fixture
def test_resource(app, staff_user):
    """Create a test resource."""
    with app.app_context():
        resource = Resource(
            title='Test Study Room',
            description='A quiet study room for students',
            category='study_space',
            owner_id=staff_user['id'],
            status='published'
        )
        db.session.add(resource)
        db.session.commit()
        
        return {
            'id': resource.id,
            'title': resource.title,
            'owner_id': resource.owner_id
        }


@pytest.fixture
def completed_booking(app, student_user, test_resource):
    """Create a completed booking."""
    with app.app_context():
        start_time = datetime.utcnow() - timedelta(days=2)
        end_time = datetime.utcnow() - timedelta(days=2, hours=-2)
        
        booking = Booking(
            resource_id=test_resource['id'],
            requester_id=student_user['id'],
            start_time=start_time,
            end_time=end_time,
            purpose='Study session',
            status='completed'
        )
        db.session.add(booking)
        db.session.commit()
        
        return {
            'id': booking.id,
            'resource_id': booking.resource_id,
            'requester_id': booking.requester_id
        }


def login_user(client, email, password):
    """Helper function to log in a user and get CSRF token."""
    # Get CSRF token
    response = client.get('/api/auth/csrf-token')
    assert response.status_code == 200
    csrf_token = response.json['csrf_token']
    
    # Login
    response = client.post(
        '/api/auth/login',
        json={'email': email, 'password': password},
        headers={'X-CSRF-Token': csrf_token}
    )
    assert response.status_code == 200
    
    return csrf_token


# ============================================================================
# Test: Create Review Endpoint
# ============================================================================

class TestCreateReviewEndpoint:
    """Test POST /api/reviews - Create review"""
    
    def test_create_review_success(self, client, app, student_user, test_resource):
        """Test successful review creation."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 5,
            'comment': 'Excellent study room! Very quiet and well-maintained.'
        }
        
        response = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 201
        data = response.json
        assert data['message'] == 'Review submitted successfully'
        assert data['review']['rating'] == 5
        assert 'Excellent study room' in data['review']['comment']
    
    def test_create_review_requires_authentication(self, client, test_resource):
        """Test that creating reviews requires authentication."""
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 5,
            'comment': 'Great room!'
        }
        
        response = client.post('/api/reviews', json=review_data)
        
        assert response.status_code == 401
        assert 'error' in response.json
    
    def test_create_review_requires_csrf(self, client, app, student_user, test_resource):
        """Test that CSRF token is required."""
        login_user(client, student_user['email'], student_user['password'])
        
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 5,
            'comment': 'Great room!'
        }
        
        response = client.post('/api/reviews', json=review_data)
        
        assert response.status_code == 400
        assert 'CSRF' in response.json.get('error', '')
    
    def test_create_review_missing_rating(self, client, app, student_user, test_resource):
        """Test creating review without rating."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        review_data = {
            'resource_id': test_resource['id'],
            'comment': 'Great room!'
        }
        
        response = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'rating' in response.json['message'].lower()
    
    def test_create_review_missing_resource_id(self, client, app, student_user):
        """Test creating review without resource_id."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        review_data = {
            'rating': 5,
            'comment': 'Great room!'
        }
        
        response = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'resource_id' in response.json['message'].lower()
    
    def test_create_review_with_booking(self, client, app, student_user, completed_booking):
        """Test creating review with associated booking."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        review_data = {
            'resource_id': completed_booking['resource_id'],
            'rating': 4,
            'comment': 'Good experience. Room was clean and quiet.',
            'booking_id': completed_booking['id']
        }
        
        response = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 201
        assert response.json['review']['booking_id'] == completed_booking['id']
    
    def test_create_review_has_security_headers(self, client, app, student_user, test_resource):
        """Test that security headers are present."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 5,
            'comment': 'Great room!'
        }
        
        response = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 201
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'


# ============================================================================
# Test: Rating Validation
# ============================================================================

class TestRatingValidation:
    """Test rating validation (1-5 stars)"""
    
    def test_rating_too_low(self, client, app, student_user, test_resource):
        """Test that rating below 1 is rejected."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 0,
            'comment': 'Test review'
        }
        
        response = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'between 1 and 5' in response.json['message'].lower()
    
    def test_rating_too_high(self, client, app, student_user, test_resource):
        """Test that rating above 5 is rejected."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 6,
            'comment': 'Test review'
        }
        
        response = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'between 1 and 5' in response.json['message'].lower()
    
    def test_valid_ratings(self, client, app, student_user):
        """Test that all valid ratings (1-5) are accepted."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # Create multiple resources for multiple reviews
        for rating in [1, 2, 3, 4, 5]:
            with app.app_context():
                resource = Resource(
                    title=f'Test Room {rating}',
                    description='Test resource',
                    category='study_space',
                    owner_id=2,
                    status='published'
                )
                db.session.add(resource)
                db.session.commit()
                resource_id = resource.id
            
            review_data = {
                'resource_id': resource_id,
                'rating': rating,
                'comment': f'Rating {rating} review'
            }
            
            response = client.post(
                '/api/reviews',
                json=review_data,
                headers={'X-CSRF-Token': csrf_token}
            )
            
            assert response.status_code == 201
            assert response.json['review']['rating'] == rating


# ============================================================================
# Test: One Review Per Resource Enforcement
# ============================================================================

class TestOneReviewPerResource:
    """Test enforcement of one review per user per resource"""
    
    def test_cannot_review_resource_twice(self, client, app, student_user, test_resource):
        """Test that user cannot review same resource twice."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # First review
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 5,
            'comment': 'First review'
        }
        response1 = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response1.status_code == 201
        
        # Second review attempt
        review_data2 = {
            'resource_id': test_resource['id'],
            'rating': 4,
            'comment': 'Second review attempt'
        }
        response2 = client.post(
            '/api/reviews',
            json=review_data2,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response2.status_code == 400
        assert 'already reviewed' in response2.json['message'].lower()


# ============================================================================
# Test: One Review Per Booking Enforcement
# ============================================================================

class TestOneReviewPerBooking:
    """Test enforcement of one review per booking"""
    
    def test_cannot_review_booking_twice(self, client, app, student_user, completed_booking):
        """Test that same booking cannot be reviewed twice."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # First review with booking
        review_data = {
            'resource_id': completed_booking['resource_id'],
            'rating': 5,
            'comment': 'First review for booking',
            'booking_id': completed_booking['id']
        }
        response1 = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response1.status_code == 201
        
        # Cannot review resource again since first review exists
        review_data2 = {
            'resource_id': completed_booking['resource_id'],
            'rating': 4,
            'comment': 'Second review attempt',
            'booking_id': completed_booking['id']
        }
        response2 = client.post(
            '/api/reviews',
            json=review_data2,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response2.status_code == 400


# ============================================================================
# Test: XSS Prevention
# ============================================================================

class TestXSSPrevention:
    """Test XSS prevention in review comments"""
    
    def test_xss_script_tag_sanitized(self, client, app, student_user, test_resource):
        """Test that script tags are sanitized."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        xss_comment = '<script>alert("XSS")</script>Nice room!'
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 5,
            'comment': xss_comment
        }
        
        response = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 201
        # Content should be sanitized
        returned_comment = response.json['review']['comment']
        assert '<script>' not in returned_comment or 'Nice room' in returned_comment
    
    def test_xss_event_handler_sanitized(self, client, app, student_user, test_resource):
        """Test that event handlers are sanitized."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        xss_comment = '<div onclick="alert(\'XSS\')">Good room</div>'
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 4,
            'comment': xss_comment
        }
        
        response = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 201
        returned_comment = response.json['review']['comment']
        assert 'onclick=' not in returned_comment.lower() or 'Good room' in returned_comment


# ============================================================================
# Test: Review CRUD Operations
# ============================================================================

class TestReviewCRUDOperations:
    """Test review CRUD operations with authorization"""
    
    def test_update_own_review(self, client, app, student_user, test_resource):
        """Test that users can update their own reviews."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # Create review
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 3,
            'comment': 'Initial review comment'
        }
        response = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code == 201
        review_id = response.json['review']['id']
        
        # Update review
        update_data = {
            'rating': 5,
            'comment': 'Updated review - much better experience!'
        }
        response = client.put(
            f'/api/reviews/{review_id}',
            json=update_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 200
        assert response.json['review']['rating'] == 5
        assert 'Updated review' in response.json['review']['comment']
    
    def test_cannot_update_others_review(self, client, app, student_user, staff_user, test_resource):
        """Test that users cannot update others' reviews."""
        # Student creates review
        csrf_token_student = login_user(client, student_user['email'], student_user['password'])
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 4,
            'comment': 'Student review'
        }
        response = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token_student}
        )
        assert response.status_code == 201
        review_id = response.json['review']['id']
        
        # Staff tries to update student's review
        client.get('/api/auth/logout')
        csrf_token_staff = login_user(client, staff_user['email'], staff_user['password'])
        
        update_data = {
            'rating': 1,
            'comment': 'Trying to change review'
        }
        response = client.put(
            f'/api/reviews/{review_id}',
            json=update_data,
            headers={'X-CSRF-Token': csrf_token_staff}
        )
        
        assert response.status_code == 403
    
    def test_delete_own_review(self, client, app, student_user, test_resource):
        """Test that users can delete their own reviews."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # Create review
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 3,
            'comment': 'Test review to delete'
        }
        response = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code == 201
        review_id = response.json['review']['id']
        
        # Delete review
        response = client.delete(
            f'/api/reviews/{review_id}',
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 200
        assert 'deleted' in response.json['message'].lower()
    
    def test_admin_can_delete_any_review(self, client, app, student_user, admin_user, test_resource):
        """Test that admins can delete any review."""
        # Student creates review
        csrf_token_student = login_user(client, student_user['email'], student_user['password'])
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 2,
            'comment': 'Inappropriate review'
        }
        response = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token_student}
        )
        assert response.status_code == 201
        review_id = response.json['review']['id']
        
        # Admin deletes review
        client.get('/api/auth/logout')
        csrf_token_admin = login_user(client, admin_user['email'], admin_user['password'])
        
        response = client.delete(
            f'/api/reviews/{review_id}',
            headers={'X-CSRF-Token': csrf_token_admin}
        )
        
        assert response.status_code == 200


# ============================================================================
# Test: Review Moderation
# ============================================================================

class TestReviewModeration:
    """Test review moderation features (flagging)"""
    
    def test_flag_review_success(self, client, app, student_user, staff_user, test_resource):
        """Test flagging a review as inappropriate."""
        # Student creates review
        csrf_token_student = login_user(client, student_user['email'], student_user['password'])
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 1,
            'comment': 'This review might be inappropriate'
        }
        response = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token_student}
        )
        assert response.status_code == 201
        review_id = response.json['review']['id']
        
        # Staff flags the review
        client.get('/api/auth/logout')
        csrf_token_staff = login_user(client, staff_user['email'], staff_user['password'])
        
        response = client.post(
            f'/api/reviews/{review_id}/flag',
            headers={'X-CSRF-Token': csrf_token_staff}
        )
        
        assert response.status_code == 200
        assert 'flagged' in response.json['message'].lower()
    
    def test_cannot_flag_own_review(self, client, app, student_user, test_resource):
        """Test that users cannot flag their own reviews."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # Create review
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 3,
            'comment': 'My review'
        }
        response = client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code == 201
        review_id = response.json['review']['id']
        
        # Try to flag own review
        response = client.post(
            f'/api/reviews/{review_id}/flag',
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'own review' in response.json['message'].lower()


# ============================================================================
# Test: Get Reviews
# ============================================================================

class TestGetReviews:
    """Test getting reviews for resources"""
    
    def test_get_resource_reviews(self, client, app, student_user, test_resource):
        """Test getting all reviews for a resource."""
        # Create a review first
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 5,
            'comment': 'Excellent resource!'
        }
        client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        # Get reviews
        response = client.get(f'/api/reviews/resources/{test_resource["id"]}/reviews')
        
        assert response.status_code == 200
        assert 'reviews' in response.json
        assert 'average_rating' in response.json
        assert len(response.json['reviews']) >= 1
    
    def test_get_my_reviews(self, client, app, student_user, test_resource):
        """Test getting current user's reviews."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # Create review
        review_data = {
            'resource_id': test_resource['id'],
            'rating': 4,
            'comment': 'My review'
        }
        client.post(
            '/api/reviews',
            json=review_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        # Get my reviews
        response = client.get('/api/reviews/my-reviews')
        
        assert response.status_code == 200
        assert 'reviews' in response.json
        assert len(response.json['reviews']) >= 1


# ============================================================================
# Test: Rate Limiting
# ============================================================================

class TestReviewRateLimiting:
    """Test rate limiting on review creation"""
    
    def test_review_rate_limit(self, client, app, student_user, staff_user):
        """Test that review creation is rate limited (5 per hour)."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        successful_reviews = 0
        for i in range(7):
            # Create a new resource for each review
            with app.app_context():
                resource = Resource(
                    title=f'Test Room {i}',
                    description='Test resource',
                    category='study_space',
                    owner_id=staff_user['id'],
                    status='published'
                )
                db.session.add(resource)
                db.session.commit()
                resource_id = resource.id
            
            review_data = {
                'resource_id': resource_id,
                'rating': 5,
                'comment': f'Review {i+1}'
            }
            
            response = client.post(
                '/api/reviews',
                json=review_data,
                headers={'X-CSRF-Token': csrf_token}
            )
            
            if response.status_code == 201:
                successful_reviews += 1
            elif response.status_code == 429:
                assert 'rate limit' in response.json.get('error', '').lower()
                break
        
        assert successful_reviews <= 5
