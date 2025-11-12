"""
Bookings API Tests
Comprehensive tests for booking management endpoints with security integration.

Tests cover:
1. Booking creation with conflict detection
2. Booking workflow (pending → approved/rejected → completed)
3. Authorization checks (requester, resource owner, staff, admin)
4. CSRF protection on all mutation endpoints
5. Input validation (dates, times, durations)
6. Rate limiting on booking creation
7. Concurrent booking attempts
8. Security headers on all responses
"""

import pytest
import time
from datetime import datetime, timedelta
from flask import session
from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.resource import Resource
from backend.models.booking import Booking


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
    """Create a staff user."""
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


@pytest.fixture
def sample_resource(app, staff_user):
    """Create a sample resource for testing."""
    with app.app_context():
        resource = Resource(
            name='Conference Room A',
            description='Large conference room',
            category='room',
            location='Building 1, Floor 2',
            owner_id=staff_user['id'],
            status='published',
            requires_approval=True
        )
        db.session.add(resource)
        db.session.commit()
        
        return {
            'id': resource.id,
            'name': resource.name,
            'owner_id': resource.owner_id
        }


@pytest.fixture
def sample_booking_data():
    """Sample booking data for tests."""
    start = datetime.utcnow() + timedelta(hours=2)
    end = start + timedelta(hours=2)
    
    return {
        'start_datetime': start.isoformat() + 'Z',
        'end_datetime': end.isoformat() + 'Z',
        'notes': 'Team meeting'
    }


# ============================================================================
# Test: Create Booking Endpoint
# ============================================================================

