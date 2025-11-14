"""
Message Repository
Data access layer for message management.
Handles all database queries for messages and threads.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import or_, and_, func
from extensions import db
from models.message import Message


class MessageRepository:
    """
    Repository for message data access operations.
    Provides methods for CRUD operations and thread management.
    """
    
    @staticmethod
    def create(sender_id: int, receiver_id: int, content: str,
              thread_id: Optional[str] = None, booking_id: Optional[int] = None,
              resource_id: Optional[int] = None) -> Message:
        """
        Create a new message.
        
        Args:
            sender_id: ID of message sender
            receiver_id: ID of message receiver
            content: Message content
            thread_id: Optional thread ID
            booking_id: Optional associated booking ID
            resource_id: Optional associated resource ID
        
        Returns:
            Message: Created message object
        """
        # Generate thread_id if not provided
        if not thread_id:
            # Sort user IDs to ensure consistent thread_id
            user_ids = sorted([sender_id, receiver_id])
            thread_id = f"thread_{user_ids[0]}_{user_ids[1]}"
            
            # If booking or resource is involved, append to thread_id
            if booking_id:
                thread_id += f"_booking_{booking_id}"
            elif resource_id:
                thread_id += f"_resource_{resource_id}"
        
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            thread_id=thread_id,
            booking_id=booking_id,
            resource_id=resource_id
        )
        # is_read defaults to False in the model
        # timestamp defaults to datetime.utcnow() in the model
        
        db.session.add(message)
        db.session.commit()
        
        return message
    
    @staticmethod
    def get_by_id(message_id: int) -> Optional[Message]:
        """
        Get a message by ID.
        
        Args:
            message_id: Message ID
        
        Returns:
            Optional[Message]: Message object or None
        """
        return Message.query.get(message_id)
    
    @staticmethod
    def get_user_threads(user_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all message threads for a user with latest message info.
        
        Args:
            user_id: User ID
            limit: Maximum number of threads
            offset: Offset for pagination
        
        Returns:
            List[Dict]: List of threads with metadata
        """
        # Subquery to get the latest message timestamp for each thread
        latest_msg_subquery = db.session.query(
            Message.thread_id,
            func.max(Message.timestamp).label('latest_timestamp')
        ).filter(
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)
        ).group_by(Message.thread_id).subquery()
        
        # Get threads with their latest messages
        threads = db.session.query(Message).join(
            latest_msg_subquery,
            and_(
                Message.thread_id == latest_msg_subquery.c.thread_id,
                Message.timestamp == latest_msg_subquery.c.latest_timestamp
            )
        ).order_by(Message.timestamp.desc()).limit(limit).offset(offset).all()
        
        result = []
        for msg in threads:
            # Get unread count for this thread
            unread_count = Message.query.filter(
                Message.thread_id == msg.thread_id,
                Message.receiver_id == user_id,
                Message.is_read == False
            ).count()
            
            # Determine other participant
            other_user_id = msg.receiver_id if msg.sender_id == user_id else msg.sender_id
            
            result.append({
                'thread_id': msg.thread_id,
                'other_user_id': other_user_id,
                'latest_message': msg.content,
                'latest_timestamp': msg.timestamp,
                'unread_count': unread_count,
                'booking_id': msg.booking_id,
                'resource_id': msg.resource_id
            })
        
        return result
    
    @staticmethod
    def get_thread_messages(thread_id: str, user_id: int,
                           limit: int = 100, offset: int = 0) -> List[Message]:
        """
        Get all messages in a thread.
        
        Args:
            thread_id: Thread ID
            user_id: User ID (for permission check)
            limit: Maximum number of messages
            offset: Offset for pagination
        
        Returns:
            List[Message]: List of messages in thread
        """
        messages = Message.query.filter(
            Message.thread_id == thread_id,
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)
        ).order_by(Message.timestamp.asc()).limit(limit).offset(offset).all()
        
        return messages
    
    @staticmethod
    def mark_as_read(message_id: int, user_id: int) -> Optional[Message]:
        """
        Mark a message as read.
        
        Args:
            message_id: Message ID
            user_id: User ID (must be receiver)
        
        Returns:
            Optional[Message]: Updated message or None
        """
        message = Message.query.filter(
            Message.id == message_id,
            Message.receiver_id == user_id
        ).first()
        
        if not message:
            return None
        
        if not message.is_read:
            message.is_read = True
            message.read_at = datetime.utcnow()
            db.session.commit()
        
        return message
    
    @staticmethod
    def mark_thread_as_read(thread_id: str, user_id: int) -> int:
        """
        Mark all messages in a thread as read for a user.
        
        Args:
            thread_id: Thread ID
            user_id: User ID (receiver)
        
        Returns:
            int: Number of messages marked as read
        """
        updated_count = Message.query.filter(
            Message.thread_id == thread_id,
            Message.receiver_id == user_id,
            Message.is_read == False
        ).update({
            'is_read': True,
            'read_at': datetime.utcnow()
        })
        
        db.session.commit()
        
        return updated_count
    
    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """
        Get count of unread messages for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            int: Number of unread messages
        """
        return Message.query.filter(
            Message.receiver_id == user_id,
            Message.is_read == False
        ).count()
    
    @staticmethod
    def search_messages(user_id: int, search_term: str,
                       limit: int = 50) -> List[Message]:
        """
        Search messages by content.
        
        Args:
            user_id: User ID
            search_term: Search term
            limit: Maximum results
        
        Returns:
            List[Message]: Matching messages
        """
        search_pattern = f"%{search_term}%"
        
        messages = Message.query.filter(
            or_(Message.sender_id == user_id, Message.receiver_id == user_id),
            Message.content.ilike(search_pattern)
        ).order_by(Message.timestamp.desc()).limit(limit).all()
        
        return messages
    
    @staticmethod
    def get_messages_by_booking(booking_id: int, user_id: int) -> List[Message]:
        """
        Get all messages related to a booking.
        
        Args:
            booking_id: Booking ID
            user_id: User ID (for permission check)
        
        Returns:
            List[Message]: Messages related to booking
        """
        messages = Message.query.filter(
            Message.booking_id == booking_id,
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)
        ).order_by(Message.timestamp.asc()).all()
        
        return messages
    
    @staticmethod
    def get_messages_by_resource(resource_id: int, user_id: int) -> List[Message]:
        """
        Get all messages related to a resource.
        
        Args:
            resource_id: Resource ID
            user_id: User ID (for permission check)
        
        Returns:
            List[Message]: Messages related to resource
        """
        messages = Message.query.filter(
            Message.resource_id == resource_id,
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)
        ).order_by(Message.timestamp.asc()).all()
        
        return messages
    
    @staticmethod
    def delete_message(message_id: int, user_id: int) -> bool:
        """
        Delete a message (soft delete - only for sender).
        
        Args:
            message_id: Message ID
            user_id: User ID (must be sender)
        
        Returns:
            bool: True if deleted, False otherwise
        """
        message = Message.query.filter(
            Message.id == message_id,
            Message.sender_id == user_id
        ).first()
        
        if not message:
            return False
        
        db.session.delete(message)
        db.session.commit()
        
        return True
    
    @staticmethod
    def count_thread_messages(thread_id: str, user_id: int) -> int:
        """
        Count messages in a thread for a user.
        
        Args:
            thread_id: Thread ID
            user_id: User ID
        
        Returns:
            int: Number of messages
        """
        return Message.query.filter(
            Message.thread_id == thread_id,
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)
        ).count()
    
    @staticmethod
    def get_recent_messages(user_id: int, limit: int = 10) -> List[Message]:
        """
        Get recent messages for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of messages
        
        Returns:
            List[Message]: Recent messages
        """
        messages = Message.query.filter(
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)
        ).order_by(Message.timestamp.desc()).limit(limit).all()
        
        return messages
