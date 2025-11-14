"""
User Model
Represents users in the Campus Resource Hub system.
Supports three roles: Student, Staff, Admin.
"""

from datetime import datetime
import secrets
from flask_login import UserMixin
from extensions import db, bcrypt


class User(UserMixin, db.Model):
    """
    User model with authentication and profile information.
    
    Implements Flask-Login's UserMixin for session management.
    """
    
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Basic Information
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    
    # Authentication
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role: 'student', 'staff', 'admin'
    role = db.Column(db.String(20), nullable=False, default='student', index=True)
    
    # Profile
    profile_image = db.Column(db.String(255), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    
    # Account Status
    # Status can be: 'active', 'pending', 'suspended'
    status = db.Column(db.String(20), nullable=False, default='active', index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # Resources owned by this user
    resources = db.relationship('Resource', back_populates='owner', lazy='dynamic',
                               foreign_keys='Resource.owner_id')
    
    # Bookings made by this user
    bookings = db.relationship('Booking', back_populates='requester', lazy='dynamic',
                              foreign_keys='Booking.requester_id')
    
    # Messages sent by this user
    sent_messages = db.relationship('Message', back_populates='sender', lazy='dynamic',
                                   foreign_keys='Message.sender_id')
    
    # Messages received by this user
    received_messages = db.relationship('Message', back_populates='receiver', lazy='dynamic',
                                       foreign_keys='Message.receiver_id')
    
    # Reviews written by this user
    reviews = db.relationship('Review', back_populates='reviewer', lazy='dynamic')
    
    def __init__(self, name, email, password=None, role='student', department=None):
        """
        Initialize a new user.
        
        Args:
            name (str): User's full name
            email (str): User's email address (must be unique)
            password (str | None): Plain text password (will be hashed). If
                omitted (e.g., in tests), a secure temporary password is
                generated and should be updated before login.
            role (str): User role ('student', 'staff', 'admin')
            department (str): User's department (optional)
        """
        self.name = name
        self.email = email
        # Ensure password_hash is always populated so model invariants hold
        self.set_password(password or self._generate_temp_password())
        self.role = role
        self.department = department
    
    def set_password(self, password):
        """
        Hash and set the user's password.
        
        Args:
            password (str): Plain text password
        """
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """
        Verify a password against the stored hash.
        
        Args:
            password (str): Plain text password to check
        
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            return bcrypt.check_password_hash(self.password_hash, password)
        except ValueError:
            # Occurs if password_hash contains an invalid or legacy format
            return False
        except Exception:
            return False
    
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'
    
    def is_staff(self):
        """Check if user has staff role."""
        return self.role == 'staff'
    
    def is_student(self):
        """Check if user has student role."""
        return self.role == 'student'
    
    def is_active_user(self):
        """Check if user account is active."""
        return self.status == 'active'
    
    def to_dict(self, include_email=False):
        """
        Convert user to dictionary representation.
        
        Args:
            include_email (bool): Whether to include email in output
        
        Returns:
            dict: User data
        """
        data = {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'department': self.department,
            'profile_image': self.profile_image,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_email:
            data['email'] = self.email
        
        return data
    
    def __repr__(self):
        """String representation of User."""
        return f'<User {self.email} ({self.role})>'

    @staticmethod
    def _generate_temp_password() -> str:
        """Generate a secure temporary password (used when password omitted)."""
        return secrets.token_urlsafe(16)