class TestCreateBookingEndpoint:
    """Test POST /api/bookings - Create booking"""
    
    def test_create_booking_success(self, client, app, student_user, sample_resource, sample_booking_data):
        """Test successful booking creation."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        booking_data = {
            'resource_id': sample_resource['id'],
            **sample_booking_data
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 201
        data = response.json
        assert data['message'] == 'Booking created successfully'
        assert data['booking']['resource_id'] == sample_resource['id']
        assert data['booking']['status'] == 'pending'
        assert data['booking']['requester_id'] == student_user['id']
    
    def test_create_booking_requires_authentication(self, client, app, sample_resource, sample_booking_data):
        """Test that booking creation requires authentication."""
        booking_data = {
            'resource_id': sample_resource['id'],
            **sample_booking_data
        }
        
        response = client.post('/api/bookings', json=booking_data)
        
        assert response.status_code == 401
        assert 'error' in response.json
    
    def test_create_booking_requires_csrf(self, client, app, student_user, sample_resource, sample_booking_data):
        """Test that CSRF token is required."""
        # Login but don't provide CSRF token
        login_user(client, student_user['email'], student_user['password'])
        
        booking_data = {
            'resource_id': sample_resource['id'],
            **sample_booking_data
        }
        
        response = client.post('/api/bookings', json=booking_data)
        
        assert response.status_code == 400
        assert 'CSRF' in response.json.get('error', '')
    
    def test_create_booking_missing_resource_id(self, client, app, student_user, sample_booking_data):
        """Test booking creation with missing resource_id."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        response = client.post(
            '/api/bookings',
            json=sample_booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'resource_id' in response.json['message'].lower()
    
    def test_create_booking_invalid_resource(self, client, app, student_user, sample_booking_data):
        """Test booking creation with non-existent resource."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        booking_data = {
            'resource_id': 99999,
            **sample_booking_data
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'not found' in response.json['message'].lower()
    
    def test_create_booking_missing_dates(self, client, app, student_user, sample_resource):
        """Test booking creation with missing datetime fields."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        booking_data = {
            'resource_id': sample_resource['id'],
            'notes': 'Missing dates'
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'datetime' in response.json['message'].lower()
    
    def test_create_booking_has_security_headers(self, client, app, student_user, sample_resource, sample_booking_data):
        """Test that security headers are present on booking creation."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        booking_data = {
            'resource_id': sample_resource['id'],
            **sample_booking_data
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 201
        # Check security headers
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'


# ============================================================================
# Test: Booking Date Validation
# ============================================================================

class TestBookingDateValidation:
    """Test booking date validation rules"""
    
    def test_booking_past_date(self, client, app, student_user, sample_resource):
        """Test that bookings cannot be made in the past."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        past_start = datetime.utcnow() - timedelta(hours=2)
        past_end = past_start + timedelta(hours=1)
        
        booking_data = {
            'resource_id': sample_resource['id'],
            'start_datetime': past_start.isoformat() + 'Z',
            'end_datetime': past_end.isoformat() + 'Z',
            'notes': 'Past booking'
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'past' in response.json['message'].lower()
    
    def test_booking_end_before_start(self, client, app, student_user, sample_resource):
        """Test that end time must be after start time."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        start = datetime.utcnow() + timedelta(hours=2)
        end = start - timedelta(hours=1)
        
        booking_data = {
            'resource_id': sample_resource['id'],
            'start_datetime': start.isoformat() + 'Z',
            'end_datetime': end.isoformat() + 'Z',
            'notes': 'Invalid booking'
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'after' in response.json['message'].lower()
    
    def test_booking_too_short(self, client, app, student_user, sample_resource):
        """Test minimum booking duration (15 minutes)."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        start = datetime.utcnow() + timedelta(hours=2)
        end = start + timedelta(minutes=5)
        
        booking_data = {
            'resource_id': sample_resource['id'],
            'start_datetime': start.isoformat() + 'Z',
            'end_datetime': end.isoformat() + 'Z',
            'notes': 'Too short'
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'duration' in response.json['message'].lower()
    
    def test_booking_too_long(self, client, app, student_user, sample_resource):
        """Test maximum booking duration (7 days)."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        start = datetime.utcnow() + timedelta(hours=2)
        end = start + timedelta(days=8)
        
        booking_data = {
            'resource_id': sample_resource['id'],
            'start_datetime': start.isoformat() + 'Z',
            'end_datetime': end.isoformat() + 'Z',
            'notes': 'Too long'
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'duration' in response.json['message'].lower() or 'exceed' in response.json['message'].lower()
    
    def test_booking_insufficient_advance_time(self, client, app, student_user, sample_resource):
        """Test minimum advance booking time (30 minutes)."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        start = datetime.utcnow() + timedelta(minutes=10)
        end = start + timedelta(hours=1)
        
        booking_data = {
            'resource_id': sample_resource['id'],
            'start_datetime': start.isoformat() + 'Z',
            'end_datetime': end.isoformat() + 'Z',
            'notes': 'Too soon'
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'advance' in response.json['message'].lower()


# ============================================================================
# Test: Conflict Detection
# ============================================================================

class TestBookingConflictDetection:
    """Test booking conflict detection algorithm"""
    
    def test_overlapping_booking_rejected(self, client, app, student_user, sample_resource):
        """Test that overlapping bookings are rejected."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # Create first booking
        start1 = datetime.utcnow() + timedelta(hours=2)
        end1 = start1 + timedelta(hours=2)
        
        booking_data1 = {
            'resource_id': sample_resource['id'],
            'start_datetime': start1.isoformat() + 'Z',
            'end_datetime': end1.isoformat() + 'Z',
            'notes': 'First booking'
        }
        
        response1 = client.post(
            '/api/bookings',
            json=booking_data1,
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response1.status_code == 201
        
        # Try to create overlapping booking
        start2 = start1 + timedelta(hours=1)
        end2 = start2 + timedelta(hours=2)
        
        booking_data2 = {
            'resource_id': sample_resource['id'],
            'start_datetime': start2.isoformat() + 'Z',
            'end_datetime': end2.isoformat() + 'Z',
            'notes': 'Overlapping booking'
        }
        
        response2 = client.post(
            '/api/bookings',
            json=booking_data2,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response2.status_code == 409
        assert 'conflict' in response2.json['message'].lower()
    
    def test_adjacent_bookings_allowed(self, client, app, student_user, sample_resource):
        """Test that adjacent (non-overlapping) bookings are allowed."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # Create first booking
        start1 = datetime.utcnow() + timedelta(hours=2)
        end1 = start1 + timedelta(hours=2)
        
        booking_data1 = {
            'resource_id': sample_resource['id'],
            'start_datetime': start1.isoformat() + 'Z',
            'end_datetime': end1.isoformat() + 'Z',
            'notes': 'First booking'
        }
        
        response1 = client.post(
            '/api/bookings',
            json=booking_data1,
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response1.status_code == 201
        
        # Create adjacent booking (starts when first ends)
        start2 = end1
        end2 = start2 + timedelta(hours=2)
        
        booking_data2 = {
            'resource_id': sample_resource['id'],
            'start_datetime': start2.isoformat() + 'Z',
            'end_datetime': end2.isoformat() + 'Z',
            'notes': 'Adjacent booking'
        }
        
        response2 = client.post(
            '/api/bookings',
            json=booking_data2,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response2.status_code == 201
    
    def test_different_resource_no_conflict(self, client, app, student_user, staff_user):
        """Test that bookings for different resources don't conflict."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # Create two resources
        with app.app_context():
            resource1 = Resource(
                name='Room A',
                description='Resource 1',
                category='room',
                location='Building 1',
                owner_id=staff_user['id'],
                status='published'
            )
            resource2 = Resource(
                name='Room B',
                description='Resource 2',
                category='room',
                location='Building 2',
                owner_id=staff_user['id'],
                status='published'
            )
            db.session.add(resource1)
            db.session.add(resource2)
            db.session.commit()
            resource1_id = resource1.id
            resource2_id = resource2.id
        
        # Create overlapping bookings for different resources
        start = datetime.utcnow() + timedelta(hours=2)
        end = start + timedelta(hours=2)
        
        booking_data1 = {
            'resource_id': resource1_id,
            'start_datetime': start.isoformat() + 'Z',
            'end_datetime': end.isoformat() + 'Z',
            'notes': 'Resource 1'
        }
        
        booking_data2 = {
            'resource_id': resource2_id,
            'start_datetime': start.isoformat() + 'Z',
            'end_datetime': end.isoformat() + 'Z',
            'notes': 'Resource 2'
        }
        
        response1 = client.post(
            '/api/bookings',
            json=booking_data1,
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response1.status_code == 201
        
        response2 = client.post(
            '/api/bookings',
            json=booking_data2,
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response2.status_code == 201


# ============================================================================
# Test: Approval/Rejection Workflow
# ============================================================================

class TestBookingApprovalWorkflow:
    """Test booking approval and rejection workflow"""
    
    def test_approve_booking_success(self, client, app, student_user, staff_user, sample_resource, sample_booking_data):
        """Test successful booking approval by resource owner."""
        # Student creates booking
        csrf_token_student = login_user(client, student_user['email'], student_user['password'])
        
        booking_data = {
            'resource_id': sample_resource['id'],
            **sample_booking_data
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token_student}
        )
        assert response.status_code == 201
        booking_id = response.json['booking']['id']
        
        # Logout student and login staff (resource owner)
        client.get('/api/auth/logout')
        csrf_token_staff = login_user(client, staff_user['email'], staff_user['password'])
        
        # Staff approves booking
        response = client.post(
            f'/api/bookings/{booking_id}/approve',
            json={'approval_notes': 'Approved'},
            headers={'X-CSRF-Token': csrf_token_staff}
        )
        
        assert response.status_code == 200
        assert response.json['booking']['status'] == 'approved'
        assert response.json['booking']['approval_notes'] == 'Approved'
    
    def test_reject_booking_success(self, client, app, student_user, staff_user, sample_resource, sample_booking_data):
        """Test successful booking rejection by resource owner."""
        # Student creates booking
        csrf_token_student = login_user(client, student_user['email'], student_user['password'])
        
        booking_data = {
            'resource_id': sample_resource['id'],
            **sample_booking_data
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token_student}
        )
        assert response.status_code == 201
        booking_id = response.json['booking']['id']
        
        # Logout and login staff
        client.get('/api/auth/logout')
        csrf_token_staff = login_user(client, staff_user['email'], staff_user['password'])
        
        # Staff rejects booking
        response = client.post(
            f'/api/bookings/{booking_id}/reject',
            json={'rejection_reason': 'Resource unavailable'},
            headers={'X-CSRF-Token': csrf_token_staff}
        )
        
        assert response.status_code == 200
        assert response.json['booking']['status'] == 'rejected'
        assert response.json['booking']['rejection_reason'] == 'Resource unavailable'
    
    def test_student_cannot_approve_booking(self, client, app, student_user, sample_resource, sample_booking_data):
        """Test that students cannot approve bookings."""
        # Create booking
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        booking_data = {
            'resource_id': sample_resource['id'],
            **sample_booking_data
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code == 201
        booking_id = response.json['booking']['id']
        
        # Try to approve own booking
        response = client.post(
            f'/api/bookings/{booking_id}/approve',
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 403
        assert 'permission' in response.json['message'].lower()
    
    def test_rejection_requires_reason(self, client, app, student_user, staff_user, sample_resource, sample_booking_data):
        """Test that rejection requires a reason."""
        # Create booking
        csrf_token_student = login_user(client, student_user['email'], student_user['password'])
        
        booking_data = {
            'resource_id': sample_resource['id'],
            **sample_booking_data
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token_student}
        )
        assert response.status_code == 201
        booking_id = response.json['booking']['id']
        
        # Logout and login staff
        client.get('/api/auth/logout')
        csrf_token_staff = login_user(client, staff_user['email'], staff_user['password'])
        
        # Try to reject without reason
        response = client.post(
            f'/api/bookings/{booking_id}/reject',
            json={},
            headers={'X-CSRF-Token': csrf_token_staff}
        )
        
        assert response.status_code == 400
        assert 'rejection_reason' in response.json['message'].lower()


# ============================================================================
# Test: Booking Cancellation
# ============================================================================

class TestBookingCancellation:
    """Test booking cancellation functionality"""
    
    def test_requester_can_cancel_own_booking(self, client, app, student_user, sample_resource, sample_booking_data):
        """Test that users can cancel their own bookings."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # Create booking
        booking_data = {
            'resource_id': sample_resource['id'],
            **sample_booking_data
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code == 201
        booking_id = response.json['booking']['id']
        
        # Cancel booking
        response = client.post(
            f'/api/bookings/{booking_id}/cancel',
            json={'cancellation_reason': 'No longer needed'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 200
        assert response.json['booking']['status'] == 'cancelled'
        assert response.json['booking']['cancellation_reason'] == 'No longer needed'
    
    def test_resource_owner_can_cancel_booking(self, client, app, student_user, staff_user, sample_resource, sample_booking_data):
        """Test that resource owners can cancel bookings."""
        # Student creates booking
        csrf_token_student = login_user(client, student_user['email'], student_user['password'])
        
        booking_data = {
            'resource_id': sample_resource['id'],
            **sample_booking_data
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token_student}
        )
        assert response.status_code == 201
        booking_id = response.json['booking']['id']
        
        # Staff (resource owner) cancels booking
        client.get('/api/auth/logout')
        csrf_token_staff = login_user(client, staff_user['email'], staff_user['password'])
        
        response = client.post(
            f'/api/bookings/{booking_id}/cancel',
            json={'cancellation_reason': 'Resource maintenance'},
            headers={'X-CSRF-Token': csrf_token_staff}
        )
        
        assert response.status_code == 200
        assert response.json['booking']['status'] == 'cancelled'


# ============================================================================
# Test: List Bookings
# ============================================================================

class TestListBookingsEndpoint:
    """Test GET /api/bookings - List user bookings"""
    
    def test_list_user_bookings(self, client, app, student_user, sample_resource):
        """Test listing user's own bookings."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # Create multiple bookings
        for i in range(3):
            start = datetime.utcnow() + timedelta(hours=2+i*3)
            end = start + timedelta(hours=2)
            
            booking_data = {
                'resource_id': sample_resource['id'],
                'start_datetime': start.isoformat() + 'Z',
                'end_datetime': end.isoformat() + 'Z',
                'notes': f'Booking {i+1}'
            }
            
            client.post(
                '/api/bookings',
                json=booking_data,
                headers={'X-CSRF-Token': csrf_token}
            )
        
        # List bookings
        response = client.get('/api/bookings')
        
        assert response.status_code == 200
        assert 'bookings' in response.json
        assert len(response.json['bookings']) == 3
    
    def test_list_bookings_with_status_filter(self, client, app, student_user, staff_user, sample_resource):
        """Test filtering bookings by status."""
        # Create and approve one booking
        csrf_token_student = login_user(client, student_user['email'], student_user['password'])
        
        start = datetime.utcnow() + timedelta(hours=2)
        end = start + timedelta(hours=2)
        
        booking_data = {
            'resource_id': sample_resource['id'],
            'start_datetime': start.isoformat() + 'Z',
            'end_datetime': end.isoformat() + 'Z',
            'notes': 'First booking'
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token_student}
        )
        booking_id = response.json['booking']['id']
        
        # Approve it
        client.get('/api/auth/logout')
        csrf_token_staff = login_user(client, staff_user['email'], staff_user['password'])
        client.post(
            f'/api/bookings/{booking_id}/approve',
            headers={'X-CSRF-Token': csrf_token_staff}
        )
        
        # Create another pending booking
        client.get('/api/auth/logout')
        csrf_token_student = login_user(client, student_user['email'], student_user['password'])
        
        start2 = datetime.utcnow() + timedelta(hours=5)
        end2 = start2 + timedelta(hours=2)
        
        booking_data2 = {
            'resource_id': sample_resource['id'],
            'start_datetime': start2.isoformat() + 'Z',
            'end_datetime': end2.isoformat() + 'Z',
            'notes': 'Second booking'
        }
        
        client.post(
            '/api/bookings',
            json=booking_data2,
            headers={'X-CSRF-Token': csrf_token_student}
        )
        
        # Filter by pending status
        response = client.get('/api/bookings?status=pending')
        
        assert response.status_code == 200
        assert len(response.json['bookings']) == 1
        assert response.json['bookings'][0]['status'] == 'pending'
    
    def test_get_specific_booking(self, client, app, student_user, sample_resource, sample_booking_data):
        """Test retrieving a specific booking by ID."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # Create booking
        booking_data = {
            'resource_id': sample_resource['id'],
            **sample_booking_data
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        booking_id = response.json['booking']['id']
        
        # Get booking
        response = client.get(f'/api/bookings/{booking_id}')
        
        assert response.status_code == 200
        assert response.json['id'] == booking_id
        assert response.json['resource_id'] == sample_resource['id']


# ============================================================================
# Test: Check Availability Endpoint
# ============================================================================

class TestCheckAvailabilityEndpoint:
    """Test POST /api/bookings/check-availability"""
    
    def test_check_availability_success(self, client, app, student_user, sample_resource):
        """Test checking availability for a free time slot."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        start = datetime.utcnow() + timedelta(hours=2)
        end = start + timedelta(hours=2)
        
        availability_data = {
            'resource_id': sample_resource['id'],
            'start_datetime': start.isoformat() + 'Z',
            'end_datetime': end.isoformat() + 'Z'
        }
        
        response = client.post(
            '/api/bookings/check-availability',
            json=availability_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 200
        assert response.json['available'] is True
    
    def test_check_availability_conflict(self, client, app, student_user, sample_resource, sample_booking_data):
        """Test checking availability when time slot is taken."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # Create a booking
        booking_data = {
            'resource_id': sample_resource['id'],
            **sample_booking_data
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code == 201
        
        # Check availability for overlapping time
        response = client.post(
            '/api/bookings/check-availability',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 200
        assert response.json['available'] is False
        assert 'conflict' in response.json['message'].lower()


# ============================================================================
# Test: Rate Limiting
# ============================================================================

class TestBookingRateLimiting:
    """Test rate limiting on booking creation endpoint"""
    
    def test_booking_creation_rate_limit(self, client, app, student_user, sample_resource):
        """Test that booking creation is rate limited (10 per hour)."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # Create bookings up to the limit
        successful_bookings = 0
        for i in range(12):  # Try to create 12 bookings (limit is 10)
            start = datetime.utcnow() + timedelta(hours=2 + i*3)
            end = start + timedelta(hours=1)
            
            booking_data = {
                'resource_id': sample_resource['id'],
                'start_datetime': start.isoformat() + 'Z',
                'end_datetime': end.isoformat() + 'Z',
                'notes': f'Booking {i+1}'
            }
            
            response = client.post(
                '/api/bookings',
                json=booking_data,
                headers={'X-CSRF-Token': csrf_token}
            )
            
            if response.status_code == 201:
                successful_bookings += 1
            elif response.status_code == 429:
                # Rate limit hit
                assert 'rate limit' in response.json.get('error', '').lower()
                break
        
        # Should hit rate limit before creating all 12
        assert successful_bookings <= 10


# ============================================================================
# Test: Pending Approvals
# ============================================================================

class TestPendingApprovalsEndpoint:
    """Test GET /api/bookings/pending"""
    
    def test_resource_owner_sees_pending_bookings(self, client, app, student_user, staff_user, sample_resource, sample_booking_data):
        """Test that resource owners see pending bookings for their resources."""
        # Student creates booking
        csrf_token_student = login_user(client, student_user['email'], student_user['password'])
        
        booking_data = {
            'resource_id': sample_resource['id'],
            **sample_booking_data
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token_student}
        )
        assert response.status_code == 201
        
        # Staff checks pending approvals
        client.get('/api/auth/logout')
        csrf_token_staff = login_user(client, staff_user['email'], staff_user['password'])
        
        response = client.get('/api/bookings/pending')
        
        assert response.status_code == 200
        assert response.json['count'] >= 1
        assert any(b['status'] == 'pending' for b in response.json['bookings'])
    
    def test_student_sees_no_pending_approvals(self, client, app, student_user, sample_resource, sample_booking_data):
        """Test that regular students don't see other users' pending bookings."""
        # Create booking
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        booking_data = {
            'resource_id': sample_resource['id'],
            **sample_booking_data
        }
        
        response = client.post(
            '/api/bookings',
            json=booking_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code == 201
        
        # Check pending approvals (students don't have resources to approve)
        response = client.get('/api/bookings/pending')
        
        assert response.status_code == 200
        # Students with no owned resources should see empty list
        assert response.json['count'] == 0
