"""
Message Model
Represents messages between users in the Campus Resource Hub.
Supports threaded conversations related to bookings and resources.
"""

from datetime import datetime
from backend.extensions import db


class Message(db.Model):
    """
    Message model for user-to-user communication.
    """
    
    __tablename__ = 'messages'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Thread ID - groups related messages together
    # Can be based on booking_id or resource_id to keep conversations organized
    thread_id = db.Column(db.String(100), nullable=True, index=True)
    
    # Foreign Keys
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Optional: Link to specific booking or resource
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True, index=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=True, index=True)
    
    # Message Content
    content = db.Column(db.Text, nullable=False)
    
    # Message Status
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    sender = db.relationship('User', back_populates='sent_messages', foreign_keys=[sender_id])
    receiver = db.relationship('User', back_populates='received_messages', foreign_keys=[receiver_id])
    booking = db.relationship('Booking', foreign_keys=[booking_id])
    resource = db.relationship('Resource', foreign_keys=[resource_id])
    
    def __init__(self, sender_id, receiver_id, content, thread_id=None, 
                 booking_id=None, resource_id=None):
        """
        Initialize a new message.
        
        Args:
            sender_id (int): ID of user sending the message
            receiver_id (int): ID of user receiving the message
            content (str): Message content
            thread_id (str): Optional thread identifier
            booking_id (int): Optional related booking ID
            resource_id (int): Optional related resource ID
        """
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.thread_id = thread_id
        self.booking_id = booking_id
        self.resource_id = resource_id
        
        # Auto-generate thread_id if not provided
        if not self.thread_id:
            if booking_id:
                self.thread_id = f'booking_{booking_id}'
            elif resource_id:
                self.thread_id = f'resource_{resource_id}'
            else:
                # Create thread based on user pair (smaller ID first for consistency)
                user_ids = sorted([sender_id, receiver_id])
                self.thread_id = f'users_{user_ids[0]}_{user_ids[1]}'
    
    def mark_as_read(self):
        """Mark message as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
    
    def mark_as_unread(self):
        """Mark message as unread."""
        self.is_read = False
        self.read_at = None
    
    def is_sent_by(self, user_id):
        """
        Check if message was sent by a specific user.
        
        Args:
            user_id (int): User ID to check
        
        Returns:
            bool: True if message was sent by user
        """
        return self.sender_id == user_id
    
    def is_received_by(self, user_id):
        """
        Check if message was received by a specific user.
        
        Args:
            user_id (int): User ID to check
        
        Returns:
            bool: True if message was received by user
        """
        return self.receiver_id == user_id
    
    def involves_user(self, user_id):
        """
        Check if user is involved in this message (sender or receiver).
        
        Args:
            user_id (int): User ID to check
        
        Returns:
            bool: True if user is sender or receiver
        """
        return self.sender_id == user_id or self.receiver_id == user_id
    
    def to_dict(self, include_sender=False, include_receiver=False, current_user_id=None):
        """
        Convert message to dictionary representation.
        
        Args:
            include_sender (bool): Include sender details
            include_receiver (bool): Include receiver details
            current_user_id (int): Current user ID for determining read status
        
        Returns:
            dict: Message data
        """
        data = {
            'id': self.id,
            'thread_id': self.thread_id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }
        
        # Include context links if present
        if self.booking_id:
            data['booking_id'] = self.booking_id
        if self.resource_id:
            data['resource_id'] = self.resource_id
        
        # Include related objects if requested
        if include_sender and self.sender:
            data['sender'] = self.sender.to_dict()
        
        if include_receiver and self.receiver:
            data['receiver'] = self.receiver.to_dict()
        
        # Add metadata for current user
        if current_user_id:
            data['is_sent_by_me'] = self.is_sent_by(current_user_id)
            data['is_received_by_me'] = self.is_received_by(current_user_id)
        
        return data
    
    def __repr__(self):
        """String representation of Message."""
        return f'<Message {self.id}: from {self.sender_id} to {self.receiver_id}>'
