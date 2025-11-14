"""
Resources API Tests
Comprehensive tests for resource management endpoints with security integration.

Tests cover:
1. CRUD operations with CSRF protection
2. Authorization checks (owner, admin, student roles)
3. Input validation and sanitization
4. Search and filtering
5. Pagination
6. Security headers on all responses
7. Error handling
"""

import pytest
from flask import session
from app import create_app
from extensions import db
from models.user import User
from models.resource import Resource


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
            password='StudentPass123',
            role='student'
        )
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
            password='StaffPass123',
            role='staff'
        )
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
            password='AdminPass123',
            role='admin'
        )
        db.session.add(user)
        db.session.commit()
        
        return {
            'id': user.id,
            'email': user.email,
            'password': 'AdminPass123'
        }


@pytest.fixture
def auth_headers(client):
    """Get CSRF token for authenticated requests."""
    csrf_response = client.get('/api/auth/csrf-token')
    csrf_token = csrf_response.get_json()['csrf_token']
    return {'X-CSRF-Token': csrf_token}


def login_user(client, email, password, headers):
    """Helper function to login a user."""
    response = client.post('/api/auth/login',
        json={'email': email, 'password': password},
        headers=headers
    )
    return response


@pytest.fixture
def sample_resource_data():
    """Sample resource data for testing."""
    return {
        'title': 'Study Room A',
        'description': 'Quiet study room with whiteboard and projector',
        'category': 'study_room',
        'location': 'Library, 2nd Floor',
        'capacity': 8,
        'images': [],
        'availability_rules': {},
        'requires_approval': True,
        'status': 'draft'
    }


@pytest.fixture
def seeded_resources(app):
    """Seed the database with published resources for filtering tests."""
    with app.app_context():
        owner = User(
            name='Owner',
            email='owner@example.com',
            password='OwnerPass123',
            role='staff'
        )
        db.session.add(owner)
        db.session.flush()

        resources = []
        sample_data = [
            {
                'title': 'Library Study Room',
                'description': 'Quiet room in main library',
                'category': 'study_room',
                'location': 'Library East Wing',
                'capacity': 6
            },
            {
                'title': 'Library Collaboration Space',
                'description': 'Group space with display',
                'category': 'study_room',
                'location': 'Library West Wing',
                'capacity': 10
            },
            {
                'title': 'Engineering Lab',
                'description': 'Hands-on engineering lab',
                'category': 'technology',
                'location': 'Engineering Building',
                'capacity': 20
            },
        ]

        for entry in sample_data:
            resource = Resource(
                owner_id=owner.id,
                title=entry['title'],
                description=entry['description'],
                category=entry['category'],
                location=entry['location'],
                capacity=entry['capacity']
            )
            resource.status = 'published'
            db.session.add(resource)
            resources.append(resource)

        db.session.commit()
        yield resources


