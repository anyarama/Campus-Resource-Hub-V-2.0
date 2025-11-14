"""
Message Service
Business logic layer for messaging system.
Handles validation and thread management.
"""

from typing import Optional, Tuple, List, Dict, Any
from data_access.message_repository import MessageRepository
from data_access.user_repository import UserRepository
from models.message import Message
from models.user import User


class MessageService:
    """
    Service layer for message operations.
    Provides business logic for messaging and thread management.
    """
    
    # Maximum message content length
    MAX_CONTENT_LENGTH = 5000
    
    # Minimum message content length
    MIN_CONTENT_LENGTH = 1
    
    @staticmethod
    def send_message(sender_id: int, receiver_id: int, content: str,
                    thread_id: Optional[str] = None, booking_id: Optional[int] = None,
                    resource_id: Optional[int] = None) -> Tuple[Optional[Message], Optional[str]]:
        """
        Send a message to another user.
        
        Args:
            sender_id: ID of sender
            receiver_id: ID of receiver
            content: Message content
            thread_id: Optional thread ID
            booking_id: Optional booking ID
            resource_id: Optional resource ID
        
        Returns:
            Tuple[Optional[Message], Optional[str]]: (message, error_message)
        """
        # Validate content
        if not content or not content.strip():
            return None, "Message content is required"
        
        content = content.strip()
        
        if len(content) < MessageService.MIN_CONTENT_LENGTH:
            return None, f"Message must be at least {MessageService.MIN_CONTENT_LENGTH} character"
        
        if len(content) > MessageService.MAX_CONTENT_LENGTH:
            return None, f"Message cannot exceed {MessageService.MAX_CONTENT_LENGTH} characters"
        
        # Validate sender exists
        sender = UserRepository.get_by_id(sender_id)
        if not sender:
            return None, "Sender not found"
        
        # Cannot send message to self
        if sender_id == receiver_id:
            return None, "Cannot send message to yourself"
        
        # Validate receiver exists
        receiver = UserRepository.get_by_id(receiver_id)
        if not receiver:
            return None, "Receiver not found"
        
        # Check if receiver account is active
        if not receiver.is_active_user():
            return None, "Cannot send message to inactive user"
        
        try:
            message = MessageRepository.create(
                sender_id=sender_id,
                receiver_id=receiver_id,
                content=content,
                thread_id=thread_id,
                booking_id=booking_id,
                resource_id=resource_id
            )
            return message, None
        except Exception as e:
            return None, f"Failed to send message: {str(e)}"
    
    @staticmethod
    def get_user_threads(user_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get all message threads for a user with pagination.
        
        Args:
            user_id: User ID
            page: Page number
            per_page: Items per page
        
        Returns:
            Dict containing threads and pagination info
        """
        offset = (page - 1) * per_page
        
        threads = MessageRepository.get_user_threads(
            user_id=user_id,
            limit=per_page,
            offset=offset
        )
        
        # For pagination, we'd need a count of total threads
        # For now, we'll indicate if there might be more
        has_next = len(threads) == per_page
        
        return {
            'threads': threads,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': page > 1
            }
        }
    
    @staticmethod
    def get_thread_messages(thread_id: str, user_id: int,
                           page: int = 1, per_page: int = 50) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Get all messages in a thread with pagination.
        
        Args:
            thread_id: Thread ID
            user_id: User ID
            page: Page number
            per_page: Items per page
        
        Returns:
            Tuple[Optional[Dict], Optional[str]]: (result, error_message)
        """
        offset = (page - 1) * per_page
        
        messages = MessageRepository.get_thread_messages(
            thread_id=thread_id,
            user_id=user_id,
            limit=per_page,
            offset=offset
        )
        
        if not messages and page == 1:
            return None, "Thread not found or access denied"
        
        total = MessageRepository.count_thread_messages(thread_id, user_id)
        total_pages = (total + per_page - 1) // per_page
        
        return {
            'messages': [m.to_dict() for m in messages],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }, None
    
    @staticmethod
    def mark_message_as_read(message_id: int, user_id: int) -> Tuple[Optional[Message], Optional[str]]:
        """
        Mark a message as read.
        
        Args:
            message_id: Message ID
            user_id: User ID (must be receiver)
        
        Returns:
            Tuple[Optional[Message], Optional[str]]: (message, error_message)
        """
        message = MessageRepository.mark_as_read(message_id, user_id)
        
        if not message:
            return None, "Message not found or you are not the receiver"
        
        return message, None
    
    @staticmethod
    def mark_thread_as_read(thread_id: str, user_id: int) -> Tuple[int, Optional[str]]:
        """
        Mark all messages in a thread as read.
        
        Args:
            thread_id: Thread ID
            user_id: User ID
        
        Returns:
            Tuple[int, Optional[str]]: (count, error_message)
        """
        try:
            count = MessageRepository.mark_thread_as_read(thread_id, user_id)
            return count, None
        except Exception as e:
            return 0, f"Failed to mark thread as read: {str(e)}"
    
    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """
        Get count of unread messages for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            int: Number of unread messages
        """
        return MessageRepository.get_unread_count(user_id)
    
    @staticmethod
    def search_messages(user_id: int, search_term: str,
                       limit: int = 50) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Search messages by content.
        
        Args:
            user_id: User ID
            search_term: Search term
            limit: Maximum results
        
        Returns:
            Tuple[List[Dict], Optional[str]]: (messages, error_message)
        """
        if not search_term or not search_term.strip():
            return [], "Search term is required"
        
        search_term = search_term.strip()
        
        if len(search_term) < 2:
            return [], "Search term must be at least 2 characters"
        
        try:
            messages = MessageRepository.search_messages(
                user_id=user_id,
                search_term=search_term,
                limit=min(limit, 100)  # Cap at 100
            )
            return [m.to_dict() for m in messages], None
        except Exception as e:
            return [], f"Search failed: {str(e)}"
    
    @staticmethod
    def get_messages_by_booking(booking_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all messages related to a booking.
        
        Args:
            booking_id: Booking ID
            user_id: User ID
        
        Returns:
            List[Dict]: Messages related to booking
        """
        messages = MessageRepository.get_messages_by_booking(booking_id, user_id)
        return [m.to_dict() for m in messages]
    
    @staticmethod
    def get_messages_by_resource(resource_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all messages related to a resource.
        
        Args:
            resource_id: Resource ID
            user_id: User ID
        
        Returns:
            List[Dict]: Messages related to resource
        """
        messages = MessageRepository.get_messages_by_resource(resource_id, user_id)
        return [m.to_dict() for m in messages]
    
    @staticmethod
    def delete_message(message_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a message.
        
        Args:
            message_id: Message ID
            user_id: User ID (must be sender)
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        success = MessageRepository.delete_message(message_id, user_id)
        
        if not success:
            return False, "Message not found or you are not the sender"
        
        return True, None
    
    @staticmethod
    def can_user_access_message(message: Message, user: User) -> bool:
        """
        Check if user can access a message.
        
        Args:
            message: Message to check
            user: User to check
        
        Returns:
            bool: True if user can access
        """
        return message.sender_id == user.id or message.receiver_id == user.id
    
    @staticmethod
    def can_user_access_thread(thread_id: str, user_id: int) -> bool:
        """
        Check if user can access a thread.
        
        Args:
            thread_id: Thread ID
            user_id: User ID
        
        Returns:
            bool: True if user can access
        """
        # Get any message from the thread to check access
        messages = MessageRepository.get_thread_messages(thread_id, user_id, limit=1)
        return len(messages) > 0
    
    @staticmethod
    def get_recent_messages(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent messages for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of messages
        
        Returns:
            List[Dict]: Recent messages
        """
        messages = MessageRepository.get_recent_messages(user_id, limit=min(limit, 50))
        return [m.to_dict() for m in messages]
