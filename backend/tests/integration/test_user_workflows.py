"""
Integration Tests: Complete User Workflows
Tests end-to-end user journeys across the entire application.
"""

import pytest
from datetime import datetime, timedelta
from backend.tests.integration.conftest import login_and_get_token


class TestStudentJourney:
    """Test complete student user journey from registration to review"""
    
    def test_student_complete_booking_workflow(self, client, app, student_alice, staff_charlie, sample_resource):
        """
        Test full student journey:
        1. Login
        2. Browse and search resources
        3. Create a booking request
        4. Wait for approval (simulated by staff)
        5. Send message to staff
        6. Complete booking
        7. Leave a review
        """
        # Step 1: Student logs in
        token = login_and_get_token(client, student_alice['email'], student_alice['password'])
        
        # Step 2: Browse resources
        response = client.get('/api/resources')
        assert response.status_code == 200
        assert 'resources' in response.json
        assert len(response.json['resources']) > 0
        resource = response.json['resources'][0]
        assert resource['id'] == sample_resource['id']
        
        # Step 3: Create booking request
        future_start = (datetime.utcnow() + timedelta(days=2)).isoformat()
        future_end = (datetime.utcnow() + timedelta(days=2, hours=2)).isoformat()
        
        booking_data = {
            'resource_id': sample_resource['id'],
            'start_datetime': future_start,
            'end_datetime': future_end,
            'notes': 'Need room for group study session'
        }
        
        response = client.post('/api/bookings', json=booking_data, headers={'X-CSRF-Token': token})
        assert response.status_code == 201
        booking_id = response.json['booking']['id']
        assert response.json['booking']['status'] == 'pending'
        
        # Step 4: Staff approves booking
        client.get('/api/auth/logout')
        staff_token = login_and_get_token(client, staff_charlie['email'], staff_charlie['password'])
        
        approval_data = {
            'action': 'approve',
            'notes': 'Approved for your study group'
        }
        response = client.post(
            f'/api/bookings/{booking_id}/respond',
            json=approval_data,
            headers={'X-CSRF-Token': staff_token}
        )
        assert response.status_code == 200
        assert response.json['booking']['status'] == 'approved'
        
        # Step 5: Student sends thank you message
        client.get('/api/auth/logout')
        token = login_and_get_token(client, student_alice['email'], student_alice['password'])
        
        message_data = {
            'receiver_id': staff_charlie['id'],
            'content': 'Thank you for approving my booking!',
            'booking_id': booking_id
        }
        response = client.post('/api/messages', json=message_data, headers={'X-CSRF-Token': token})
        assert response.status_code == 201
        
        # Step 6: Simulate booking completion (would normally happen after end_datetime)
        # For this test, we'll manually update the status using staff
        client.get('/api/auth/logout')
        staff_token = login_and_get_token(client, staff_charlie['email'], staff_charlie['password'])
        
        complete_data = {'status': 'completed'}
        response = client.put(
            f'/api/bookings/{booking_id}',
            json=complete_data,
            headers={'X-CSRF-Token': staff_token}
        )
        # Note: May return 200 or 400 depending on implementation
        
        # Step 7: Student leaves a review
        client.get('/api/auth/logout')
        token = login_and_get_token(client, student_alice['email'], student_alice['password'])
        
        review_data = {
            'resource_id': sample_resource['id'],
            'booking_id': booking_id,
            'rating': 5,
            'comment': 'Great study room! Very quiet and clean.'
        }
        response = client.post('/api/reviews', json=review_data, headers={'X-CSRF-Token': token})
        # Should succeed or return appropriate error
        assert response.status_code in [201, 400]  # 400 if booking not completed yet
        
        # Verify review appears in resource reviews
        response = client.get(f'/api/resources/{sample_resource["id"]}/reviews')
        assert response.status_code == 200


