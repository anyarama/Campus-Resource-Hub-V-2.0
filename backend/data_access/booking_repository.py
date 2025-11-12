"""
Booking Repository
Data access layer for Booking model CRUD operations.
Handles all database queries and operations for bookings.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import and_, or_
from backend.extensions import db
from backend.models.booking import Booking
from backend.models.resource import Resource
from backend.models.user import User


class BookingRepository:
    """
    Repository for Booking model data access operations.
    Handles all database queries and operations for bookings.
    """
    
    @staticmethod
    def create(resource_id: int, requester_id: int,
               start_datetime: datetime, end_datetime: datetime,
               notes: Optional[str] = None) -> Booking:
        """
        Create a new booking.
        
        Args:
            resource_id: ID of the resource being booked
            requester_id: ID of the user making the booking
            start_datetime: Booking start time
            end_datetime: Booking end time
            notes: Optional booking notes
        
        Returns:
            Booking: Created booking object
        """
        booking = Booking(
            resource_id=resource_id,
            requester_id=requester_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            notes=notes
        )
        # Status defaults to 'pending' in the model
        
        db.session.add(booking)
        db.session.commit()
        return booking
    
    @staticmethod
    def get_by_id(booking_id: int) -> Optional[Booking]:
        """
        Retrieve a booking by ID.
        
        Args:
            booking_id: Booking ID
        
        Returns:
            Booking: Booking object or None if not found
        """
        return Booking.query.get(booking_id)
    
    @staticmethod
    def get_all(status: Optional[str] = None, requester_id: Optional[int] = None,
                resource_id: Optional[int] = None, limit: Optional[int] = None,
                offset: int = 0) -> List[Booking]:
        """
        Retrieve all bookings with optional filtering.
        
        Args:
            status: Filter by status
            requester_id: Filter by requester
            resource_id: Filter by resource
            limit: Maximum number of bookings to return
            offset: Number of bookings to skip
        
        Returns:
            List[Booking]: List of booking objects
        """
        query = Booking.query
        
        if status:
            query = query.filter_by(status=status)
        
        if requester_id:
            query = query.filter_by(requester_id=requester_id)
        
        if resource_id:
            query = query.filter_by(resource_id=resource_id)
        
        # Order by start date (newest first)
        query = query.order_by(Booking.start_datetime.desc())
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_by_requester(requester_id: int, status: Optional[str] = None) -> List[Booking]:
        """
        Get all bookings made by a specific user.
        
        Args:
            requester_id: User ID
            status: Optional status filter
        
        Returns:
            List[Booking]: List of bookings
        """
        query = Booking.query.filter_by(requester_id=requester_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Booking.start_datetime.desc()).all()
    
    @staticmethod
    def get_by_resource(resource_id: int, status: Optional[str] = None) -> List[Booking]:
        """
        Get all bookings for a specific resource.
        
        Args:
            resource_id: Resource ID
            status: Optional status filter
        
        Returns:
            List[Booking]: List of bookings
        """
        query = Booking.query.filter_by(resource_id=resource_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Booking.start_datetime.desc()).all()
    
    @staticmethod
    def check_conflicts(resource_id: int, start_datetime: datetime,
                       end_datetime: datetime, exclude_booking_id: Optional[int] = None) -> List[Booking]:
        """
        Check for conflicting bookings for a resource in a time range.
        
        Args:
            resource_id: Resource ID to check
            start_datetime: Start of time range
            end_datetime: End of time range
            exclude_booking_id: Booking ID to exclude from check (for updates)
        
        Returns:
            List[Booking]: List of conflicting bookings
        """
        query = Booking.query.filter(
            Booking.resource_id == resource_id,
            Booking.status.in_(['pending', 'approved']),  # Only check active bookings
            or_(
                # New booking starts during existing booking
                and_(
                    Booking.start_datetime <= start_datetime,
                    Booking.end_datetime > start_datetime
                ),
                # New booking ends during existing booking
                and_(
                    Booking.start_datetime < end_datetime,
                    Booking.end_datetime >= end_datetime
                ),
                # New booking completely contains existing booking
                and_(
                    Booking.start_datetime >= start_datetime,
                    Booking.end_datetime <= end_datetime
                )
            )
        )
        
        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)
        
        return query.all()
    
    @staticmethod
    def update(booking: Booking, **kwargs) -> Booking:
        """
        Update booking attributes.
        
        Args:
            booking: Booking object to update
            **kwargs: Field names and values to update
        
        Returns:
            Booking: Updated booking object
        """
        for key, value in kwargs.items():
            if hasattr(booking, key):
                setattr(booking, key, value)
        
        booking.updated_at = datetime.utcnow()
        db.session.commit()
        return booking
    
    @staticmethod
    def approve(booking: Booking, approver_id: int,
                approval_notes: Optional[str] = None) -> Booking:
        """
        Approve a booking.
        
        Args:
            booking: Booking to approve
            approver_id: ID of user approving
            approval_notes: Optional approval notes
        
        Returns:
            Booking: Updated booking
        """
        booking.status = 'approved'
        booking.approved_by = approver_id
        booking.approval_notes = approval_notes
        booking.updated_at = datetime.utcnow()
        
        db.session.commit()
        return booking
    
    @staticmethod
    def reject(booking: Booking, approver_id: int,
               rejection_reason: str) -> Booking:
        """
        Reject a booking.
        
        Args:
            booking: Booking to reject
            approver_id: ID of user rejecting
            rejection_reason: Reason for rejection
        
        Returns:
            Booking: Updated booking
        """
        booking.status = 'rejected'
        booking.approved_by = approver_id
        booking.rejection_reason = rejection_reason
        booking.updated_at = datetime.utcnow()
        
        db.session.commit()
        return booking
    
    @staticmethod
    def cancel(booking: Booking, cancellation_reason: Optional[str] = None) -> Booking:
        """
        Cancel a booking.
        
        Args:
            booking: Booking to cancel
            cancellation_reason: Reason for cancellation
        
        Returns:
            Booking: Updated booking
        """
        booking.status = 'cancelled'
        booking.cancelled_at = datetime.utcnow()
        booking.cancellation_reason = cancellation_reason
        booking.updated_at = datetime.utcnow()
        
        db.session.commit()
        return booking
    
    @staticmethod
    def complete(booking: Booking) -> Booking:
        """
        Mark a booking as completed.
        
        Args:
            booking: Booking to complete
        
        Returns:
            Booking: Updated booking
        """
        booking.status = 'completed'
        booking.updated_at = datetime.utcnow()
        
        db.session.commit()
        return booking
    
    @staticmethod
    def delete(booking: Booking) -> bool:
        """
        Delete a booking from the database.
        
        Args:
            booking: Booking object to delete
        
        Returns:
            bool: True if successful
        """
        try:
            db.session.delete(booking)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    @staticmethod
    def count(status: Optional[str] = None, requester_id: Optional[int] = None,
              resource_id: Optional[int] = None) -> int:
        """
        Count bookings with optional filtering.
        
        Args:
            status: Filter by status
            requester_id: Filter by requester
            resource_id: Filter by resource
        
        Returns:
            int: Number of bookings
        """
        query = Booking.query
        
        if status:
            query = query.filter_by(status=status)
        
        if requester_id:
            query = query.filter_by(requester_id=requester_id)
        
        if resource_id:
            query = query.filter_by(resource_id=resource_id)
        
        return query.count()
    
    @staticmethod
    def get_pending_for_resource_owner(owner_id: int) -> List[Booking]:
        """
        Get all pending bookings for resources owned by a user.
        
        Args:
            owner_id: Resource owner's user ID
        
        Returns:
            List[Booking]: List of pending bookings
        """
        return Booking.query.join(Resource).filter(
            Resource.owner_id == owner_id,
            Booking.status == 'pending'
        ).order_by(Booking.created_at.desc()).all()
    
    @staticmethod
    def get_upcoming(requester_id: int, limit: int = 10) -> List[Booking]:
        """
        Get upcoming bookings for a user.
        
        Args:
            requester_id: User ID
            limit: Maximum number of bookings
        
        Returns:
            List[Booking]: List of upcoming bookings
        """
        now = datetime.utcnow()
        
        return Booking.query.filter(
            Booking.requester_id == requester_id,
            Booking.start_datetime > now,
            Booking.status.in_(['pending', 'approved'])
        ).order_by(Booking.start_datetime.asc()).limit(limit).all()
    
    @staticmethod
    def get_past(requester_id: int, limit: int = 10) -> List[Booking]:
        """
        Get past bookings for a user.
        
        Args:
            requester_id: User ID
            limit: Maximum number of bookings
        
        Returns:
            List[Booking]: List of past bookings
        """
        now = datetime.utcnow()
        
        return Booking.query.filter(
            Booking.requester_id == requester_id,
            Booking.end_datetime < now
        ).order_by(Booking.end_datetime.desc()).limit(limit).all()
