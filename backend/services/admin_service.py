"""
Admin Service
Business logic layer for admin operations.
Handles user management, analytics, and system-wide operations.
"""

from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import func
from extensions import db
from models.user import User
from models.resource import Resource
from models.booking import Booking
from models.message import Message
from models.review import Review
from data_access.user_repository import UserRepository


class AdminService:
    """
    Service layer for admin operations.
    Provides business logic for administration and analytics.
    """
    
    @staticmethod
    def get_system_analytics() -> Dict[str, Any]:
        """
        Get system-wide analytics and statistics.
        
        Returns:
            Dict: System analytics data
        """
        # User statistics
        total_users = User.query.count()
        active_users = User.query.filter(User.status == 'active').count()
        students = User.query.filter(User.role == 'student').count()
        staff = User.query.filter(User.role == 'staff').count()
        admins = User.query.filter(User.role == 'admin').count()
        
        # Resource statistics
        total_resources = Resource.query.count()
        published_resources = Resource.query.filter(Resource.status == 'published').count()
        draft_resources = Resource.query.filter(Resource.status == 'draft').count()
        archived_resources = Resource.query.filter(Resource.status == 'archived').count()
        
        # Booking statistics
        total_bookings = Booking.query.count()
        pending_bookings = Booking.query.filter(Booking.status == 'pending').count()
        approved_bookings = Booking.query.filter(Booking.status == 'approved').count()
        completed_bookings = Booking.query.filter(Booking.status == 'completed').count()
        
        # Message statistics
        total_messages = Message.query.count()
        unread_messages = Message.query.filter(Message.is_read == False).count()
        
        # Review statistics
        total_reviews = Review.query.count()
        flagged_reviews = Review.query.filter(Review.is_flagged == True).count()
        hidden_reviews = Review.query.filter(Review.is_hidden == True).count()
        average_rating = db.session.query(func.avg(Review.rating)).filter(
            Review.is_hidden == False
        ).scalar() or 0
        
        # Recent activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        new_users_week = User.query.filter(User.created_at >= seven_days_ago).count()
        new_resources_week = Resource.query.filter(Resource.created_at >= seven_days_ago).count()
        new_bookings_week = Booking.query.filter(Booking.created_at >= seven_days_ago).count()
        new_reviews_week = Review.query.filter(Review.timestamp >= seven_days_ago).count()
        
        return {
            'users': {
                'total': total_users,
                'active': active_users,
                'by_role': {
                    'students': students,
                    'staff': staff,
                    'admins': admins
                },
                'new_this_week': new_users_week
            },
            'resources': {
                'total': total_resources,
                'published': published_resources,
                'draft': draft_resources,
                'archived': archived_resources,
                'new_this_week': new_resources_week
            },
            'bookings': {
                'total': total_bookings,
                'pending': pending_bookings,
                'approved': approved_bookings,
                'completed': completed_bookings,
                'new_this_week': new_bookings_week
            },
            'messages': {
                'total': total_messages,
                'unread': unread_messages
            },
            'reviews': {
                'total': total_reviews,
                'flagged': flagged_reviews,
                'hidden': hidden_reviews,
                'average_rating': round(float(average_rating), 2),
                'new_this_week': new_reviews_week
            }
        }
    
    @staticmethod
    def update_user_role(user_id: int, new_role: str, admin: User) -> Tuple[Optional[User], Optional[str]]:
        """
        Update a user's role (admin only).
        
        Args:
            user_id: User ID to update
            new_role: New role ('student', 'staff', 'admin')
            admin: Admin performing the action
        
        Returns:
            Tuple[Optional[User], Optional[str]]: (user, error_message)
        """
        if not admin.is_admin():
            return None, "Only admins can update user roles"
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            return None, "User not found"
        
        # Validate role
        valid_roles = ['student', 'staff', 'admin']
        if new_role not in valid_roles:
            return None, f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        
        # Prevent admin from demoting themselves
        if user.id == admin.id and new_role != 'admin':
            return None, "You cannot change your own role"
        
        try:
            user.role = new_role
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, f"Failed to update user role: {str(e)}"
    
    @staticmethod
    def update_user_status(user_id: int, new_status: str, admin: User) -> Tuple[Optional[User], Optional[str]]:
        """
        Update a user's account status (admin only).
        
        Args:
            user_id: User ID to update
            new_status: New status ('active', 'suspended', 'inactive')
            admin: Admin performing the action
        
        Returns:
            Tuple[Optional[User], Optional[str]]: (user, error_message)
        """
        if not admin.is_admin():
            return None, "Only admins can update user status"
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            return None, "User not found"
        
        # Validate status
        valid_statuses = ['active', 'suspended', 'inactive']
        if new_status not in valid_statuses:
            return None, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        
        # Prevent admin from suspending themselves
        if user.id == admin.id and new_status != 'active':
            return None, "You cannot change your own status"
        
        try:
            user.status = new_status
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, f"Failed to update user status: {str(e)}"
    
    @staticmethod
    def get_users_list(admin: User, role: Optional[str] = None, status: Optional[str] = None,
                      page: int = 1, per_page: int = 20) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Get list of all users with filtering (admin only).
        
        Args:
            admin: Admin requesting the list
            role: Filter by role
            status: Filter by status
            page: Page number
            per_page: Items per page
        
        Returns:
            Tuple[Optional[Dict], Optional[str]]: (result, error_message)
        """
        if not admin.is_admin():
            return None, "Only admins can view all users"
        
        offset = (page - 1) * per_page
        
        query = User.query
        
        if role:
            query = query.filter(User.role == role)
        
        if status:
            query = query.filter(User.status == status)
        
        users = query.order_by(User.created_at.desc()).limit(per_page).offset(offset).all()
        
        # Get total count for pagination
        total = query.count()
        total_pages = (total + per_page - 1) // per_page
        
        return {
            'users': [u.to_dict() for u in users],
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
    def get_resources_for_moderation(admin: User, status: Optional[str] = None,
                                    page: int = 1, per_page: int = 20) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Get all resources for moderation (admin only).
        
        Args:
            admin: Admin requesting the list
            status: Filter by status
            page: Page number
            per_page: Items per page
        
        Returns:
            Tuple[Optional[Dict], Optional[str]]: (result, error_message)
        """
        if not admin.is_admin():
            return None, "Only admins can moderate resources"
        
        offset = (page - 1) * per_page
        
        query = Resource.query
        
        if status:
            query = query.filter(Resource.status == status)
        
        resources = query.order_by(Resource.created_at.desc()).limit(per_page).offset(offset).all()
        
        # Get total count
        total = query.count()
        total_pages = (total + per_page - 1) // per_page
        
        return {
            'resources': [r.to_dict() for r in resources],
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
    def get_activity_report(days: int = 30) -> Dict[str, Any]:
        """
        Get activity report for specified time period.
        
        Args:
            days: Number of days to look back
        
        Returns:
            Dict: Activity report data
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # New users
        new_users = User.query.filter(User.created_at >= start_date).count()
        
        # New resources
        new_resources = Resource.query.filter(Resource.created_at >= start_date).count()
        
        # Bookings by status
        bookings_created = Booking.query.filter(Booking.created_at >= start_date).count()
        bookings_approved = Booking.query.filter(
            Booking.created_at >= start_date,
            Booking.status == 'approved'
        ).count()
        bookings_completed = Booking.query.filter(
            Booking.created_at >= start_date,
            Booking.status == 'completed'
        ).count()
        
        # Messages sent
        messages_sent = Message.query.filter(Message.timestamp >= start_date).count()
        
        # Reviews submitted
        reviews_submitted = Review.query.filter(Review.timestamp >= start_date).count()
        reviews_flagged = Review.query.filter(
            Review.timestamp >= start_date,
            Review.is_flagged == True
        ).count()
        
        return {
            'period': f'Last {days} days',
            'start_date': start_date.isoformat(),
            'end_date': datetime.utcnow().isoformat(),
            'activity': {
                'new_users': new_users,
                'new_resources': new_resources,
                'bookings_created': bookings_created,
                'bookings_approved': bookings_approved,
                'bookings_completed': bookings_completed,
                'messages_sent': messages_sent,
                'reviews_submitted': reviews_submitted,
                'reviews_flagged': reviews_flagged
            }
        }
