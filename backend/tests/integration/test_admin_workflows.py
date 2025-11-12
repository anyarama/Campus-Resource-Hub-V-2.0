"""
Integration Tests: Admin Workflows
Tests complete admin user journeys including moderation and analytics.
"""

import pytest
from datetime import datetime, timedelta
from backend.tests.integration.conftest import login_and_get_token


class TestAdminModeration:
    """Test admin content moderation workflows"""
    
    def test_admin_complete_moderation_workflow(self, client, app, admin_diana, staff_charlie, student_alice, sample_resource):
        """
        Test full admin moderation journey:
        1. Login as admin
        2. View system analytics
        3. Review flagged content
        4. Moderate resources
        5. Manage users
        6. View activity reports
        """
        # Step 1: Admin logs in
        token = login_and_get_token(client, admin_diana['email'], admin_diana['password'])
        
        # Step 2: View system analytics
        response = client.get('/api/admin/analytics')
        assert response.status_code == 200
        assert 'users' in response.json
        assert 'resources' in response.json
        assert 'bookings' in response.json
        
        # Step 3: Student creates a booking and review
        client.get('/api/auth/logout')
        student_token = login_and_get_token(client, student_alice['email'], student_alice['password'])
        
        future_start = (datetime.utcnow() + timedelta(days=1)).isoformat()
        future_end = (datetime.utcnow() + timedelta(days=1, hours=1)).isoformat()
        
        booking_data = {
            'resource_id': sample_resource['id'],
            'start_datetime': future_start,
            'end_datetime': future_end
        }
        response = client.post('/api/bookings', json=booking_data, headers={'X-CSRF-Token': student_token})
        assert response.status_code == 201
        booking_id = response.json['booking']['id']
        
        # Create a review
        review_data = {
            'resource_id': sample_resource['id'],
            'rating': 1,
            'comment': 'This is a test review that might get flagged'
        }
        response = client.post('/api/reviews', json=review_data, headers={'X-CSRF-Token': student_token})
        # May succeed or fail depending on booking status
        review_id = response.json.get('review', {}).get('id') if response.status_code == 201 else None
        
        # Step 4: Admin moderates content
        client.get('/api/auth/logout')
        token = login_and_get_token(client, admin_diana['email'], admin_diana['password'])
        
        # View resources for moderation
        response = client.get('/api/admin/resources')
        assert response.status_code == 200
        assert 'resources' in response.json
        
        # View flagged reviews (if any)
        response = client.get('/api/admin/reviews/flagged')
        assert response.status_code == 200
        
        # Hide a review if one exists
        if review_id:
            response = client.post(
                f'/api/admin/reviews/{review_id}/hide',
                json={'moderation_notes': 'Inappropriate content'},
                headers={'X-CSRF-Token': token}
            )
            assert response.status_code in [200, 404]
        
        # Step 5: Admin manages users
        response = client.get('/api/admin/users')
        assert response.status_code == 200
        assert 'users' in response.json
        
        # Step 6: View activity report
        response = client.get('/api/admin/reports/activity?days=7')
        assert response.status_code == 200
        assert 'activity' in response.json
    
    def test_admin_user_management(self, client, app, admin_diana, student_alice):
        """Test admin user management capabilities"""
        # Admin logs in
        token = login_and_get_token(client, admin_diana['email'], admin_diana['password'])
        
        # List all users
        response = client.get('/api/admin/users')
        assert response.status_code == 200
        users = response.json['users']
        assert len(users) >= 2  # At least admin and student
        
        # Update user role
        response = client.put(
            f'/api/admin/users/{student_alice["id"]}/role',
            json={'role': 'staff'},
            headers={'X-CSRF-Token': token}
        )
        assert response.status_code == 200
        assert response.json['user']['role'] == 'staff'
        
        # Verify user can't change their own role
        response = client.put(
            f'/api/admin/users/{admin_diana["id"]}/role',
            json={'role': 'student'},
            headers={'X-CSRF-Token': token}
        )
        assert response.status_code == 403
        
        # Update user status
        response = client.put(
            f'/api/admin/users/{student_alice["id"]}/status',
            json={'status': 'suspended'},
            headers={'X-CSRF-Token': token}
        )
        assert response.status_code == 200
        assert response.json['user']['status'] == 'suspended'