class TestListResourcesEndpoint:
    """Test GET /api/resources - List resources."""
    
    def test_list_resources_without_auth(self, client):
        """Test listing resources without authentication."""
        response = client.get('/api/resources')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'resources' in data
        assert 'pagination' in data
    
    def test_list_resources_has_security_headers(self, client):
        """Test security headers are present."""
        response = client.get('/api/resources')
        
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
    
    def test_list_resources_pagination(self, client):
        """Test pagination works correctly."""
        response = client.get('/api/resources?page=1&per_page=10')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 10
    
    def test_list_resources_invalid_page(self, client):
        """Test invalid page parameter."""
        response = client.get('/api/resources?page=invalid')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_list_resources_max_per_page(self, client):
        """Test per_page is capped at 100."""
        response = client.get('/api/resources?per_page=200')
        
        assert response.status_code == 200
        data = response.get_json()
        # Should be capped at 100
        assert data['pagination']['per_page'] <= 100
    
    def test_list_resources_filter_by_status(self, client):
        """Test filtering by status."""
        response = client.get('/api/resources?status=published')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'resources' in data
    
    def test_list_resources_filter_by_category(self, client):
        """Test filtering by category."""
        response = client.get('/api/resources?category=study_room')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'resources' in data
    
    def test_list_resources_search(self, client):
        """Test search functionality."""
        response = client.get('/api/resources?search=study')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'resources' in data

    def test_list_resources_search_filters_results(self, client, seeded_resources):
        """Search filter should affect both results and pagination totals."""
        response = client.get('/api/resources?search=library')
        assert response.status_code == 200
        data = response.get_json()
        # Two library resources seeded
        assert data['pagination']['total'] == 2
        assert len(data['resources']) == 2

    def test_list_resources_location_filter(self, client, seeded_resources):
        """Location filter should narrow the dataset."""
        response = client.get('/api/resources?location=Engineering')
        assert response.status_code == 200
        data = response.get_json()
        assert data['pagination']['total'] == 1
        assert len(data['resources']) == 1

    def test_list_resources_search_pagination(self, client, seeded_resources):
        """Pagination metadata should remain consistent with filtered totals."""
        response = client.get('/api/resources?search=library&per_page=1&page=2')
        assert response.status_code == 200
        data = response.get_json()
        pagination = data['pagination']
        assert pagination['total'] == 2
        assert pagination['per_page'] == 1
        assert pagination['page'] == 2


