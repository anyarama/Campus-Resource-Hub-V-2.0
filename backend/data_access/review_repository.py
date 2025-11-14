"""
Review Repository
Data access layer for review management.
Handles all database queries for reviews and ratings.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import func
from extensions import db
from models.review import Review


class ReviewRepository:
    """
    Repository for review data access operations.
    Provides methods for CRUD operations and rating calculations.
    """
    
    @staticmethod
    def create(resource_id: int, reviewer_id: int, rating: int,
              comment: Optional[str] = None, booking_id: Optional[int] = None) -> Review:
        """
        Create a new review.
        
        Args:
            resource_id: ID of resource being reviewed
            reviewer_id: ID of reviewer
            rating: Rating (1-5)
            comment: Optional review comment
            booking_id: Optional associated booking ID
        
        Returns:
            Review: Created review object
        """
        review = Review(
            resource_id=resource_id,
            reviewer_id=reviewer_id,
            rating=rating,
            comment=comment,
            booking_id=booking_id,
            is_flagged=False,
            is_hidden=False,
            timestamp=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(review)
        db.session.commit()
        
        # Update resource average rating
        ReviewRepository._update_resource_rating(resource_id)
        
        return review
    
    @staticmethod
    def get_by_id(review_id: int) -> Optional[Review]:
        """
        Get a review by ID.
        
        Args:
            review_id: Review ID
        
        Returns:
            Optional[Review]: Review object or None
        """
        return Review.query.get(review_id)
    
    @staticmethod
    def get_by_resource(resource_id: int, include_hidden: bool = False,
                       limit: int = 100, offset: int = 0) -> List[Review]:
        """
        Get all reviews for a resource.
        
        Args:
            resource_id: Resource ID
            include_hidden: Whether to include hidden reviews
            limit: Maximum number of reviews
            offset: Offset for pagination
        
        Returns:
            List[Review]: List of reviews
        """
        query = Review.query.filter(Review.resource_id == resource_id)
        
        if not include_hidden:
            query = query.filter(Review.is_hidden == False)
        
        reviews = query.order_by(Review.timestamp.desc()).limit(limit).offset(offset).all()
        
        return reviews
    
    @staticmethod
    def get_by_reviewer(reviewer_id: int, limit: int = 50, offset: int = 0) -> List[Review]:
        """
        Get all reviews by a reviewer.
        
        Args:
            reviewer_id: Reviewer ID
            limit: Maximum number of reviews
            offset: Offset for pagination
        
        Returns:
            List[Review]: List of reviews
        """
        reviews = Review.query.filter(
            Review.reviewer_id == reviewer_id
        ).order_by(Review.timestamp.desc()).limit(limit).offset(offset).all()
        
        return reviews
    
    @staticmethod
    def get_by_booking(booking_id: int) -> Optional[Review]:
        """
        Get review associated with a booking.
        
        Args:
            booking_id: Booking ID
        
        Returns:
            Optional[Review]: Review object or None
        """
        return Review.query.filter(Review.booking_id == booking_id).first()
    
    @staticmethod
    def update(review: Review, rating: Optional[int] = None,
              comment: Optional[str] = None) -> Review:
        """
        Update a review.
        
        Args:
            review: Review to update
            rating: New rating (optional)
            comment: New comment (optional)
        
        Returns:
            Review: Updated review
        """
        if rating is not None:
            review.rating = rating
        
        if comment is not None:
            review.comment = comment
        
        review.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Update resource average rating
        ReviewRepository._update_resource_rating(review.resource_id)
        
        return review
    
    @staticmethod
    def delete(review: Review) -> None:
        """
        Delete a review.
        
        Args:
            review: Review to delete
        """
        resource_id = review.resource_id
        
        db.session.delete(review)
        db.session.commit()
        
        # Update resource average rating
        ReviewRepository._update_resource_rating(resource_id)
    
    @staticmethod
    def flag_review(review: Review, user_id: int) -> Review:
        """
        Flag a review as inappropriate.
        
        Args:
            review: Review to flag
            user_id: ID of user flagging the review
        
        Returns:
            Review: Flagged review
        """
        review.is_flagged = True
        review.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return review
    
    @staticmethod
    def hide_review(review: Review, moderation_notes: Optional[str] = None) -> Review:
        """
        Hide a review (moderation action).
        
        Args:
            review: Review to hide
            moderation_notes: Notes from moderator
        
        Returns:
            Review: Hidden review
        """
        review.is_hidden = True
        review.moderation_notes = moderation_notes
        review.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Update resource average rating (excluding hidden reviews)
        ReviewRepository._update_resource_rating(review.resource_id)
        
        return review
    
    @staticmethod
    def unhide_review(review: Review) -> Review:
        """
        Unhide a review (reverse moderation).
        
        Args:
            review: Review to unhide
        
        Returns:
            Review: Unhidden review
        """
        review.is_hidden = False
        review.is_flagged = False
        review.moderation_notes = None
        review.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Update resource average rating
        ReviewRepository._update_resource_rating(review.resource_id)
        
        return review
    
    @staticmethod
    def get_flagged_reviews(limit: int = 100, offset: int = 0) -> List[Review]:
        """
        Get all flagged reviews for moderation.
        
        Args:
            limit: Maximum number of reviews
            offset: Offset for pagination
        
        Returns:
            List[Review]: List of flagged reviews
        """
        reviews = Review.query.filter(
            Review.is_flagged == True
        ).order_by(Review.updated_at.desc()).limit(limit).offset(offset).all()
        
        return reviews
    
    @staticmethod
    def count_by_resource(resource_id: int, include_hidden: bool = False) -> int:
        """
        Count reviews for a resource.
        
        Args:
            resource_id: Resource ID
            include_hidden: Whether to include hidden reviews
        
        Returns:
            int: Number of reviews
        """
        query = Review.query.filter(Review.resource_id == resource_id)
        
        if not include_hidden:
            query = query.filter(Review.is_hidden == False)
        
        return query.count()
    
    @staticmethod
    def get_average_rating(resource_id: int) -> Optional[float]:
        """
        Calculate average rating for a resource.
        
        Args:
            resource_id: Resource ID
        
        Returns:
            Optional[float]: Average rating or None
        """
        result = db.session.query(func.avg(Review.rating)).filter(
            Review.resource_id == resource_id,
            Review.is_hidden == False
        ).scalar()
        
        return float(result) if result else None
    
    @staticmethod
    def _update_resource_rating(resource_id: int) -> None:
        """
        Update resource's average rating and review count.
        
        Args:
            resource_id: Resource ID
        """
        from models.resource import Resource
        
        resource = Resource.query.get(resource_id)
        if not resource:
            return
        
        # Calculate average rating (excluding hidden reviews)
        avg_rating = ReviewRepository.get_average_rating(resource_id)
        
        # Count reviews (excluding hidden)
        review_count = ReviewRepository.count_by_resource(resource_id, include_hidden=False)
        
        # Update resource
        resource.average_rating = avg_rating
        resource.review_count = review_count
        
        db.session.commit()
    
    @staticmethod
    def user_has_reviewed_resource(user_id: int, resource_id: int) -> bool:
        """
        Check if user has already reviewed a resource.
        
        Args:
            user_id: User ID
            resource_id: Resource ID
        
        Returns:
            bool: True if user has reviewed
        """
        return Review.query.filter(
            Review.reviewer_id == user_id,
            Review.resource_id == resource_id
        ).first() is not None
    
    @staticmethod
    def get_recent_reviews(limit: int = 10) -> List[Review]:
        """
        Get recent reviews across all resources.
        
        Args:
            limit: Maximum number of reviews
        
        Returns:
            List[Review]: Recent reviews
        """
        reviews = Review.query.filter(
            Review.is_hidden == False
        ).order_by(Review.timestamp.desc()).limit(limit).all()
        
        return reviews
