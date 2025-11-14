"""
Resource Model
Represents bookable resources in the Campus Resource Hub.
Examples: study rooms, labs, equipment, event spaces.
"""

from datetime import datetime
import json
from extensions import db


class Resource(db.Model):
    """
    Resource model for campus resources available for booking.
    """
    
    __tablename__ = 'resources'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Owner (User who created/manages this resource)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Basic Information
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    
    # Classification
    category = db.Column(db.String(50), nullable=True, index=True)  # 'study_room', 'lab', 'equipment', etc.
    location = db.Column(db.String(200), nullable=True, index=True)
    
    # Capacity & Details
    capacity = db.Column(db.Integer, nullable=True)  # Max number of people/users
    
    # Images - stored as JSON array of image paths
    images = db.Column(db.Text, nullable=True)  # JSON: ["path1.jpg", "path2.jpg"]
    
    # Availability Rules - JSON blob for complex scheduling rules
    # Example: {"recurring": "weekly", "days": ["monday", "wednesday"], "hours": "9:00-17:00"}
    availability_rules = db.Column(db.Text, nullable=True)
    
    # Status: 'draft', 'published', 'archived'
    status = db.Column(db.String(20), nullable=False, default='draft', index=True)
    
    # Approval Settings
    requires_approval = db.Column(db.Boolean, default=False)  # Does booking need owner/admin approval?
    
    # Ratings & Reviews (calculated fields)
    average_rating = db.Column(db.Float, nullable=True, default=0.0)
    review_count = db.Column(db.Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = db.relationship('User', back_populates='resources', foreign_keys=[owner_id])
    bookings = db.relationship('Booking', back_populates='resource', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', back_populates='resource', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, owner_id, title=None, description=None, category=None, location=None, 
                 capacity=None, requires_approval=False, name=None, status='draft'):
        """
        Initialize a new resource.
        
        Args:
            owner_id (int): ID of user who owns this resource
            title (str): Resource title
            description (str): Resource description
            category (str): Resource category
            location (str): Physical location
            capacity (int): Maximum capacity
            requires_approval (bool): Whether bookings need approval
            name (str): Legacy alias for title (maintained for backward compatibility)
            status (str): Initial resource status (defaults to 'draft')
        """
        self.owner_id = owner_id
        resolved_title = title or name
        if not resolved_title:
            raise ValueError("Resource title is required")
        self.title = resolved_title
        self.description = description
        self.category = category
        self.location = location
        self.capacity = capacity
        self.requires_approval = requires_approval
        self.status = status
    
    def set_images(self, image_paths):
        """
        Store image paths as JSON.
        
        Args:
            image_paths (list): List of image file paths
        """
        if image_paths:
            self.images = json.dumps(image_paths)
        else:
            self.images = None
    
    def get_images(self):
        """
        Retrieve image paths from JSON.
        
        Returns:
            list: List of image paths or empty list
        """
        if self.images:
            try:
                return json.loads(self.images)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def set_availability_rules(self, rules):
        """
        Store availability rules as JSON.
        
        Args:
            rules (dict): Availability rules dictionary
        """
        if rules:
            self.availability_rules = json.dumps(rules)
        else:
            self.availability_rules = None
    
    def get_availability_rules(self):
        """
        Retrieve availability rules from JSON.
        
        Returns:
            dict: Availability rules or empty dict
        """
        if self.availability_rules:
            try:
                return json.loads(self.availability_rules)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def update_rating(self):
        """
        Recalculate average rating from all reviews.
        Should be called after a review is added/updated/deleted.
        """
        reviews = self.reviews.all()
        if reviews:
            self.review_count = len(reviews)
            self.average_rating = sum(r.rating for r in reviews) / len(reviews)
        else:
            self.review_count = 0
            self.average_rating = 0.0
    
    def is_published(self):
        """Check if resource is published."""
        return self.status == 'published'
    
    def is_available_for_booking(self):
        """Check if resource can be booked."""
        return self.status == 'published'
    
    def to_dict(self, include_owner=False, include_stats=True):
        """
        Convert resource to dictionary representation.
        
        Args:
            include_owner (bool): Include owner details
            include_stats (bool): Include rating/review stats
        
        Returns:
            dict: Resource data
        """
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'location': self.location,
            'capacity': self.capacity,
            'images': self.get_images(),
            'availability_rules': self.get_availability_rules(),
            'status': self.status,
            'requires_approval': self.requires_approval,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_stats:
            data['average_rating'] = self.average_rating
            data['review_count'] = self.review_count
        
        if include_owner and self.owner:
            data['owner'] = self.owner.to_dict()
        else:
            data['owner_id'] = self.owner_id
        
        return data
    
    def __repr__(self):
        """String representation of Resource."""
        return f'<Resource {self.title} ({self.category})>'

    @property
    def name(self):
        """Legacy compatibility alias for title."""
        return self.title

    @name.setter
    def name(self, value):
        """Update resource title via legacy name setter."""
        self.title = value
