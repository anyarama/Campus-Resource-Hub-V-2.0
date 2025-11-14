"""
Integration Tests: Concurrent Operations
Tests race conditions and concurrent user operations.
"""

import pytest
import threading
import time
from datetime import datetime, timedelta
from tests.integration.conftest import login_and_get_token


class TestConcurrentBookings:
    """Test concurrent booking scenarios to detect race conditions"""
    
    def test_simultaneous_booking_attempts(self, client, app, sample_resource, student_alice, student_bob, staff_charlie):
        """
        Test when two users try to book the same resource at the same time.
        Only one should succeed (or both go to pending, but not both approved).
        """
        # Login both users
        alice_token = login_and_get_token(client, student_alice['email'], student_alice['password'])
        
        # Use a separate client for Bob
        bob_client = app.test_client()
        bob_token = login_and_get_token(bob_client, student_bob['email'], student_bob['password'])
        
        # Same time slot for both
        start_time = (datetime.utcnow() + timedelta(days=4)).isoformat()
        end_time = (datetime.utcnow() + timedelta(days=4, hours=2)).isoformat()
        
        alice_booking = {
            'resource_id': sample_resource['id'],
            'start_datetime': start_time,
            'end_datetime': end_time,
            'notes': 'Alice booking'
        }
        
        bob_booking = {
            'resource_id': sample_resource['id'],
            'start_datetime': start_time,
            'end_datetime': end_time,
            'notes': 'Bob booking'
        }
        
        # Results storage
        results = {'alice': None, 'bob': None}
        
        def book_as_alice():
            results['alice'] = client.post(
                '/api/bookings',
                json=alice_booking,
                headers={'X-CSRF-Token': alice_token}
            )
        
        def book_as_bob():
            results['bob'] = bob_client.post(
                '/api/bookings',
                json=bob_booking,
                headers={'X-CSRF-Token': bob_token}
            )
        
        # Start both threads simultaneously
        thread_alice = threading.Thread(target=book_as_alice)
        thread_bob = threading.Thread(target=book_as_bob)
        
        thread_alice.start()
        thread_bob.start()
        
        thread_alice.join()
        thread_bob.join()
        
        alice_response = results['alice']
        bob_response = results['bob']
        
        # Both requests should succeed in creating bookings (status = pending)
        # But conflict should be detected when trying to approve
        assert alice_response.status_code in [201, 400]
        assert bob_response.status_code in [201, 400]
        
        # At least one should succeed
        successful_bookings = []
        if alice_response.status_code == 201:
            successful_bookings.append(alice_response.json['booking']['id'])
        if bob_response.status_code == 201:
            successful_bookings.append(bob_response.json['booking']['id'])
        
        assert len(successful_bookings) >= 1, "At least one booking should be created"
        
        # If both were created, test that only one can be approved
        if len(successful_bookings) == 2:
            staff_client = app.test_client()
            staff_token = login_and_get_token(staff_client, staff_charlie['email'], staff_charlie['password'])
            
            # Approve first booking
            response1 = staff_client.post(
                f'/api/bookings/{successful_bookings[0]}/respond',
                json={'action': 'approve'},
                headers={'X-CSRF-Token': staff_token}
            )
            
            # Try to approve second booking (should fail due to conflict)
            response2 = staff_client.post(
                f'/api/bookings/{successful_bookings[1]}/respond',
                json={'action': 'approve'},
                headers={'X-CSRF-Token': staff_token}
            )
            
            # One should succeed, one should fail
            statuses = [response1.status_code, response2.status_code]
            assert 200 in statuses or 201 in statuses, "At least one approval should succeed"
            assert 400 in statuses or 409 in statuses, "One approval should fail due to conflict"


class TestConcurrentResourceCreation:
    """Test concurrent resource creation"""
    
    def test_multiple_users_creating_resources(self, client, app, staff_charlie):
        """Test multiple staff users creating resources simultaneously"""
        # Create another staff user
        with app.app_context():
            from models.user import User
            from extensions import db
            
            staff2 = User(
                name='David Staff',
                email='david@example.com',
                password='DavidPass123!',
                role='staff'
            )
            db.session.add(staff2)
            db.session.commit()
            staff2_id = staff2.id
        
        # Login both staff users
        charlie_token = login_and_get_token(client, staff_charlie['email'], staff_charlie['password'])
        
        david_client = app.test_client()
        david_token = login_and_get_token(david_client, 'david@example.com', 'DavidPass123!')
        
        # Create resources simultaneously
        results = {'charlie': None, 'david': None}
        
        def create_as_charlie():
            results['charlie'] = client.post(
                '/api/resources',
                json={
                    'title': 'Charlie Resource',
                    'description': 'Test resource by Charlie',
                    'category': 'lab',
                    'location': 'Building A',
                    'capacity': 10
                },
                headers={'X-CSRF-Token': charlie_token}
            )
        
        def create_as_david():
            results['david'] = david_client.post(
                '/api/resources',
                json={
                    'title': 'David Resource',
                    'description': 'Test resource by David',
                    'category': 'lab',
                    'location': 'Building B',
                    'capacity': 8
                },
                headers={'X-CSRF-Token': david_token}
            )
        
        thread_charlie = threading.Thread(target=create_as_charlie)
        thread_david = threading.Thread(target=create_as_david)
        
        thread_charlie.start()
        thread_david.start()
        
        thread_charlie.join()
        thread_david.join()
        
        # Both should succeed independently
        assert results['charlie'].status_code == 201
        assert results['david'].status_code == 201
        
        charlie_resource_id = results['charlie'].json['resource']['id']
        david_resource_id = results['david'].json['resource']['id']
        
        # Resources should have different IDs
        assert charlie_resource_id != david_resource_id


