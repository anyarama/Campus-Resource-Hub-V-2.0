"""
Debug script to test booking creation
"""
from datetime import datetime, timedelta
from backend.app import create_app
from backend.models.user import User
from backend.models.resource import Resource
from backend.extensions import db

app = create_app()
app.config.update({
    'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'WTF_CSRF_ENABLED': False,
    'SECRET_KEY': 'test-key',
})

with app.app_context():
    db.create_all()
    
    # Create users
    alice = User(
        name='Alice Student',
        email='alice@example.com',
        password='AlicePass123!',
        role='student'
    )
    charlie = User(
        name='Charlie Staff',
        email='charlie@example.com',
        password='CharliePass123!',
        role='staff'
    )
    db.session.add(alice)
    db.session.add(charlie)
    db.session.commit()
    
    # Create resource
    resource = Resource(
        owner_id=charlie.id,
        title='Study Room A',
        description='Test room',
        location='Library',
        category='study_room',
        capacity=6
    )
    resource.status = 'published'
    resource.requires_approval = True
    db.session.add(resource)
    db.session.commit()
    
    print(f"Alice ID: {alice.id}")
    print(f"Charlie ID: {charlie.id}")
    print(f"Resource ID: {resource.id}")
    
    # Test client
    client = app.test_client()
    
    # Login as Alice
    response = client.post('/api/auth/login', json={
        'email': 'alice@example.com',
        'password': 'AlicePass123!'
    })
    print(f"\nLogin Response: {response.status_code}")
    print(f"Login Data: {response.json}")
    
    # Try to create booking
    future_start = (datetime.utcnow() + timedelta(days=2)).isoformat()
    future_end = (datetime.utcnow() + timedelta(days=2, hours=2)).isoformat()
    
    booking_data = {
        'resource_id': resource.id,
        'start_datetime': future_start,
        'end_datetime': future_end,
        'notes': 'Test booking'
    }
    
    print(f"\nBooking data: {booking_data}")
    
    response = client.post('/api/bookings', json=booking_data)
    print(f"\nBooking Response: {response.status_code}")
    print(f"Booking Data: {response.json}")
