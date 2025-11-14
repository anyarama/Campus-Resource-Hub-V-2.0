"""
Review Model
Represents user reviews and ratings for resources.
Users can review resources after completing bookings.
"""

from datetime import datetime
from extensions import db


class Review(db.Model):
    """
    Review model for resource ratings and feedback.
    """
    
    __tablename__ = 'reviews'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False, index=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Optional: Link to specific booking
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True, index=True)
    
    # Rating (1-5 scale)
    rating = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4, or 5
    
    # Review Content
    comment = db.Column(db.Text, nullable=True)
    
    # Moderation
    is_flagged = db.Column(db.Boolean, default=False, nullable=False)
    is_hidden = db.Column(db.Boolean, default=False, nullable=False)
    moderation_notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resource = db.relationship('Resource', back_populates='reviews')
    reviewer = db.relationship('User', back_populates='reviews')
    booking = db.relationship('Booking', foreign_keys=[booking_id])
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        # Optional: Prevent multiple reviews for same booking
        # db.UniqueConstraint('booking_id', name='unique_booking_review'),
    )
    
    def __init__(self, resource_id, reviewer_id, rating, comment=None, booking_id=None):
        """
        Initialize a new review.
        
        Args:
            resource_id (int): ID of resource being reviewed
            reviewer_id (int): ID of user writing the review
            rating (int): Rating value (1-5)
            comment (str): Optional review comment
            booking_id (int): Optional related booking ID
        """
        self.resource_id = resource_id
        self.reviewer_id = reviewer_id
        self.rating = self._validate_rating(rating)
        self.comment = comment
        self.booking_id = booking_id
    
    @staticmethod
    def _validate_rating(rating):
        """
        Validate rating is within acceptable range.
        
        Args:
            rating (int): Rating value
        
        Returns:
            int: Validated rating
        
        Raises:
            ValueError: If rating is not between 1 and 5
        """
        try:
            rating_int = int(rating)
            if 1 <= rating_int <= 5:
                return rating_int
            raise ValueError("Rating must be between 1 and 5")
        except (TypeError, ValueError):
            raise ValueError("Rating must be an integer between 1 and 5")
    
    def update_rating(self, new_rating):
        """
        Update the review rating.
        
        Args:
            new_rating (int): New rating value (1-5)
        """
        self.rating = self._validate_rating(new_rating)
        self.updated_at = datetime.utcnow()
    
    def update_comment(self, new_comment):
        """
        Update the review comment.
        
        Args:
            new_comment (str): New comment text
        """
        self.comment = new_comment
        self.updated_at = datetime.utcnow()
    
    def flag(self, notes=None):
        """
        Flag review for moderation.
        
        Args:
            notes (str): Optional moderation notes
        """
        self.is_flagged = True
        if notes:
            self.moderation_notes = notes
    
    def unflag(self):
        """Remove flag from review."""
        self.is_flagged = False
    
    def hide(self, notes=None):
        """
        Hide review from public view.
        
        Args:
            notes (str): Optional moderation notes
        """
        self.is_hidden = True
        if notes:
            self.moderation_notes = notes
    
    def unhide(self):
        """Make review visible again."""
        self.is_hidden = False
    
    def is_visible(self):
        """Check if review is visible to public."""
        return not self.is_hidden
    
    def get_rating_stars(self):
        """
        Get rating as star string representation.
        
        Returns:
            str: Star representation (e.g., "★★★★☆")
        """
        filled = '★' * self.rating
        empty = '☆' * (5 - self.rating)
        return filled + empty
    
    def is_by_user(self, user_id):
        """
        Check if review was written by a specific user.
        
        Args:
            user_id (int): User ID to check
        
        Returns:
            bool: True if review was written by user
        """
        return self.reviewer_id == user_id
    
    def to_dict(self, include_reviewer=False, include_resource=False, include_moderation=False):
        """
        Convert review to dictionary representation.
        
        Args:
            include_reviewer (bool): Include reviewer details
            include_resource (bool): Include resource details
            include_moderation (bool): Include moderation details (admin only)
        
        Returns:
            dict: Review data
        """
        data = {
            'id': self.id,
            'resource_id': self.resource_id,
            'reviewer_id': self.reviewer_id,
            'rating': self.rating,
            'comment': self.comment,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Include moderation fields for admins
        if include_moderation:
            data['is_flagged'] = self.is_flagged
            data['is_hidden'] = self.is_hidden
            data['moderation_notes'] = self.moderation_notes
        
        # Include related objects if requested
        if include_reviewer and self.reviewer:
            data['reviewer'] = self.reviewer.to_dict()
        
        if include_resource and self.resource:
            data['resource'] = {
                'id': self.resource.id,
                'title': self.resource.title,
                'category': self.resource.category,
            }
        
        # Include booking context if present
        if self.booking_id:
            data['booking_id'] = self.booking_id
        
        return data
    
    def __repr__(self):
        """String representation of Review."""
        return f'<Review {self.id}: {self.rating}★ for resource {self.resource_id}>'
