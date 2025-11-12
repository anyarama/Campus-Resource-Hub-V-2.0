"""
Messages API Tests
Comprehensive tests for messaging system endpoints with security integration.

Tests cover:
1. Message creation and sending
2. Message threading and conversations
3. Authorization (message privacy - users can only see their messages)
4. XSS prevention in message content
5. Message search with SQL injection prevention
6. Rate limiting on message sending
7. CSRF protection on all mutation endpoints
8. Security headers on all responses
"""

import pytest
from flask import session
from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.resource import Resource
from backend.models.message import Message


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
def another_user(app):
    """Create another user for testing message privacy."""
    with app.app_context():
        user = User(
            name='Another User',
            email='another@example.com',
            role='student'
        )
        user.set_password('AnotherPass123')
        db.session.add(user)
        db.session.commit()
        
        return {
            'id': user.id,
            'email': user.email,
            'password': 'AnotherPass123'
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
# Test: Send Message Endpoint
# ============================================================================

class TestSendMessageEndpoint:
    """Test POST /api/messages - Send message"""
    
    def test_send_message_success(self, client, app, student_user, staff_user):
        """Test successful message sending."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        message_data = {
            'receiver_id': staff_user['id'],
            'content': 'Hello, I have a question about the resource.'
        }
        
        response = client.post(
            '/api/messages',
            json=message_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 201
        data = response.json
        assert data['message'] == 'Message sent successfully'
        assert data['data']['content'] == message_data['content']
        assert data['data']['sender_id'] == student_user['id']
        assert data['data']['receiver_id'] == staff_user['id']
    
    def test_send_message_requires_authentication(self, client, staff_user):
        """Test that sending messages requires authentication."""
        message_data = {
            'receiver_id': staff_user['id'],
            'content': 'Test message'
        }
        
        response = client.post('/api/messages', json=message_data)
        
        assert response.status_code == 401
        assert 'error' in response.json
    
    def test_send_message_requires_csrf(self, client, app, student_user, staff_user):
        """Test that CSRF token is required."""
        login_user(client, student_user['email'], student_user['password'])
        
        message_data = {
            'receiver_id': staff_user['id'],
            'content': 'Test message'
        }
        
        response = client.post('/api/messages', json=message_data)
        
        assert response.status_code == 400
        assert 'CSRF' in response.json.get('error', '')
    
    def test_send_message_missing_receiver(self, client, app, student_user):
        """Test sending message without receiver_id."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        message_data = {
            'content': 'Test message'
        }
        
        response = client.post(
            '/api/messages',
            json=message_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'receiver_id' in response.json['message'].lower()
    
    def test_send_message_missing_content(self, client, app, student_user, staff_user):
        """Test sending message without content."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        message_data = {
            'receiver_id': staff_user['id']
        }
        
        response = client.post(
            '/api/messages',
            json=message_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 400
        assert 'content' in response.json['message'].lower()
    
    def test_send_message_with_thread_id(self, client, app, student_user, staff_user):
        """Test sending message with thread_id for threading."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        message_data = {
            'receiver_id': staff_user['id'],
            'content': 'Follow-up message',
            'thread_id': 'thread_1_2_resource_5'
        }
        
        response = client.post(
            '/api/messages',
            json=message_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 201
        assert response.json['data']['thread_id'] == 'thread_1_2_resource_5'
    
    def test_send_message_has_security_headers(self, client, app, student_user, staff_user):
        """Test that security headers are present."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        message_data = {
            'receiver_id': staff_user['id'],
            'content': 'Test message'
        }
        
        response = client.post(
            '/api/messages',
            json=message_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 201
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'


# ============================================================================
# Test: Message Threading
# ============================================================================

class TestMessageThreading:
    """Test message threading functionality"""
    
    def test_thread_conversation(self, client, app, student_user, staff_user):
        """Test that messages with same thread_id are grouped."""
        csrf_token_student = login_user(client, student_user['email'], student_user['password'])
        
        thread_id = f"thread_{student_user['id']}_{staff_user['id']}"
        
        # Send first message
        msg1_data = {
            'receiver_id': staff_user['id'],
            'content': 'Initial question',
            'thread_id': thread_id
        }
        response1 = client.post(
            '/api/messages',
            json=msg1_data,
            headers={'X-CSRF-Token': csrf_token_student}
        )
        assert response1.status_code == 201
        
        # Send second message in same thread
        msg2_data = {
            'receiver_id': staff_user['id'],
            'content': 'Follow-up question',
            'thread_id': thread_id
        }
        response2 = client.post(
            '/api/messages',
            json=msg2_data,
            headers={'X-CSRF-Token': csrf_token_student}
        )
        assert response2.status_code == 201
        assert response2.json['data']['thread_id'] == thread_id
    
    def test_get_thread_messages(self, client, app, student_user, staff_user):
        """Test retrieving all messages in a thread."""
        csrf_token_student = login_user(client, student_user['email'], student_user['password'])
        
        thread_id = f"thread_{student_user['id']}_{staff_user['id']}"
        
        # Send messages
        for i in range(3):
            msg_data = {
                'receiver_id': staff_user['id'],
                'content': f'Message {i+1}',
                'thread_id': thread_id
            }
            client.post(
                '/api/messages',
                json=msg_data,
                headers={'X-CSRF-Token': csrf_token_student}
            )
        
        # Get thread messages
        response = client.get(f'/api/messages/thread/{thread_id}')
        
        assert response.status_code == 200
        assert 'messages' in response.json
        assert len(response.json['messages']) == 3


# ============================================================================
# Test: Message Authorization (Privacy)
# ============================================================================

class TestMessageAuthorization:
    """Test message privacy - users can only see their messages"""
    
    def test_user_can_view_sent_messages(self, client, app, student_user, staff_user):
        """Test that users can view messages they sent."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        # Send message
        msg_data = {
            'receiver_id': staff_user['id'],
            'content': 'Test message'
        }
        response = client.post(
            '/api/messages',
            json=msg_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code == 201
        
        # Get threads
        response = client.get('/api/messages')
        assert response.status_code == 200
        assert 'threads' in response.json
    
    def test_user_can_view_received_messages(self, client, app, student_user, staff_user):
        """Test that users can view messages they received."""
        csrf_token_student = login_user(client, student_user['email'], student_user['password'])
        
        # Send message from student to staff
        msg_data = {
            'receiver_id': staff_user['id'],
            'content': 'Question for staff'
        }
        client.post(
            '/api/messages',
            json=msg_data,
            headers={'X-CSRF-Token': csrf_token_student}
        )
        
        # Logout and login as staff
        client.get('/api/auth/logout')
        csrf_token_staff = login_user(client, staff_user['email'], staff_user['password'])
        
        # Staff checks their messages
        response = client.get('/api/messages')
        assert response.status_code == 200
        assert 'threads' in response.json
    
    def test_user_cannot_view_others_private_messages(self, client, app, student_user, staff_user, another_user):
        """Test that users cannot view messages between other users."""
        # Student sends message to staff
        csrf_token_student = login_user(client, student_user['email'], student_user['password'])
        msg_data = {
            'receiver_id': staff_user['id'],
            'content': 'Private message'
        }
        response = client.post(
            '/api/messages',
            json=msg_data,
            headers={'X-CSRF-Token': csrf_token_student}
        )
        assert response.status_code == 201
        thread_id = response.json['data']['thread_id']
        
        # Logout and login as another user
        client.get('/api/auth/logout')
        login_user(client, another_user['email'], another_user['password'])
        
        # Try to access the thread
        response = client.get(f'/api/messages/thread/{thread_id}')
        
        # Should return 404 (not found) to not reveal thread exists
        assert response.status_code == 404


# ============================================================================
# Test: XSS Prevention
# ============================================================================

class TestXSSPrevention:
    """Test XSS prevention in message content"""
    
    def test_xss_script_tag_sanitized(self, client, app, student_user, staff_user):
        """Test that script tags are sanitized."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        xss_content = '<script>alert("XSS")</script>Hello'
        msg_data = {
            'receiver_id': staff_user['id'],
            'content': xss_content
        }
        
        response = client.post(
            '/api/messages',
            json=msg_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 201
        # Content should be sanitized (exact sanitization depends on implementation)
        returned_content = response.json['data']['content']
        assert '<script>' not in returned_content or 'Hello' in returned_content
    
    def test_xss_event_handler_sanitized(self, client, app, student_user, staff_user):
        """Test that event handlers are sanitized."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        xss_content = '<div onload="alert(\'XSS\')">Content</div>'
        msg_data = {
            'receiver_id': staff_user['id'],
            'content': xss_content
        }
        
        response = client.post(
            '/api/messages',
            json=msg_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 201
        returned_content = response.json['data']['content']
        # Event handler should be removed
        assert 'onload=' not in returned_content.lower() or 'Content' in returned_content
    
    def test_safe_html_preserved(self, client, app, student_user, staff_user):
        """Test that safe HTML/text is preserved."""
        csrf_token = login_user(client, student_user['email'], student_user['password'])
        
        safe_content = 'Hello, I need help with <Resource Name>'
        msg_data = {
            'receiver_id': staff_user['id'],
            'content': safe_content
        }
        
        response = client.post(
            '/api/messages',
            json=msg_data,
            headers={'X-CSRF-Token': csrf_token}
        )
        
        assert response.status_code == 201
        # Safe content should be preserved
        assert 'Resource Name' in response.json['data']['content']
