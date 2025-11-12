"""
Resource Repository
Data access layer for Resource model CRUD operations.
Handles all database queries and operations for resources.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import or_, and_
from backend.extensions import db
from backend.models.resource import Resource
from backend.models.user import User


class ResourceRepository:
    """
    Repository for Resource model data access operations.
    Handles all database queries and operations for resources.
    """
    
    @staticmethod
    def create(owner_id: int, title: str, description: Optional[str] = None,
               category: Optional[str] = None, location: Optional[str] = None,
               capacity: Optional[int] = None, images: Optional[List[str]] = None,
               availability_rules: Optional[Dict[str, Any]] = None,
               requires_approval: bool = True, status: str = 'draft') -> Resource:
        """
        Create a new resource.
        
        Args:
            owner_id: ID of the user creating the resource
            title: Resource title
            description: Resource description
            category: Resource category
            location: Resource location
            capacity: Resource capacity
            images: List of image URLs
            availability_rules: Availability rules as dictionary
            requires_approval: Whether bookings require approval
            status: Resource status ('draft', 'published', 'archived')
        
        Returns:
            Resource: Created resource object
        """
        resource = Resource(
            owner_id=owner_id,
            title=title,
            description=description,
            category=category,
            location=location,
            capacity=capacity,
            requires_approval=requires_approval,
            status=status
        )
        
        if images:
            resource.set_images(images)
        
        if availability_rules:
            resource.availability_rules = availability_rules
        
        db.session.add(resource)
        db.session.commit()
        return resource
    
    @staticmethod
    def get_by_id(resource_id: int) -> Optional[Resource]:
        """
        Retrieve a resource by ID.
        
        Args:
            resource_id: Resource ID
        
        Returns:
            Resource: Resource object or None if not found
        """
        return Resource.query.get(resource_id)
    
    @staticmethod
    def get_all(status: Optional[str] = None, category: Optional[str] = None,
                owner_id: Optional[int] = None, limit: Optional[int] = None,
                offset: int = 0, search: Optional[str] = None,
                location: Optional[str] = None) -> List[Resource]:
        """
        Retrieve all resources with optional filtering.
        
        Args:
            status: Filter by status ('draft', 'published', 'archived')
            category: Filter by category
            owner_id: Filter by owner ID
            limit: Maximum number of resources to return
            offset: Number of resources to skip (for pagination)
            search: Search term for title and description
            location: Filter by location
        
        Returns:
            List[Resource]: List of resource objects
        """
        query = Resource.query
        
        # Apply filters
        if status:
            query = query.filter_by(status=status)
        
        if category:
            query = query.filter_by(category=category)
        
        if owner_id:
            query = query.filter_by(owner_id=owner_id)
        
        if location:
            query = query.filter(Resource.location.ilike(f'%{location}%'))
        
        if search:
            search_filter = or_(
                Resource.title.ilike(f'%{search}%'),
                Resource.description.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # Order by creation date (newest first)
        query = query.order_by(Resource.created_at.desc())
        
        # Apply pagination
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def search(search_term: str, category: Optional[str] = None,
               location: Optional[str] = None, limit: int = 20) -> List[Resource]:
        """
        Search resources by title, description, location.
        
        Args:
            search_term: Search term
            category: Optional category filter
            location: Optional location filter
            limit: Maximum number of results
        
        Returns:
            List[Resource]: List of matching resources
        """
        query = Resource.query.filter_by(status='published')
        
        # Build search filter
        search_filter = or_(
            Resource.title.ilike(f'%{search_term}%'),
            Resource.description.ilike(f'%{search_term}%'),
            Resource.location.ilike(f'%{search_term}%')
        )
        query = query.filter(search_filter)
        
        if category:
            query = query.filter_by(category=category)
        
        if location:
            query = query.filter(Resource.location.ilike(f'%{location}%'))
        
        # Order by average rating (best first), then created date
        query = query.order_by(
            Resource.average_rating.desc().nullslast(),
            Resource.created_at.desc()
        )
        
        return query.limit(limit).all()
    
    @staticmethod
    def update(resource: Resource, **kwargs) -> Resource:
        """
        Update resource attributes.
        
        Args:
            resource: Resource object to update
            **kwargs: Field names and values to update
        
        Returns:
            Resource: Updated resource object
        """
        # Handle images separately
        if 'images' in kwargs:
            resource.set_images(kwargs.pop('images'))
        
        # Handle availability_rules separately
        if 'availability_rules' in kwargs:
            resource.availability_rules = kwargs.pop('availability_rules')
        
        # Update other fields
        for key, value in kwargs.items():
            if hasattr(resource, key):
                setattr(resource, key, value)
        
        resource.updated_at = datetime.utcnow()
        db.session.commit()
        return resource
    
    @staticmethod
    def update_status(resource: Resource, status: str) -> Resource:
        """
        Update resource status.
        
        Args:
            resource: Resource object to update
            status: New status ('draft', 'published', 'archived')
        
        Returns:
            Resource: Updated resource object
        """
        resource.status = status
        resource.updated_at = datetime.utcnow()
        db.session.commit()
        return resource
    
    @staticmethod
    def delete(resource: Resource) -> bool:
        """
        Delete a resource from the database.
        
        Args:
            resource: Resource object to delete
        
        Returns:
            bool: True if successful
        
        Note:
            This is a hard delete. Consider soft delete (status='archived')
            for production use.
        """
        try:
            db.session.delete(resource)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    @staticmethod
    def count(status: Optional[str] = None, category: Optional[str] = None,
              owner_id: Optional[int] = None) -> int:
        """
        Count resources with optional filtering.
        
        Args:
            status: Filter by status
            category: Filter by category
            owner_id: Filter by owner ID
        
        Returns:
            int: Number of resources matching criteria
        """
        query = Resource.query
        
        if status:
            query = query.filter_by(status=status)
        
        if category:
            query = query.filter_by(category=category)
        
        if owner_id:
            query = query.filter_by(owner_id=owner_id)
        
        return query.count()
    
    @staticmethod
    def get_categories() -> List[str]:
        """
        Get all unique categories from resources.
        
        Returns:
            List[str]: List of unique categories
        """
        categories = db.session.query(Resource.category).distinct().filter(
            Resource.category.isnot(None),
            Resource.status == 'published'
        ).all()
        
        return [cat[0] for cat in categories if cat[0]]
    
    @staticmethod
    def get_locations() -> List[str]:
        """
        Get all unique locations from resources.
        
        Returns:
            List[str]: List of unique locations
        """
        locations = db.session.query(Resource.location).distinct().filter(
            Resource.location.isnot(None),
            Resource.status == 'published'
        ).all()
        
        return [loc[0] for loc in locations if loc[0]]
    
    @staticmethod
    def get_by_owner(owner_id: int, status: Optional[str] = None) -> List[Resource]:
        """
        Get all resources owned by a specific user.
        
        Args:
            owner_id: Owner's user ID
            status: Optional status filter
        
        Returns:
            List[Resource]: List of resources owned by the user
        """
        query = Resource.query.filter_by(owner_id=owner_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Resource.created_at.desc()).all()
    
    @staticmethod
    def get_popular(limit: int = 10) -> List[Resource]:
        """
        Get popular resources based on bookings and ratings.
        
        Args:
            limit: Maximum number of resources to return
        
        Returns:
            List[Resource]: List of popular resources
        """
        return Resource.query.filter_by(status='published').order_by(
            Resource.average_rating.desc().nullslast(),
            Resource.review_count.desc()
        ).limit(limit).all()
    
    @staticmethod
    def is_owner(resource: Resource, user_id: int) -> bool:
        """
        Check if a user is the owner of a resource.
        
        Args:
            resource: Resource object
            user_id: User ID to check
        
        Returns:
            bool: True if user is the owner
        """
        return resource.owner_id == user_id
