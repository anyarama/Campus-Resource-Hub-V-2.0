"""
Shared Fixtures for Integration Tests
Provides common test fixtures for end-to-end workflows.
"""

import pytest
from datetime import datetime, timedelta
from models.user import User
from models.resource import Resource
from models.booking import Booking
from models.message import Message
from models.review import Review
from extensions import db


@pytest.fixture
def app():
    """Create and configure a test Flask application for integration tests."""
    from app import create_app
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'integration-test-secret-key',
        'RATELIMIT_ENABLED': False,  # Disable rate limiting for integration tests
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


def login_and_get_token(client, email: str, password: str):
    """
    Helper function to log in a user and return CSRF token.
    
    Args:
        client: Flask test client
        email: User email
        password: User password
    
    Returns:
        str: CSRF token (empty if disabled)
    """
    response = client.post('/api/auth/login', json={
        'email': email,
        'password': password
    })
    assert response.status_code == 200, f"Login failed: {response.json}"
    return response.json.get('csrf_token', '')


@pytest.fixture(scope='function')
def student_alice(app):
    """Create a student user named Alice for testing."""
    user = User(
        name='Alice Student',
        email='alice@example.com',
        password='AlicePass123!',
        role='student'
    )
    db.session.add(user)
    db.session.commit()
    
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'password': 'AlicePass123!',
        'role': 'student'
    }


@pytest.fixture(scope='function')
def student_bob(app):
    """Create a student user named Bob for testing."""
    user = User(
        name='Bob Student',
        email='bob@example.com',
        password='BobPass123!',
        role='student'
    )
    db.session.add(user)
    db.session.commit()
    
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'password': 'BobPass123!',
        'role': 'student'
    }


@pytest.fixture(scope='function')
def staff_charlie(app):
    """Create a staff user named Charlie for testing."""
    user = User(
        name='Charlie Staff',
        email='charlie@example.com',
        password='CharliePass123!',
        role='staff'
    )
    db.session.add(user)
    db.session.commit()
    
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'password': 'CharliePass123!',
        'role': 'staff'
    }


@pytest.fixture(scope='function')
def admin_diana(app):
    """Create an admin user named Diana for testing."""
    user = User(
        name='Diana Admin',
        email='diana@example.com',
        password='DianaPass123!',
        role='admin'
    )
    db.session.add(user)
    db.session.commit()
    
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'password': 'DianaPass123!',
        'role': 'admin'
    }


@pytest.fixture(scope='function')
def sample_resource(app, staff_charlie):
    """Create a sample resource owned by Charlie."""
    resource = Resource(
        owner_id=staff_charlie['id'],
        title='Study Room A',
        description='Quiet study room with whiteboard',
        location='Library 2nd Floor',
        category='study_room',
        capacity=6
    )
    resource.status = 'published'
    resource.requires_approval = True
    db.session.add(resource)
    db.session.commit()
    
    return {
        'id': resource.id,
        'title': resource.title,
        'owner_id': resource.owner_id
    }


@pytest.fixture
def future_datetime():
    """Return a datetime 2 days in the future."""
    return datetime.utcnow() + timedelta(days=2)


@pytest.fixture
def past_datetime():
    """Return a datetime 2 days in the past."""
    return datetime.utcnow() - timedelta(days=2)