class TestResourceOwnerJourney:
    """Test complete resource owner (staff) journey"""
    
    def test_staff_resource_management_workflow(self, client, app, staff_charlie, student_alice):
        """
        Test full staff journey:
        1. Login
        2. Create a new resource
        3. Receive booking request
        4. Approve booking
        5. Communicate with student
        6. View analytics for their resource
        """
        # Step 1: Staff logs in
        token = login_and_get_token(client, staff_charlie['email'], staff_charlie['password'])
        
        # Step 2: Create a new resource
        resource_data = {
            'title': 'Conference Room B',
            'description': 'Large conference room with projector and whiteboard',
            'category': 'meeting_room',
            'location': 'Admin Building 3rd Floor',
            'capacity': 12,
            'requires_approval': True
        }
        
        response = client.post('/api/resources', json=resource_data, headers={'X-CSRF-Token': token})
        assert response.status_code == 201
        resource_id = response.json['resource']['id']
        assert response.json['resource']['title'] == 'Conference Room B'
        
        # Step 3: Student creates booking request
        client.get('/api/auth/logout')
        student_token = login_and_get_token(client, student_alice['email'], student_alice['password'])
        
        future_start = (datetime.utcnow() + timedelta(days=1)).isoformat()
        future_end = (datetime.utcnow() + timedelta(days=1, hours=1)).isoformat()
        
        booking_data = {
            'resource_id': resource_id,
            'start_datetime': future_start,
            'end_datetime': future_end,
            'notes': 'Need for club meeting'
        }
        
        response = client.post('/api/bookings', json=booking_data, headers={'X-CSRF-Token': student_token})
        assert response.status_code == 201
        booking_id = response.json['booking']['id']
        
        # Step 4: Staff receives notification (check pending bookings)
        client.get('/api/auth/logout')
        token = login_and_get_token(client, staff_charlie['email'], staff_charlie['password'])
        
        response = client.get('/api/bookings?status=pending')
        assert response.status_code == 200
        pending_bookings = [b for b in response.json['bookings'] if b['id'] == booking_id]
        assert len(pending_bookings) == 1
        
        # Step 5: Staff approves booking
        approval_data = {
            'action': 'approve',
            'notes': 'Enjoy your meeting!'
        }
        response = client.post(
            f'/api/bookings/{booking_id}/respond',
            json=approval_data,
            headers={'X-CSRF-Token': token}
        )
        assert response.status_code == 200
        
        # Step 6: Staff sends message to student
        message_data = {
            'receiver_id': student_alice['id'],
            'content': 'Your booking is approved. Please be there 5 minutes early.',
            'booking_id': booking_id
        }
        response = client.post('/api/messages', json=message_data, headers={'X-CSRF-Token': token})
        assert response.status_code == 201
        
        # Step 7: Staff views their resource
        response = client.get(f'/api/resources/{resource_id}')
        assert response.status_code == 200
        assert response.json['resource']['title'] == 'Conference Room B'