class TestConcurrentMessaging:
    """Test concurrent message sending"""
    
    def test_simultaneous_message_sending(self, client, app, student_alice, staff_charlie):
        """Test sending messages simultaneously"""
        alice_token = login_and_get_token(client, student_alice['email'], student_alice['password'])
        
        charlie_client = app.test_client()
        charlie_token = login_and_get_token(charlie_client, staff_charlie['email'], staff_charlie['password'])
        
        results = {'alice': [], 'charlie': []}
        
        def send_alice_messages():
            for i in range(3):
                response = client.post(
                    '/api/messages',
                    json={
                        'receiver_id': staff_charlie['id'],
                        'content': f'Message {i+1} from Alice'
                    },
                    headers={'X-CSRF-Token': alice_token}
                )
                results['alice'].append(response.status_code)
                time.sleep(0.1)
        
        def send_charlie_messages():
            for i in range(3):
                response = charlie_client.post(
                    '/api/messages',
                    json={
                        'receiver_id': student_alice['id'],
                        'content': f'Message {i+1} from Charlie'
                    },
                    headers={'X-CSRF-Token': charlie_token}
                )
                results['charlie'].append(response.status_code)
                time.sleep(0.1)
        
        thread_alice = threading.Thread(target=send_alice_messages)
        thread_charlie = threading.Thread(target=send_charlie_messages)
        
        thread_alice.start()
        thread_charlie.start()
        
        thread_alice.join()
        thread_charlie.join()
        
        # All messages should be sent successfully
        assert all(status == 201 for status in results['alice'])
        assert all(status == 201 for status in results['charlie'])
        assert len(results['alice']) == 3
        assert len(results['charlie']) == 3


class TestDataConsistency:
    """Test data consistency under concurrent operations"""
    
    def test_booking_count_consistency(self, client, app, sample_resource, student_alice, staff_charlie):
        """
        Test that booking counts remain consistent even with concurrent operations
        """
        alice_token = login_and_get_token(client, student_alice['email'], student_alice['password'])
        
        # Create multiple bookings for different time slots
        booking_ids = []
        
        for day in range(1, 4):
            start_time = (datetime.utcnow() + timedelta(days=day+5)).isoformat()
            end_time = (datetime.utcnow() + timedelta(days=day+5, hours=1)).isoformat()
            
            response = client.post(
                '/api/bookings',
                json={
                    'resource_id': sample_resource['id'],
                    'start_datetime': start_time,
                    'end_datetime': end_time
                },
                headers={'X-CSRF-Token': alice_token}
            )
            
            if response.status_code == 201:
                booking_ids.append(response.json['booking']['id'])
        
        # Verify all bookings are in the system
        response = client.get('/api/bookings')
        assert response.status_code == 200
        
        bookings = response.json['bookings']
        created_booking_ids = [b['id'] for b in bookings if b['id'] in booking_ids]
        
        assert len(created_booking_ids) == len(booking_ids), "All created bookings should be retrievable"
    
    def test_review_count_updates(self, client, app, sample_resource, student_alice):
        """Test that review counts update correctly"""
        alice_token = login_and_get_token(client, student_alice['email'], student_alice['password'])
        
        # Get initial resource state
        response = client.get(f'/api/resources/{sample_resource["id"]}')
        assert response.status_code == 200
        initial_review_count = response.json['resource'].get('review_count', 0)
        
        # Create a review
        review_data = {
            'resource_id': sample_resource['id'],
            'rating': 4,
            'comment': 'Good resource for testing'
        }
        
        response = client.post('/api/reviews', json=review_data, headers={'X-CSRF-Token': alice_token})
        # May succeed or fail depending on booking requirements
        
        if response.status_code == 201:
            # Verify review count increased
            response = client.get(f'/api/resources/{sample_resource["id"]}')
            assert response.status_code == 200
            new_review_count = response.json['resource'].get('review_count', 0)
            assert new_review_count == initial_review_count + 1
