"""
Initialize Database and Create Admin User
Run this script to set up the database with all tables and create an admin account.
"""

from app import app
from extensions import db
from models.user import User

def init_database():
    """Initialize database and create admin user."""
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Tables created successfully")
        
        # Check if admin user already exists
        admin_email = 'admin@iu.edu'
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if existing_admin:
            print(f"✓ Admin user already exists: {admin_email}")
        else:
            # Create admin user
            print("Creating admin user...")
            admin = User(
                name='Admin User',
                email=admin_email,
                password='admin123',
                role='admin'
            )
            admin.status = 'active'
            
            db.session.add(admin)
            db.session.commit()
            print(f"✓ Admin user created: {admin_email} / admin123")
        
        print("\n✓ Database initialization complete!")
        print("\nYou can now log in with:")
        print("  Email: admin@iu.edu")
        print("  Password: admin123")

if __name__ == '__main__':
    init_database()