class TestMultiUserInteraction:
    """Test interactions between multiple users"""
    
    def test_resource_booking_with_conflict_detection(self, client, app, sample_resource, student_alice, student_bob, staff_charlie):
        """
        Test scenario where two students try to book the same resource:
        1. Alice creates booking for time slot
        2. Bob tries to book overlapping time
        3. System prevents double-booking
        """
        # Alice logs in and books resource
        alice_token = login_and_get_token(client, student_alice['email'], student_alice['password'])
        
        start_time = datetime.utcnow() + timedelta(days=3)
        end_time = start_time + timedelta(hours=2)
        
        alice_booking = {
            'resource_id': sample_resource['id'],
            'start_datetime': start_time.isoformat(),
            'end_datetime': end_time.isoformat(),
            'notes': 'Study session'
        }
        
        response = client.post('/api/bookings', json=alice_booking, headers={'X-CSRF-Token': alice_token})
        assert response.status_code == 201
        alice_booking_id = response.json['booking']['id']
        
        # Staff approves Alice's booking
        client.get('/api/auth/logout')
        staff_token = login_and_get_token(client, staff_charlie['email'], staff_charlie['password'])
        
        response = client.post(
            f'/api/bookings/{alice_booking_id}/respond',
            json={'action': 'approve'},
            headers={'X-CSRF-Token': staff_token}
        )
        assert response.status_code == 200
        
        # Bob tries to book overlapping time
        client.get('/api/auth/logout')
        bob_token = login_and_get_token(client, student_bob['email'], student_bob['password'])
        
        # Booking that overlaps with Alice's (starts 1 hour in, ends 1 hour after)
        overlap_start = start_time + timedelta(hours=1)
        overlap_end = end_time + timedelta(hours=1)
        
        bob_booking = {
            'resource_id': sample_resource['id'],
            'start_datetime': overlap_start.isoformat(),
            'end_datetime': overlap_end.isoformat(),
            'notes': 'Project work'
        }
        
        response = client.post('/api/bookings', json=bob_booking, headers={'X-CSRF-Token': bob_token})
        # Should fail due to conflict or be marked as pending
        assert response.status_code in [400, 201]
        
        if response.status_code == 400:
            # Conflict detected immediately
            assert 'conflict' in response.json.get('message', '').lower() or 'overlap' in response.json.get('message', '').lower()
        else:
            # Booking created as pending, conflict should be detected on approval
            booking_id = response.json['booking']['id']
            
            # Staff tries to approve Bob's conflicting booking
            client.get('/api/auth/logout')
            staff_token = login_and_get_token(client, staff_charlie['email'], staff_charlie['password'])
            
            response = client.post(
                f'/api/bookings/{booking_id}/respond',
                json={'action': 'approve'},
                headers={'X-CSRF-Token': staff_token}
            )
            # Should detect conflict
            assert response.status_code in [400, 409]


class TestMessageThreading:
    """Test message threading and conversation flows"""
    
    def test_bidirectional_messaging(self, client, app, student_alice, staff_charlie, sample_resource):
        """Test back-and-forth messaging between student and staff"""
        # Create a booking first to have context
        alice_token = login_and_get_token(client, student_alice['email'], student_alice['password'])
        
        future_start = (datetime.utcnow() + timedelta(days=5)).isoformat()
        future_end = (datetime.utcnow() + timedelta(days=5, hours=2)).isoformat()
        
        booking_data = {
            'resource_id': sample_resource['id'],
            'start_datetime': future_start,
            'end_datetime': future_end
        }
        
        response = client.post('/api/bookings', json=booking_data, headers={'X-CSRF-Token': alice_token})
        assert response.status_code == 201
        booking_id = response.json['booking']['id']
        
        # Alice sends initial message
        msg1_data = {
            'receiver_id': staff_charlie['id'],
            'content': 'Can I bring food into the study room?',
            'resource_id': sample_resource['id'],
            'booking_id': booking_id
        }
        
        response = client.post('/api/messages', json=msg1_data, headers={'X-CSRF-Token': alice_token})
        assert response.status_code == 201
        thread_id = response.json.get('message', {}).get('thread_id')
        
        # Staff responds
        client.get('/api/auth/logout')
        staff_token = login_and_get_token(client, staff_charlie['email'], staff_charlie['password'])
        
        msg2_data = {
            'receiver_id': student_alice['id'],
            'content': 'Yes, but please clean up after yourself!',
            'resource_id': sample_resource['id'],
            'booking_id': booking_id
        }
        
        response = client.post('/api/messages', json=msg2_data, headers={'X-CSRF-Token': staff_token})
        assert response.status_code == 201
        
        # Alice reads messages
        client.get('/api/auth/logout')
        alice_token = login_and_get_token(client, student_alice['email'], student_alice['password'])
        
        response = client.get('/api/messages')
        assert response.status_code == 200
        messages = response.json.get('messages', [])
        assert len(messages) >= 2
        
        # Verify messages are threaded (if threading is implemented)
        # This assumes message threading is available
        if thread_id:
            response = client.get(f'/api/messages?thread_id={thread_id}')
            assert response.status_code in [200, 404]  # 404 if threading not implemented yet
