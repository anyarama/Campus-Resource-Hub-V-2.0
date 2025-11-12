"""
Review Service
Business logic layer for review management.
Handles validation, rating system, and moderation.
"""

from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime, timedelta
from backend.data_access.review_repository import ReviewRepository
from backend.data_access.resource_repository import ResourceRepository
from backend.data_access.booking_repository import BookingRepository
from backend.models.review import Review
from backend.models.user import User


class ReviewService:
    """
    Service layer for review operations.
    Provides business logic for reviews and ratings.
    """
    
    # Rating range
    MIN_RATING = 1
    MAX_RATING = 5
    
    # Comment length limits
    MAX_COMMENT_LENGTH = 2000
    MIN_COMMENT_LENGTH = 10
    
    # Edit window (in days)
    EDIT_WINDOW_DAYS = 7
    
    @staticmethod
    def create_review(resource_id: int, reviewer_id: int, rating: int,
                     comment: Optional[str] = None,
                     booking_id: Optional[int] = None) -> Tuple[Optional[Review], Optional[str]]:
        """
        Create a new review for a resource.
        
        Args:
            resource_id: ID of resource to review
            reviewer_id: ID of reviewer
            rating: Rating (1-5)
            comment: Optional review comment
            booking_id: Optional associated booking ID
        
        Returns:
            Tuple[Optional[Review], Optional[str]]: (review, error_message)
        """
        # Validate rating
        if rating < ReviewService.MIN_RATING or rating > ReviewService.MAX_RATING:
            return None, f"Rating must be between {ReviewService.MIN_RATING} and {ReviewService.MAX_RATING}"
        
        # Validate comment if provided
        if comment:
            comment = comment.strip()
            
            if len(comment) < ReviewService.MIN_COMMENT_LENGTH:
                return None, f"Comment must be at least {ReviewService.MIN_COMMENT_LENGTH} characters"
            
            if len(comment) > ReviewService.MAX_COMMENT_LENGTH:
                return None, f"Comment cannot exceed {ReviewService.MAX_COMMENT_LENGTH} characters"
        
        # Check if resource exists
        resource = ResourceRepository.get_by_id(resource_id)
        if not resource:
            return None, "Resource not found"
        
        # Check if resource is published
        if resource.status != 'published':
            return None, "Can only review published resources"
        
        # Check if user has already reviewed this resource
        if ReviewRepository.user_has_reviewed_resource(reviewer_id, resource_id):
            return None, "You have already reviewed this resource"
        
        # If booking_id provided, validate it
        if booking_id:
            booking = BookingRepository.get_by_id(booking_id)
            if not booking:
                return None, "Booking not found"
            
            # Check if booking belongs to reviewer
            if booking.requester_id != reviewer_id:
                return None, "You can only review bookings you made"
            
            # Check if booking is for this resource
            if booking.resource_id != resource_id:
                return None, "Booking is not for this resource"
            
            # Check if booking is completed
            if booking.status != 'completed':
                return None, "Can only review completed bookings"
            
            # Check if booking has already been reviewed
            existing_review = ReviewRepository.get_by_booking(booking_id)
            if existing_review:
                return None, "This booking has already been reviewed"
        
        try:
            review = ReviewRepository.create(
                resource_id=resource_id,
                reviewer_id=reviewer_id,
                rating=rating,
                comment=comment,
                booking_id=booking_id
            )
            return review, None
        except Exception as e:
            return None, f"Failed to create review: {str(e)}"
    
    @staticmethod
    def update_review(review_id: int, user_id: int, rating: Optional[int] = None,
                     comment: Optional[str] = None) -> Tuple[Optional[Review], Optional[str]]:
        """
        Update an existing review.
        
        Args:
            review_id: Review ID
            user_id: User ID (must be reviewer)
            rating: New rating (optional)
            comment: New comment (optional)
        
        Returns:
            Tuple[Optional[Review], Optional[str]]: (review, error_message)
        """
        review = ReviewRepository.get_by_id(review_id)
        if not review:
            return None, "Review not found"
        
        # Check if user is the reviewer
        if review.reviewer_id != user_id:
            return None, "You can only edit your own reviews"
        
        # Check if review is within edit window
        edit_deadline = review.timestamp + timedelta(days=ReviewService.EDIT_WINDOW_DAYS)
        if datetime.utcnow() > edit_deadline:
            return None, f"Reviews can only be edited within {ReviewService.EDIT_WINDOW_DAYS} days"
        
        # Validate new rating if provided
        if rating is not None:
            if rating < ReviewService.MIN_RATING or rating > ReviewService.MAX_RATING:
                return None, f"Rating must be between {ReviewService.MIN_RATING} and {ReviewService.MAX_RATING}"
        
        # Validate new comment if provided
        if comment is not None:
            comment = comment.strip()
            
            if len(comment) < ReviewService.MIN_COMMENT_LENGTH:
                return None, f"Comment must be at least {ReviewService.MIN_COMMENT_LENGTH} characters"
            
            if len(comment) > ReviewService.MAX_COMMENT_LENGTH:
                return None, f"Comment cannot exceed {ReviewService.MAX_COMMENT_LENGTH} characters"
        
        try:
            updated_review = ReviewRepository.update(review, rating, comment)
            return updated_review, None
        except Exception as e:
            return None, f"Failed to update review: {str(e)}"
    
    @staticmethod
    def delete_review(review_id: int, user: User) -> Tuple[bool, Optional[str]]:
        """
        Delete a review.
        
        Args:
            review_id: Review ID
            user: User deleting the review (reviewer or admin)
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        review = ReviewRepository.get_by_id(review_id)
        if not review:
            return False, "Review not found"
        
        # Check permissions (reviewer or admin)
        if not (review.reviewer_id == user.id or user.is_admin()):
            return False, "You do not have permission to delete this review"
        
        try:
            ReviewRepository.delete(review)
            return True, None
        except Exception as e:
            return False, f"Failed to delete review: {str(e)}"
    
    @staticmethod
    def get_resource_reviews(resource_id: int, page: int = 1,
                            per_page: int = 20) -> Dict[str, Any]:
        """
        Get all reviews for a resource with pagination.
        
        Args:
            resource_id: Resource ID
            page: Page number
            per_page: Items per page
        
        Returns:
            Dict containing reviews and pagination info
        """
        offset = (page - 1) * per_page
        
        reviews = ReviewRepository.get_by_resource(
            resource_id=resource_id,
            include_hidden=False,
            limit=per_page,
            offset=offset
        )
        
        total = ReviewRepository.count_by_resource(resource_id, include_hidden=False)
        total_pages = (total + per_page - 1) // per_page
        
        # Get average rating
        avg_rating = ReviewRepository.get_average_rating(resource_id)
        
        return {
            'reviews': [r.to_dict() for r in reviews],
            'average_rating': avg_rating,
            'total_reviews': total,
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
    def get_user_reviews(user_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get all reviews by a user with pagination.
        
        Args:
            user_id: User ID
            page: Page number
            per_page: Items per page
        
        Returns:
            Dict containing reviews and pagination info
        """
        offset = (page - 1) * per_page
        
        reviews = ReviewRepository.get_by_reviewer(
            reviewer_id=user_id,
            limit=per_page,
            offset=offset
        )
        
        # Simple pagination (would need count query for exact total)
        has_next = len(reviews) == per_page
        
        return {
            'reviews': [r.to_dict() for r in reviews],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': page > 1
            }
        }
    
    @staticmethod
    def flag_review(review_id: int, user_id: int) -> Tuple[Optional[Review], Optional[str]]:
        """
        Flag a review as inappropriate.
        
        Args:
            review_id: Review ID
            user_id: ID of user flagging
        
        Returns:
            Tuple[Optional[Review], Optional[str]]: (review, error_message)
        """
        review = ReviewRepository.get_by_id(review_id)
        if not review:
            return None, "Review not found"
        
        # Can't flag own review
        if review.reviewer_id == user_id:
            return None, "You cannot flag your own review"
        
        # Can't flag already hidden reviews
        if review.is_hidden:
            return None, "This review is already hidden"
        
        try:
            flagged_review = ReviewRepository.flag_review(review, user_id)
            return flagged_review, None
        except Exception as e:
            return None, f"Failed to flag review: {str(e)}"
    
    @staticmethod
    def hide_review(review_id: int, user: User,
                   moderation_notes: Optional[str] = None) -> Tuple[Optional[Review], Optional[str]]:
        """
        Hide a review (admin/moderation action).
        
        Args:
            review_id: Review ID
            user: User hiding the review (must be admin)
            moderation_notes: Notes explaining moderation
        
        Returns:
            Tuple[Optional[Review], Optional[str]]: (review, error_message)
        """
        if not user.is_admin():
            return None, "Only admins can hide reviews"
        
        review = ReviewRepository.get_by_id(review_id)
        if not review:
            return None, "Review not found"
        
        if review.is_hidden:
            return None, "Review is already hidden"
        
        try:
            hidden_review = ReviewRepository.hide_review(review, moderation_notes)
            return hidden_review, None
        except Exception as e:
            return None, f"Failed to hide review: {str(e)}"
    
    @staticmethod
    def unhide_review(review_id: int, user: User) -> Tuple[Optional[Review], Optional[str]]:
        """
        Unhide a review (admin action).
        
        Args:
            review_id: Review ID
            user: User unhiding the review (must be admin)
        
        Returns:
            Tuple[Optional[Review], Optional[str]]: (review, error_message)
        """
        if not user.is_admin():
            return None, "Only admins can unhide reviews"
        
        review = ReviewRepository.get_by_id(review_id)
        if not review:
            return None, "Review not found"
        
        if not review.is_hidden:
            return None, "Review is not hidden"
        
        try:
            unhidden_review = ReviewRepository.unhide_review(review)
            return unhidden_review, None
        except Exception as e:
            return None, f"Failed to unhide review: {str(e)}"
    
    @staticmethod
    def get_flagged_reviews(user: User, page: int = 1, per_page: int = 20) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Get flagged reviews for moderation (admin only).
        
        Args:
            user: User requesting flagged reviews (must be admin)
            page: Page number
            per_page: Items per page
        
        Returns:
            Tuple[Optional[Dict], Optional[str]]: (result, error_message)
        """
        if not user.is_admin():
            return None, "Only admins can view flagged reviews"
        
        offset = (page - 1) * per_page
        
        reviews = ReviewRepository.get_flagged_reviews(limit=per_page, offset=offset)
        
        has_next = len(reviews) == per_page
        
        return {
            'reviews': [r.to_dict() for r in reviews],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': page > 1
            }
        }, None
    
    @staticmethod
    def can_user_edit_review(review: Review, user: User) -> bool:
        """
        Check if user can edit a review.
        
        Args:
            review: Review to check
            user: User to check
        
        Returns:
            bool: True if user can edit
        """
        # Must be the reviewer
        if review.reviewer_id != user.id:
            return False
        
        # Must be within edit window
        edit_deadline = review.timestamp + timedelta(days=ReviewService.EDIT_WINDOW_DAYS)
        return datetime.utcnow() <= edit_deadline
    
    @staticmethod
    def can_user_delete_review(review: Review, user: User) -> bool:
        """
        Check if user can delete a review.
        
        Args:
            review: Review to check
            user: User to check
        
        Returns:
            bool: True if user can delete
        """
        return review.reviewer_id == user.id or user.is_admin()