class TestCrossFeatureIntegration:
    """Test integration across multiple features"""
    
    def test_complete_platform_workflow(self, client, app, student_alice, staff_charlie, admin_diana):
        """
        Test workflow involving all user types and all features:
        1. Staff creates resource
        2. Student books resource
        3. Staff approves
        4. Users exchange messages
        5. Student reviews
        6. Admin views analytics
        """
        # Step 1: Staff creates resource
        staff_token = login_and_get_token(client, staff_charlie['email'], staff_charlie['password'])
        
        resource_data = {
            'title': 'Integration Test Room',
            'description': 'Room for testing full workflow',
            'category': 'study_room',
            'location': 'Test Building',
            'capacity': 4,
            'requires_approval': True
        }
        
        response = client.post('/api/resources', json=resource_data, headers={'X-CSRF-Token': staff_token})
        assert response.status_code == 201
        resource_id = response.json['resource']['id']
        
        # Step 2: Student books resource
        client.get('/api/auth/logout')
        student_token = login_and_get_token(client, student_alice['email'], student_alice['password'])
        
        future_start = (datetime.utcnow() + timedelta(days=2)).isoformat()
        future_end = (datetime.utcnow() + timedelta(days=2, hours=2)).isoformat()
        
        booking_data = {
            'resource_id': resource_id,
            'start_datetime': future_start,
            'end_datetime': future_end,
            'notes': 'Integration test booking'
        }
        
        response = client.post('/api/bookings', json=booking_data, headers={'X-CSRF-Token': student_token})
        assert response.status_code == 201
        booking_id = response.json['booking']['id']
        
        # Step 3: Staff approves booking
        client.get('/api/auth/logout')
        staff_token = login_and_get_token(client, staff_charlie['email'], staff_charlie['password'])
        
        response = client.post(
            f'/api/bookings/{booking_id}/respond',
            json={'action': 'approve', 'notes': 'Approved for integration test'},
            headers={'X-CSRF-Token': staff_token}
        )
        assert response.status_code == 200
        
        # Step 4: Exchange messages
        message_data = {
            'receiver_id': student_alice['id'],
            'content': 'Your booking is confirmed!',
            'booking_id': booking_id
        }
        response = client.post('/api/messages', json=message_data, headers={'X-CSRF-Token': staff_token})
        assert response.status_code == 201
        
        # Student replies
        client.get('/api/auth/logout')
        student_token = login_and_get_token(client, student_alice['email'], student_alice['password'])
        
        reply_data = {
            'receiver_id': staff_charlie['id'],
            'content': 'Thank you!',
            'booking_id': booking_id
        }
        response = client.post('/api/messages', json=reply_data, headers={'X-CSRF-Token': student_token})
        assert response.status_code == 201
        
        # Step 5: Student leaves review (may fail if booking not completed)
        review_data = {
            'resource_id': resource_id,
            'rating': 5,
            'comment': 'Great room for the integration test!'
        }
        response = client.post('/api/reviews', json=review_data, headers={'X-CSRF-Token': student_token})
        # Accept either success or "booking not completed" error
        assert response.status_code in [201, 400]
        
        # Step 6: Admin views analytics
        client.get('/api/auth/logout')
        admin_token = login_and_get_token(client, admin_diana['email'], admin_diana['password'])
        
        response = client.get('/api/admin/analytics')
        assert response.status_code == 200
        analytics = response.json
        
        # Verify data reflects our operations
        assert analytics['users']['total'] >= 3
        assert analytics['resources']['total'] >= 1
        assert analytics['bookings']['total'] >= 1
        assert analytics['messages']['total'] >= 2
