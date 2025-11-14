"""
Booking Service
Business logic layer for booking management.
Handles validation, conflict detection, and approval workflows.
"""

from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime, timedelta, timezone
from data_access.booking_repository import BookingRepository
from data_access.resource_repository import ResourceRepository
from models.booking import Booking
from models.resource import Resource
from models.user import User


class BookingService:
    """
    Service layer for booking operations.
    Provides business logic for booking management and conflict detection.
    """
    
    # Valid booking statuses
    VALID_STATUSES = {'pending', 'approved', 'rejected', 'cancelled', 'completed'}
    
    # Minimum booking duration (in minutes)
    MIN_DURATION_MINUTES = 15
    
    # Maximum booking duration (in days)
    MAX_DURATION_DAYS = 7
    
    # Minimum advance booking time (in minutes)
    MIN_ADVANCE_MINUTES = 30
    
    @staticmethod
    def validate_datetime_range(start_datetime: datetime, end_datetime: datetime) -> Tuple[bool, Optional[str]]:
        """
        Validate booking datetime range.
        
        Args:
            start_datetime: Booking start time
            end_datetime: Booking end time
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        now = datetime.utcnow()
        
        # Check if start is in the past
        if start_datetime < now:
            return False, "Booking start time cannot be in the past"
        
        # Check if end is before start
        if end_datetime <= start_datetime:
            return False, "Booking end time must be after start time"
        
        # Check minimum advance time
        if (start_datetime - now).total_seconds() < BookingService.MIN_ADVANCE_MINUTES * 60:
            return False, f"Bookings must be made at least {BookingService.MIN_ADVANCE_MINUTES} minutes in advance"
        
        # Check duration
        duration = end_datetime - start_datetime
        
        if duration.total_seconds() < BookingService.MIN_DURATION_MINUTES * 60:
            return False, f"Booking duration must be at least {BookingService.MIN_DURATION_MINUTES} minutes"
        
        if duration.days > BookingService.MAX_DURATION_DAYS:
            return False, f"Booking duration cannot exceed {BookingService.MAX_DURATION_DAYS} days"
        
        return True, None
    
    @staticmethod
    def create_booking(requester_id: int, resource_id: int,
                      start_datetime: datetime, end_datetime: datetime,
                      notes: Optional[str] = None) -> Tuple[Optional[Booking], Optional[str]]:
        """
        Create a new booking with validation and conflict checking.
        
        Args:
            requester_id: ID of user making booking
            resource_id: ID of resource to book
            start_datetime: Booking start time
            end_datetime: Booking end time
            notes: Optional notes
        
        Returns:
            Tuple[Optional[Booking], Optional[str]]: (booking, error_message)
        """
        # Normalize datetimes to naive UTC for consistent comparisons/storage
        if start_datetime.tzinfo is not None:
            start_datetime = start_datetime.astimezone(timezone.utc).replace(tzinfo=None)
        if end_datetime.tzinfo is not None:
            end_datetime = end_datetime.astimezone(timezone.utc).replace(tzinfo=None)

        # Check if resource exists
        resource = ResourceRepository.get_by_id(resource_id)
        if not resource:
            return None, "Resource not found"
        
        # Check if resource is published
        if resource.status != 'published':
            return None, "This resource is not available for booking"
        
        # Validate datetime range
        is_valid, error = BookingService.validate_datetime_range(start_datetime, end_datetime)
        if not is_valid:
            return None, error
        
        # Check for conflicts
        conflicts = BookingRepository.check_conflicts(
            resource_id=resource_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime
        )
        
        if conflicts:
            return None, "This time slot conflicts with an existing booking"
        
        # Create booking
        try:
            booking = BookingRepository.create(
                resource_id=resource_id,
                requester_id=requester_id,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                notes=notes
            )
            return booking, None
        except Exception as e:
            return None, f"Failed to create booking: {str(e)}"
    
    @staticmethod
    def get_booking(booking_id: int) -> Optional[Booking]:
        """
        Get a booking by ID.
        
        Args:
            booking_id: Booking ID
        
        Returns:
            Optional[Booking]: Booking object or None
        """
        return BookingRepository.get_by_id(booking_id)
    
    @staticmethod
    def list_user_bookings(user_id: int, status: Optional[str] = None,
                          page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        List bookings for a user with pagination.
        
        Args:
            user_id: User ID
            status: Optional status filter
            page: Page number
            per_page: Items per page
        
        Returns:
            Dict containing bookings and pagination info
        """
        offset = (page - 1) * per_page
        
        bookings = BookingRepository.get_all(
            requester_id=user_id,
            status=status,
            limit=per_page,
            offset=offset
        )
        
        total = BookingRepository.count(requester_id=user_id, status=status)
        total_pages = (total + per_page - 1) // per_page
        
        return {
            'bookings': [b.to_dict() for b in bookings],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
    
    @staticmethod
    def approve_booking(booking_id: int, approver: User,
                       approval_notes: Optional[str] = None) -> Tuple[Optional[Booking], Optional[str]]:
        """
        Approve a booking.
        
        Args:
            booking_id: Booking ID
            approver: User approving the booking
            approval_notes: Optional approval notes
        
        Returns:
            Tuple[Optional[Booking], Optional[str]]: (booking, error_message)
        """
        booking = BookingRepository.get_by_id(booking_id)
        if not booking:
            return None, "Booking not found"
        
        # Check if booking is in pending status
        if booking.status != 'pending':
            return None, f"Cannot approve booking with status: {booking.status}"
        
        # Check permissions (resource owner, staff, or admin)
        resource = booking.resource
        if not (resource.owner_id == approver.id or approver.is_staff() or approver.is_admin()):
            return None, "You don't have permission to approve this booking"
        
        # Check for conflicts again (in case status changed)
        conflicts = BookingRepository.check_conflicts(
            resource_id=booking.resource_id,
            start_datetime=booking.start_datetime,
            end_datetime=booking.end_datetime,
            exclude_booking_id=booking.id
        )
        
        if conflicts:
            return None, "This booking now conflicts with an approved booking"
        
        try:
            approved_booking = BookingRepository.approve(
                booking=booking,
                approver_id=approver.id,
                approval_notes=approval_notes
            )
            return approved_booking, None
        except Exception as e:
            return None, f"Failed to approve booking: {str(e)}"
    
    @staticmethod
    def reject_booking(booking_id: int, approver: User,
                      rejection_reason: str) -> Tuple[Optional[Booking], Optional[str]]:
        """
        Reject a booking.
        
        Args:
            booking_id: Booking ID
            approver: User rejecting the booking
            rejection_reason: Reason for rejection
        
        Returns:
            Tuple[Optional[Booking], Optional[str]]: (booking, error_message)
        """
        booking = BookingRepository.get_by_id(booking_id)
        if not booking:
            return None, "Booking not found"
        
        # Check if booking is in pending status
        if booking.status != 'pending':
            return None, f"Cannot reject booking with status: {booking.status}"
        
        # Check permissions
        resource = booking.resource
        if not (resource.owner_id == approver.id or approver.is_staff() or approver.is_admin()):
            return None, "You don't have permission to reject this booking"
        
        if not rejection_reason or not rejection_reason.strip():
            return None, "Rejection reason is required"
        
        try:
            rejected_booking = BookingRepository.reject(
                booking=booking,
                approver_id=approver.id,
                rejection_reason=rejection_reason.strip()
            )
            return rejected_booking, None
        except Exception as e:
            return None, f"Failed to reject booking: {str(e)}"
    
    @staticmethod
    def cancel_booking(booking_id: int, user: User,
                      cancellation_reason: Optional[str] = None) -> Tuple[Optional[Booking], Optional[str]]:
        """
        Cancel a booking.
        
        Args:
            booking_id: Booking ID
            user: User cancelling the booking
            cancellation_reason: Optional cancellation reason
        
        Returns:
            Tuple[Optional[Booking], Optional[str]]: (booking, error_message)
        """
        booking = BookingRepository.get_by_id(booking_id)
        if not booking:
            return None, "Booking not found"
        
        # Check if booking can be cancelled
        if booking.status not in ['pending', 'approved']:
            return None, f"Cannot cancel booking with status: {booking.status}"
        
        # Check permissions (requester, resource owner, or admin)
        resource = booking.resource
        if not (booking.requester_id == user.id or resource.owner_id == user.id or user.is_admin()):
            return None, "You don't have permission to cancel this booking"
        
        try:
            cancelled_booking = BookingRepository.cancel(
                booking=booking,
                cancellation_reason=cancellation_reason
            )
            return cancelled_booking, None
        except Exception as e:
            return None, f"Failed to cancel booking: {str(e)}"
    
    @staticmethod
    def check_availability(resource_id: int, start_datetime: datetime,
                          end_datetime: datetime) -> Tuple[bool, Optional[str]]:
        """
        Check if a resource is available for a time slot.
        
        Args:
            resource_id: Resource ID
            start_datetime: Start time
            end_datetime: End time
        
        Returns:
            Tuple[bool, Optional[str]]: (is_available, message)
        """
        # Validate datetime range
        is_valid, error = BookingService.validate_datetime_range(start_datetime, end_datetime)
        if not is_valid:
            return False, error
        
        # Check for conflicts
        conflicts = BookingRepository.check_conflicts(
            resource_id=resource_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime
        )
        
        if conflicts:
            return False, f"Time slot conflicts with {len(conflicts)} existing booking(s)"
        
        return True, "Time slot is available"
    
    @staticmethod
    def get_resource_bookings(resource_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all bookings for a resource.
        
        Args:
            resource_id: Resource ID
            status: Optional status filter
        
        Returns:
            List of booking dictionaries
        """
        bookings = BookingRepository.get_by_resource(resource_id, status)
        return [b.to_dict() for b in bookings]
    
    @staticmethod
    def get_pending_approvals(user: User) -> List[Dict[str, Any]]:
        """
        Get pending bookings that need approval by user.
        
        Args:
            user: User object
        
        Returns:
            List of booking dictionaries
        """
        if user.is_admin():
            # Admins can see all pending bookings
            bookings = BookingRepository.get_all(status='pending')
        else:
            # Resource owners see their own resources' bookings
            bookings = BookingRepository.get_pending_for_resource_owner(user.id)
        
        return [b.to_dict() for b in bookings]
    
    @staticmethod
    def get_upcoming_bookings(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get upcoming bookings for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of bookings
        
        Returns:
            List of booking dictionaries
        """
        bookings = BookingRepository.get_upcoming(user_id, limit)
        return [b.to_dict() for b in bookings]
    
    @staticmethod
    def get_past_bookings(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get past bookings for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of bookings
        
        Returns:
            List of booking dictionaries
        """
        bookings = BookingRepository.get_past(user_id, limit)
        return [b.to_dict() for b in bookings]
    
    @staticmethod
    def can_user_view(booking: Booking, user: User) -> bool:
        """
        Check if user can view a booking.
        
        Args:
            booking: Booking to check
            user: User to check
        
        Returns:
            bool: True if user can view
        """
        # User can view if they are: requester, resource owner, or admin
        return (
            booking.requester_id == user.id or
            booking.resource.owner_id == user.id or
            user.is_admin()
        )
    
    @staticmethod
    def can_user_approve(booking: Booking, user: User) -> bool:
        """
        Check if user can approve/reject a booking.
        
        Args:
            booking: Booking to check
            user: User to check
        
        Returns:
            bool: True if user can approve/reject
        """
        # Resource owner, staff, or admin can approve
        return (
            booking.resource.owner_id == user.id or
            user.is_staff() or
            user.is_admin()
        )
    
    @staticmethod
    def can_user_cancel(booking: Booking, user: User) -> bool:
        """
        Check if user can cancel a booking.
        
        Args:
            booking: Booking to check
            user: User to check
        
        Returns:
            bool: True if user can cancel
        """
        # Requester, resource owner, or admin can cancel
        return (
            booking.requester_id == user.id or
            booking.resource.owner_id == user.id or
            user.is_admin()
        )
