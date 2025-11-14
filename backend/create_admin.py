"""
Script to create an admin user in the database
"""
from app import create_app
from extensions import db
from models.user import User

app = create_app()

with app.app_context():
    # Create all database tables
    db.create_all()
    print("✓ Database tables created/verified")
    
    # Check if admin user exists
    admin = User.query.filter_by(email='admin@iu.edu').first()
    
    if admin:
        print("✓ Admin user already exists")
    else:
        # Create admin user
        admin = User(
            name="Admin User",
            email="admin@iu.edu",
            password="admin123"
        )
        admin.role = "admin"
        admin.department = "Administration"
        admin.status = "active"
        
        db.session.add(admin)
        db.session.commit()
        
        print("✓ Admin user created successfully")
        print(f"  Email: admin@iu.edu")
        print(f"  Password: admin123")
        print(f"  Role: admin")
