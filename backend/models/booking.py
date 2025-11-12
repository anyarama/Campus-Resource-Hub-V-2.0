"""
Booking Model
Represents resource bookings/reservations in the Campus Resource Hub.
Includes conflict detection and approval workflow.
"""

from datetime import datetime
from backend.extensions import db


class Booking(db.Model):
    """
    Booking model for resource reservations.
    """
    
    __tablename__ = 'bookings'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False, index=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Booking Time Slot
    start_datetime = db.Column(db.DateTime, nullable=False, index=True)
    end_datetime = db.Column(db.DateTime, nullable=False, index=True)
    
    # Status: 'pending', 'approved', 'rejected', 'cancelled', 'completed'
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    
    # Approval/Rejection Details
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approval_notes = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Cancellation Details
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancellation_reason = db.Column(db.Text, nullable=True)
    
    # Additional Notes
    notes = db.Column(db.Text, nullable=True)  # Requester's notes
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resource = db.relationship('Resource', back_populates='bookings')
    requester = db.relationship('User', back_populates='bookings', foreign_keys=[requester_id])
    approver = db.relationship('User', foreign_keys=[approved_by])
    
    def __init__(self, resource_id, requester_id, start_datetime, end_datetime, notes=None):
        """
        Initialize a new booking.
        
        Args:
            resource_id (int): ID of resource being booked
            requester_id (int): ID of user making the booking
            start_datetime (datetime): Booking start time
            end_datetime (datetime): Booking end time
            notes (str): Optional notes from requester
        """
        self.resource_id = resource_id
        self.requester_id = requester_id
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.notes = notes
        
        # Auto-approve if resource doesn't require approval
        # This will be handled by the service layer
    
    def approve(self, approver_id, notes=None):
        """
        Approve the booking.
        
        Args:
            approver_id (int): ID of user approving the booking
            notes (str): Optional approval notes
        """
        self.status = 'approved'
        self.approved_by = approver_id
        self.approval_notes = notes
        self.updated_at = datetime.utcnow()
    
    def reject(self, approver_id, reason):
        """
        Reject the booking.
        
        Args:
            approver_id (int): ID of user rejecting the booking
            reason (str): Reason for rejection
        """
        self.status = 'rejected'
        self.approved_by = approver_id
        self.rejection_reason = reason
        self.updated_at = datetime.utcnow()
    
    def cancel(self, reason=None):
        """
        Cancel the booking.
        
        Args:
            reason (str): Optional cancellation reason
        """
        self.status = 'cancelled'
        self.cancelled_at = datetime.utcnow()
        self.cancellation_reason = reason
        self.updated_at = datetime.utcnow()
    
    def complete(self):
        """Mark booking as completed (after end_datetime has passed)."""
        self.status = 'completed'
        self.updated_at = datetime.utcnow()
    
    def is_active(self):
        """Check if booking is currently active (approved and within time slot)."""
        if self.status != 'approved':
            return False
        now = datetime.utcnow()
        return self.start_datetime <= now <= self.end_datetime
    
    def is_upcoming(self):
        """Check if booking is upcoming (approved and before start time)."""
        if self.status != 'approved':
            return False
        return datetime.utcnow() < self.start_datetime
    
    def is_past(self):
        """Check if booking is in the past."""
        return datetime.utcnow() > self.end_datetime
    
    def can_be_cancelled(self):
        """Check if booking can be cancelled (pending or approved, not past)."""
        return self.status in ['pending', 'approved'] and not self.is_past()
    
    def overlaps_with(self, other_start, other_end):
        """
        Check if this booking overlaps with another time slot.
        
        Args:
            other_start (datetime): Start time of other booking
            other_end (datetime): End time of other booking
        
        Returns:
            bool: True if there is an overlap
        """
        return (
            (self.start_datetime < other_end and self.end_datetime > other_start) or
            (other_start < self.end_datetime and other_end > self.start_datetime)
        )
    
    def get_duration_hours(self):
        """
        Calculate booking duration in hours.
        
        Returns:
            float: Duration in hours
        """
        if self.start_datetime and self.end_datetime:
            delta = self.end_datetime - self.start_datetime
            return delta.total_seconds() / 3600
        return 0
    
    def to_dict(self, include_resource=False, include_requester=False):
        """
        Convert booking to dictionary representation.
        
        Args:
            include_resource (bool): Include full resource details
            include_requester (bool): Include requester details
        
        Returns:
            dict: Booking data
        """
        data = {
            'id': self.id,
            'resource_id': self.resource_id,
            'requester_id': self.requester_id,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'status': self.status,
            'notes': self.notes,
            'duration_hours': self.get_duration_hours(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Include approval details if applicable
        if self.status in ['approved', 'rejected']:
            data['approved_by'] = self.approved_by
            if self.approval_notes:
                data['approval_notes'] = self.approval_notes
            if self.rejection_reason:
                data['rejection_reason'] = self.rejection_reason
        
        # Include cancellation details if applicable
        if self.status == 'cancelled':
            data['cancelled_at'] = self.cancelled_at.isoformat() if self.cancelled_at else None
            data['cancellation_reason'] = self.cancellation_reason
        
        # Include related objects if requested
        if include_resource and self.resource:
            data['resource'] = self.resource.to_dict()
        
        if include_requester and self.requester:
            data['requester'] = self.requester.to_dict()
        
        return data
    
    def __repr__(self):
        """String representation of Booking."""
        return f'<Booking {self.id}: {self.resource_id} by {self.requester_id} ({self.status})>'