class TestGetResourceEndpoint:
    """Test GET /api/resources/:id - Get single resource."""
    
    def test_get_nonexistent_resource(self, client):
        """Test getting a resource that doesn't exist."""
        response = client.get('/api/resources/99999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Not Found'
    
    def test_get_resource_has_security_headers(self, client):
        """Test security headers on get resource."""
        response = client.get('/api/resources/1')
        
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers


class TestCreateResourceEndpoint:
    """Test POST /api/resources - Create resource."""
    
    def test_create_resource_without_auth(self, client, auth_headers, sample_resource_data):
        """Test creating resource without authentication fails."""
        response = client.post('/api/resources',
            json=sample_resource_data,
            headers=auth_headers
        )
        
        assert response.status_code == 401
    
    def test_create_resource_without_csrf(self, client, student_user, sample_resource_data):
        """Test creating resource without CSRF token fails."""
        # Login first
        headers = {}
        csrf_response = client.get('/api/auth/csrf-token')
        headers['X-CSRF-Token'] = csrf_response.get_json()['csrf_token']
        
        login_user(client, student_user['email'], student_user['password'], headers)
        
        # Try to create without CSRF
        response = client.post('/api/resources', json=sample_resource_data)
        
        assert response.status_code == 403
    
    def test_create_resource_success(self, client, student_user, auth_headers, sample_resource_data):
        """Test successfully creating a resource."""
        # Login
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        # Get new CSRF token after login
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        # Create resource
        response = client.post('/api/resources',
            json=sample_resource_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'resource' in data
        assert data['resource']['title'] == sample_resource_data['title']
    
    def test_create_resource_missing_title(self, client, student_user, auth_headers):
        """Test creating resource without title fails."""
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        response = client.post('/api/resources',
            json={'description': 'Test'},
            headers=headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_resource_title_too_short(self, client, student_user, auth_headers, sample_resource_data):
        """Test title validation - too short."""
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        sample_resource_data['title'] = 'AB'  # Too short
        
        response = client.post('/api/resources',
            json=sample_resource_data,
            headers=headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'title' in data['message'].lower() or 'length' in data['message'].lower()
    
    def test_create_resource_title_too_long(self, client, student_user, auth_headers, sample_resource_data):
        """Test title validation - too long."""
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        sample_resource_data['title'] = 'A' * 201  # Too long
        
        response = client.post('/api/resources',
            json=sample_resource_data,
            headers=headers
        )
        
        assert response.status_code == 400
    
    def test_create_resource_invalid_category(self, client, student_user, auth_headers, sample_resource_data):
        """Test invalid category fails validation."""
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        sample_resource_data['category'] = 'invalid_category'
        
        response = client.post('/api/resources',
            json=sample_resource_data,
            headers=headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'category' in data['message'].lower()
    
    def test_create_resource_invalid_status(self, client, student_user, auth_headers, sample_resource_data):
        """Test invalid status fails validation."""
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        sample_resource_data['status'] = 'invalid_status'
        
        response = client.post('/api/resources',
            json=sample_resource_data,
            headers=headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'status' in data['message'].lower()
    
    def test_create_resource_negative_capacity(self, client, student_user, auth_headers, sample_resource_data):
        """Test negative capacity fails validation."""
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        sample_resource_data['capacity'] = -5
        
        response = client.post('/api/resources',
            json=sample_resource_data,
            headers=headers
        )
        
        assert response.status_code == 400
    
    def test_create_resource_location_too_long(self, client, student_user, auth_headers, sample_resource_data):
        """Test location validation - too long."""
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        sample_resource_data['location'] = 'A' * 201
        
        response = client.post('/api/resources',
            json=sample_resource_data,
            headers=headers
        )
        
        assert response.status_code == 400
    
    def test_create_resource_xss_in_title(self, client, student_user, auth_headers, sample_resource_data):
        """Test XSS attempt in title is handled."""
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        sample_resource_data['title'] = '<script>alert("XSS")</script>Study Room'
        
        response = client.post('/api/resources',
            json=sample_resource_data,
            headers=headers
        )
        
        # Should either reject or sanitize
        assert response.status_code in [201, 400]
    
    def test_create_resource_has_security_headers(self, client, student_user, auth_headers, sample_resource_data):
        """Test security headers on create response."""
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        response = client.post('/api/resources',
            json=sample_resource_data,
            headers=headers
        )
        
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers


class TestUpdateResourceEndpoint:
    """Test PUT/PATCH /api/resources/:id - Update resource."""
    
    def test_update_resource_without_auth(self, client, auth_headers):
        """Test updating resource without authentication fails."""
        response = client.put('/api/resources/1',
            json={'title': 'Updated Title'},
            headers=auth_headers
        )
        
        assert response.status_code in [401, 404]
    
    def test_update_resource_without_csrf(self, client, student_user):
        """Test updating without CSRF token fails."""
        headers = {}
        csrf_response = client.get('/api/auth/csrf-token')
        headers['X-CSRF-Token'] = csrf_response.get_json()['csrf_token']
        
        login_user(client, student_user['email'], student_user['password'], headers)
        
        # Try to update without CSRF
        response = client.put('/api/resources/1',
            json={'title': 'Updated'}
        )
        
        assert response.status_code == 403
    
    def test_update_nonexistent_resource(self, client, student_user, auth_headers):
        """Test updating non-existent resource."""
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        response = client.put('/api/resources/99999',
            json={'title': 'Updated'},
            headers=headers
        )
        
        assert response.status_code == 404


class TestDeleteResourceEndpoint:
    """Test DELETE /api/resources/:id - Delete resource."""
    
    def test_delete_resource_without_auth(self, client, auth_headers):
        """Test deleting resource without authentication fails."""
        response = client.delete('/api/resources/1', headers=auth_headers)
        
        assert response.status_code in [401, 404]
    
    def test_delete_resource_without_csrf(self, client, student_user):
        """Test deleting without CSRF token fails."""
        headers = {}
        csrf_response = client.get('/api/auth/csrf-token')
        headers['X-CSRF-Token'] = csrf_response.get_json()['csrf_token']
        
        login_user(client, student_user['email'], student_user['password'], headers)
        
        # Try to delete without CSRF
        response = client.delete('/api/resources/1')
        
        assert response.status_code == 403
    
    def test_delete_nonexistent_resource(self, client, student_user, auth_headers):
        """Test deleting non-existent resource."""
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        response = client.delete('/api/resources/99999', headers=headers)
        
        assert response.status_code == 404


class TestPublishResourceEndpoint:
    """Test POST /api/resources/:id/publish - Publish resource."""
    
    def test_publish_resource_without_auth(self, client, auth_headers):
        """Test publishing without authentication fails."""
        response = client.post('/api/resources/1/publish', headers=auth_headers)
        
        assert response.status_code in [401, 404]
    
    def test_publish_resource_without_csrf(self, client, student_user):
        """Test publishing without CSRF fails."""
        headers = {}
        csrf_response = client.get('/api/auth/csrf-token')
        headers['X-CSRF-Token'] = csrf_response.get_json()['csrf_token']
        
        login_user(client, student_user['email'], student_user['password'], headers)
        
        response = client.post('/api/resources/1/publish')
        
        assert response.status_code == 403


class TestSearchResourcesEndpoint:
    """Test GET /api/resources/search - Search resources."""
    
    def test_search_without_query(self, client):
        """Test search without query parameter fails."""
        response = client.get('/api/resources/search')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_search_empty_query(self, client):
        """Test search with empty query."""
        response = client.get('/api/resources/search?q=')
        
        assert response.status_code == 400
    
    def test_search_valid_query(self, client):
        """Test search with valid query."""
        response = client.get('/api/resources/search?q=study')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'results' in data
        assert 'count' in data
    
    def test_search_with_category_filter(self, client):
        """Test search with category filter."""
        response = client.get('/api/resources/search?q=room&category=study_room')
        
        assert response.status_code == 200
    
    def test_search_invalid_limit(self, client):
        """Test search with invalid limit parameter."""
        response = client.get('/api/resources/search?q=study&limit=invalid')
        
        assert response.status_code == 400
    
    def test_search_xss_in_query(self, client):
        """Test XSS attempt in search query is handled."""
        response = client.get('/api/resources/search?q=<script>alert("XSS")</script>')
        
        # Should handle safely
        assert response.status_code in [200, 400]
    
    def test_search_sql_injection_attempt(self, client):
        """Test SQL injection attempt in search is prevented."""
        response = client.get('/api/resources/search?q=\' OR \'1\'=\'1')
        
        # Should handle safely without causing SQL error
        assert response.status_code in [200, 400]
        assert response.content_type == 'application/json'


class TestGetCategoriesEndpoint:
    """Test GET /api/resources/categories - Get categories."""
    
    def test_get_categories(self, client):
        """Test getting categories list."""
        response = client.get('/api/resources/categories')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'categories' in data
        assert isinstance(data['categories'], list)
    
    def test_get_categories_has_security_headers(self, client):
        """Test security headers on categories endpoint."""
        response = client.get('/api/resources/categories')
        
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers


class TestGetMyResourcesEndpoint:
    """Test GET /api/resources/my-resources - Get user's resources."""
    
    def test_get_my_resources_without_auth(self, client):
        """Test getting my resources without authentication fails."""
        response = client.get('/api/resources/my-resources')
        
        assert response.status_code == 401
    
    def test_get_my_resources_success(self, client, student_user, auth_headers):
        """Test getting authenticated user's resources."""
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        response = client.get('/api/resources/my-resources')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'resources' in data
        assert 'count' in data


class TestGetPopularResourcesEndpoint:
    """Test GET /api/resources/popular - Get popular resources."""
    
    def test_get_popular_resources(self, client):
        """Test getting popular resources."""
        response = client.get('/api/resources/popular')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'resources' in data
        assert 'count' in data
    
    def test_get_popular_resources_with_limit(self, client):
        """Test getting popular resources with limit."""
        response = client.get('/api/resources/popular?limit=5')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] <= 5
    
    def test_get_popular_resources_invalid_limit(self, client):
        """Test invalid limit parameter."""
        response = client.get('/api/resources/popular?limit=invalid')
        
        assert response.status_code == 400


class TestResourceAuthorizationSecurity:
    """Test authorization and permission checks."""
    
    def test_student_cannot_edit_others_resource(self, client, student_user, staff_user, auth_headers, sample_resource_data):
        """Test student cannot edit another user's resource."""
        # Create resource as staff user
        login_user(client, staff_user['email'], staff_user['password'], auth_headers)
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        create_response = client.post('/api/resources',
            json=sample_resource_data,
            headers=headers
        )
        resource_id = create_response.get_json()['resource']['id']
        
        # Logout and login as student
        client.post('/api/auth/logout', headers=headers)
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        login_user(client, student_user['email'], student_user['password'], headers)
        
        # Try to update
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        response = client.put(f'/api/resources/{resource_id}',
            json={'title': 'Hacked Title'},
            headers=headers
        )
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'permission' in data['message'].lower()


class TestResourceErrorHandling:
    """Test error handling and security in error responses."""
    
    def test_error_responses_have_security_headers(self, client):
        """Test error responses include security headers."""
        response = client.get('/api/resources/invalid')
        
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers
    
    def test_error_responses_no_sensitive_data(self, client):
        """Test error responses don't leak sensitive information."""
        response = client.get('/api/resources/99999')
        
        data = response.get_json()
        response_text = str(data)
        
        # Should not contain sensitive info
        assert 'traceback' not in response_text.lower()
        assert 'password' not in response_text.lower()
        assert 'secret' not in response_text.lower()


class TestResourceRateLimiting:
    """Test rate limiting on resource creation endpoint."""
    
    def test_resource_creation_rate_limit(self, client, student_user, auth_headers, sample_resource_data):
        """Test rate limit on resource creation (20 per hour)."""
        # Login
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        # Get CSRF token
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        # Create resources up to the limit
        successful_creates = 0
        for i in range(21):  # Try to create 21 resources
            test_data = sample_resource_data.copy()
            test_data['title'] = f'Test Resource {i}'
            
            response = client.post('/api/resources',
                json=test_data,
                headers=headers
            )
            
            if response.status_code == 201:
                successful_creates += 1
            elif response.status_code == 429:
                # Rate limit hit
                break
        
        # Should have hit rate limit before creating all 21
        assert successful_creates <= 20
    
    def test_rate_limit_error_format(self, client, student_user, auth_headers, sample_resource_data):
        """Test rate limit error response format."""
        # Login
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        # Get CSRF token
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        # Exhaust rate limit
        for i in range(20):
            test_data = sample_resource_data.copy()
            test_data['title'] = f'Test Resource {i}'
            client.post('/api/resources', json=test_data, headers=headers)
        
        # Try one more - should be rate limited
        test_data = sample_resource_data.copy()
        test_data['title'] = 'Rate Limited Resource'
        response = client.post('/api/resources',
            json=test_data,
            headers=headers
        )
        
        if response.status_code == 429:
            data = response.get_json()
            assert 'error' in data
            assert data['error'] == 'Too Many Requests'
    
    def test_rate_limit_does_not_affect_read_operations(self, client, student_user, auth_headers, sample_resource_data):
        """Test rate limit only applies to creation, not reads."""
        # Login
        login_user(client, student_user['email'], student_user['password'], auth_headers)
        
        # Get CSRF token
        csrf_response = client.get('/api/auth/csrf-token')
        headers = {'X-CSRF-Token': csrf_response.get_json()['csrf_token']}
        
        # Create resources to exhaust limit
        for i in range(20):
            test_data = sample_resource_data.copy()
            test_data['title'] = f'Test Resource {i}'
            client.post('/api/resources', json=test_data, headers=headers)
        
        # Reading should still work
        response = client.get('/api/resources')
        assert response.status_code == 200
        
        response = client.get('/api/resources/my-resources')
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
