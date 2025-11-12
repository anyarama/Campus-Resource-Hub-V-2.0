"""
Resource Service
Business logic layer for resource management.
Handles validation, permissions, and resource operations.
"""

from typing import Optional, List, Tuple, Dict, Any
from backend.data_access.resource_repository import ResourceRepository
from backend.models.resource import Resource
from backend.models.user import User


class ResourceService:
    """
    Service layer for resource operations.
    Provides business logic for resource management.
    """
    
    # Valid resource statuses
    VALID_STATUSES = {'draft', 'published', 'archived'}
    
    # Valid categories (can be extended)
    VALID_CATEGORIES = {
        'study_room', 'equipment', 'facility', 'vehicle',
        'technology', 'sports', 'event_space', 'other'
    }
    
    @staticmethod
    def validate_title(title: str) -> Tuple[bool, Optional[str]]:
        """
        Validate resource title.
        
        Args:
            title: Title to validate
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not title or not title.strip():
            return False, "Title is required"
        
        if len(title) < 3:
            return False, "Title must be at least 3 characters long"
        
        if len(title) > 200:
            return False, "Title is too long (max 200 characters)"
        
        return True, None
    
    @staticmethod
    def validate_category(category: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate resource category.
        
        Args:
            category: Category to validate
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if category and category not in ResourceService.VALID_CATEGORIES:
            return False, f"Invalid category. Must be one of: {', '.join(ResourceService.VALID_CATEGORIES)}"
        
        return True, None
   
    @staticmethod
    def validate_status(status: str) -> Tuple[bool, Optional[str]]:
        """
        Validate resource status.
        
        Args:
            status: Status to validate
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if status not in ResourceService.VALID_STATUSES:
            return False, f"Invalid status. Must be one of: {', '.join(ResourceService.VALID_STATUSES)}"
        
        return True, None
    
    @staticmethod
    def validate_capacity(capacity: Optional[int]) -> Tuple[bool, Optional[str]]:
        """
        Validate resource capacity.
        
        Args:
            capacity: Capacity to validate
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if capacity is not None:
            if capacity < 1:
                return False, "Capacity must be at least 1"
            
            if capacity > 10000:
                return False, "Capacity is too large (max 10,000)"
        
        return True, None
    
    @staticmethod
    def create_resource(owner_id: int, title: str, description: Optional[str] = None,
                       category: Optional[str] = None, location: Optional[str] = None,
                       capacity: Optional[int] = None, images: Optional[List[str]] = None,
                       availability_rules: Optional[Dict[str, Any]] = None,
                       requires_approval: bool = True,
                       status: str = 'draft') -> Tuple[Optional[Resource], Optional[str]]:
        """
        Create a new resource with validation.
        
        Args:
            owner_id: ID of the user creating the resource
            title: Resource title
            description: Resource description
            category: Resource category
            location: Resource location
            capacity: Resource capacity
            images: List of image URLs
            availability_rules: Availability rules
            requires_approval: Whether bookings require approval
            status: Resource status
        
        Returns:
            Tuple[Optional[Resource], Optional[str]]: (resource, error_message)
        """
        # Validate title
        is_valid, error = ResourceService.validate_title(title)
        if not is_valid:
            return None, error
        
        # Validate category
        is_valid, error = ResourceService.validate_category(category)
        if not is_valid:
            return None, error
        
        # Validate status
        is_valid, error = ResourceService.validate_status(status)
        if not is_valid:
            return None, error
        
        # Validate capacity
        is_valid, error = ResourceService.validate_capacity(capacity)
        if not is_valid:
            return None, error
        
        # Validate location
        if location and len(location) > 200:
            return None, "Location is too long (max 200 characters)"
        
        try:
            resource = ResourceRepository.create(
                owner_id=owner_id,
                title=title.strip(),
                description=description.strip() if description else None,
                category=category,
                location=location.strip() if location else None,
                capacity=capacity,
                images=images,
                availability_rules=availability_rules,
                requires_approval=requires_approval,
                status=status
            )
            return resource, None
        except Exception as e:
            return None, f"Failed to create resource: {str(e)}"
    
    @staticmethod
    def get_resource(resource_id: int) -> Optional[Resource]:
        """
        Get a resource by ID.
        
        Args:
            resource_id: Resource ID
        
        Returns:
            Optional[Resource]: Resource object or None
        """
        return ResourceRepository.get_by_id(resource_id)
    
    @staticmethod
    def list_resources(status: Optional[str] = 'published',
                      category: Optional[str] = None,
                      owner_id: Optional[int] = None,
                      page: int = 1, per_page: int = 20,
                      search: Optional[str] = None,
                      location: Optional[str] = None) -> Dict[str, Any]:
        """
        List resources with pagination and filtering.
        
        Args:
            status: Filter by status (default: published)
            category: Filter by category
            owner_id: Filter by owner
            page: Page number (1-indexed)
            per_page: Items per page
            search: Search term
            location: Filter by location
        
        Returns:
            Dict containing resources and pagination info
        """
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get resources
        resources = ResourceRepository.get_all(
            status=status,
            category=category,
            owner_id=owner_id,
            limit=per_page,
            offset=offset,
            search=search,
            location=location
        )
        
        # Get total count
        total = ResourceRepository.count(
            status=status,
            category=category,
            owner_id=owner_id
        )
        
        # Calculate pagination info
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
        }
    
    @staticmethod
    def search_resources(search_term: str, category: Optional[str] = None,
                        location: Optional[str] = None,
                        limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search resources.
        
        Args:
            search_term: Search term
            category: Optional category filter
            location: Optional location filter
            limit: Maximum results
        
        Returns:
            List of resource dictionaries
        """
        if not search_term or not search_term.strip():
            return []
        
        resources = ResourceRepository.search(
            search_term=search_term.strip(),
            category=category,
            location=location,
            limit=limit
        )
        
        return [r.to_dict() for r in resources]
    
    @staticmethod
    def update_resource(resource_id: int, user: User,
                       **kwargs) -> Tuple[Optional[Resource], Optional[str]]:
        """
        Update a resource with permission checking.
        
        Args:
            resource_id: Resource ID
            user: User making the update
            **kwargs: Fields to update
        
        Returns:
            Tuple[Optional[Resource], Optional[str]]: (resource, error_message)
        """
        # Get resource
        resource = ResourceRepository.get_by_id(resource_id)
        if not resource:
            return None, "Resource not found"
        
        # Check permissions (owner or admin)
        if not (ResourceRepository.is_owner(resource, user.id) or user.is_admin()):
            return None, "You don't have permission to update this resource"
        
        # Validate updates
        if 'title' in kwargs:
            is_valid, error = ResourceService.validate_title(kwargs['title'])
            if not is_valid:
                return None, error
            kwargs['title'] = kwargs['title'].strip()
        
        if 'category' in kwargs:
            is_valid, error = ResourceService.validate_category(kwargs['category'])
            if not is_valid:
                return None, error
        
        if 'status' in kwargs:
            is_valid, error = ResourceService.validate_status(kwargs['status'])
            if not is_valid:
                return None, error
        
        if 'capacity' in kwargs:
            is_valid, error = ResourceService.validate_capacity(kwargs['capacity'])
            if not is_valid:
                return None, error
        
        if 'location' in kwargs and kwargs['location']:
            if len(kwargs['location']) > 200:
                return None, "Location is too long (max 200 characters)"
            kwargs['location'] = kwargs['location'].strip()
        
        if 'description' in kwargs and kwargs['description']:
            kwargs['description'] = kwargs['description'].strip()
        
        try:
            updated_resource = ResourceRepository.update(resource, **kwargs)
            return updated_resource, None
        except Exception as e:
            return None, f"Failed to update resource: {str(e)}"
    
    @staticmethod
    def delete_resource(resource_id: int, user: User) -> Tuple[bool, Optional[str]]:
        """
        Delete a resource with permission checking.
        
        Args:
            resource_id: Resource ID
            user: User requesting deletion
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        # Get resource
        resource = ResourceRepository.get_by_id(resource_id)
        if not resource:
            return False, "Resource not found"
        
        # Check permissions (owner or admin)
        if not (ResourceRepository.is_owner(resource, user.id) or user.is_admin()):
            return False, "You don't have permission to delete this resource"
        
        # Soft delete by archiving instead of hard delete
        try:
            ResourceRepository.update_status(resource, 'archived')
            return True, None
        except Exception as e:
            return False, f"Failed to delete resource: {str(e)}"
    
    @staticmethod
    def publish_resource(resource_id: int, user: User) -> Tuple[Optional[Resource], Optional[str]]:
        """
        Publish a draft resource.
        
        Args:
            resource_id: Resource ID
            user: User making the request
        
        Returns:
            Tuple[Optional[Resource], Optional[str]]: (resource, error_message)
        """
        resource = ResourceRepository.get_by_id(resource_id)
        if not resource:
            return None, "Resource not found"
        
        # Check permissions
        if not (ResourceRepository.is_owner(resource, user.id) or user.is_admin()):
            return None, "You don't have permission to publish this resource"
        
        # Validate resource is complete enough to publish
        if not resource.title or len(resource.title.strip()) < 3:
            return None, "Resource must have a valid title to be published"
        
        if resource.status == 'published':
            return None, "Resource is already published"
        
        try:
            updated_resource = ResourceRepository.update_status(resource, 'published')
            return updated_resource, None
        except Exception as e:
            return None, f"Failed to publish resource: {str(e)}"
    
    @staticmethod
    def get_categories() -> List[str]:
        """
        Get all available categories.
        
        Returns:
            List of category names
        """
        return sorted(list(ResourceService.VALID_CATEGORIES))
    
    @staticmethod
    def get_user_resources(user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all resources owned by a user.
        
        Args:
            user_id: User ID
            status: Optional status filter
        
        Returns:
            List of resource dictionaries
        """
        resources = ResourceRepository.get_by_owner(user_id, status)
        return [r.to_dict() for r in resources]
    
    @staticmethod
    def get_popular_resources(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get popular resources.
        
        Args:
            limit: Maximum number of resources
        
        Returns:
            List of resource dictionaries
        """
        resources = ResourceRepository.get_popular(limit)
        return [r.to_dict() for r in resources]
    
    @staticmethod
    def can_user_edit(resource: Resource, user: User) -> bool:
        """
        Check if user can edit a resource.
        
        Args:
            resource: Resource to check
            user: User to check
        
        Returns:
            bool: True if user can edit
        """
        return ResourceRepository.is_owner(resource, user.id) or user.is_admin()
    
    @staticmethod
    def can_user_delete(resource: Resource, user: User) -> bool:
        """
        Check if user can delete a resource.
        
        Args:
            resource: Resource to check
            user: User to check
        
        Returns:
            bool: True if user can delete
        """
        return ResourceRepository.is_owner(resource, user.id) or user.is_admin()
