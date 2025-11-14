"""
Debug script to test resource creation
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.user import User
from models.resource import Resource
from datetime import datetime
from werkzeug.security import generate_password_hash

def test_resource_creation():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        
        # Create a staff user
        staff = User(
            name='Charlie Staff',
            email='charlie@example.com',
            password_hash=generate_password_hash('password123'),
            role='staff',
            status='active',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(staff)
        db.session.commit()
        
        print(f"Created staff user: id={staff.id}, role={staff.role}")
        
        # Try to create a resource
        client = app.test_client()
        
        # Login
        response = client.post('/api/auth/login', json={
            'email': 'charlie@example.com',
            'password': 'password123'
        })
        print(f"Login response: {response.status_code}")
        print(f"Login data: {response.json}")
        
        if response.status_code == 200:
            token = response.json.get('csrf_token')
            print(f"CSRF token: {token}")
            
            # Create resource
            resource_data = {
                'title': 'Test Conference Room',
                'description': 'A test conference room',
                'category': 'meeting_room',
                'location': 'Building 1',
                'capacity': 10,
                'requires_approval': True
            }
            
            response = client.post('/api/resources', 
                                  json=resource_data, 
                                  headers={'X-CSRF-Token': token})
            print(f"\nResource creation response: {response.status_code}")
            print(f"Response data: {response.json}")
            
            if response.status_code == 201:
                print("✓ Resource created successfully!")
            else:
                print(f"✗ Resource creation failed!")
                print(f"Error: {response.json.get('message', 'No message')}")

if __name__ == '__main__':
    test_resource_creation()
