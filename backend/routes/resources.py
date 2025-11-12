"""
Resources Routes
REST API endpoints for resource management.
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from backend.services.resource_service import ResourceService
from backend.middleware.auth import login_required, optional_auth
from backend.extensions import limiter

# Create resources blueprint
resources_bp = Blueprint('resources', __name__)


@resources_bp.route('', methods=['GET'])
@optional_auth
def list_resources():
    """
    List all resources with filtering and pagination.
    
    GET /api/resources?status=published&category=study_room&page=1&per_page=20
    
    Query Parameters:
        status: Filter by status ('published', 'draft', 'archived')
        category: Filter by category
        location: Filter by location (partial match)
        search: Search in title and description
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
    
    Returns:
        200: List of resources with pagination
        500: Server error
    """
    try:
        # Get query parameters
        status = request.args.get('status', 'published')
        category = request.args.get('category')
        location = request.args.get('location')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # For non-authenticated users or students, only show published resources
        if not current_user.is_authenticated or current_user.is_student():
            status = 'published'
        
        # Get resources
        result = ResourceService.list_resources(
            status=status,
            category=category,
            location=location,
            search=search,
            page=page,
            per_page=per_page
        )
        
        return jsonify(result), 200
    
    except ValueError as e:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid page or per_page value'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching resources'
        }), 500


@resources_bp.route('/<int:resource_id>', methods=['GET'])
@optional_auth
def get_resource(resource_id):
    """
    Get a specific resource by ID.
    
    GET /api/resources/:id
    
    Returns:
        200: Resource details
        404: Resource not found
        403: Access denied (draft resources)
    """
    try:
        resource = ResourceService.get_resource(resource_id)
        
        if not resource:
            return jsonify({
                'error': 'Not Found',
                'message': 'Resource not found'
            }), 404
        
        # Check if user can view this resource
        # Draft and archived resources only visible to owner and admin
        if resource.status in ['draft', 'archived']:
            if not current_user.is_authenticated:
                return jsonify({
                    'error': 'Forbidden',
                    'message': 'This resource is not available'
                }), 403
            
            if not (resource.owner_id == current_user.id or current_user.is_admin()):
                return jsonify({
                    'error': 'Forbidden',
                    'message': 'You do not have permission to view this resource'
                }), 403
        
        return jsonify(resource.to_dict()), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching the resource'
        }), 500


@resources_bp.route('', methods=['POST'])
@login_required
@limiter.limit("20 per hour")
def create_resource():
    """
    Create a new resource.
    
    POST /api/resources
    
    Requires: Authentication
    
    Request Body:
        {
            "title": "Study Room A",
            "description": "Quiet study room with whiteboard",
            "category": "study_room",
            "location": "Library, 2nd Floor",
            "capacity": 8,
            "images": ["url1", "url2"],
            "availability_rules": {...},
            "requires_approval": true,
            "status": "draft"
        }
    
    Returns:
        201: Resource created
        400: Validation error
        401: Not authenticated
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body is required'
            }), 400
        
        # Create resource
        resource, error = ResourceService.create_resource(
            owner_id=current_user.id,
            title=data.get('title'),
            description=data.get('description'),
            category=data.get('category'),
            location=data.get('location'),
            capacity=data.get('capacity'),
            images=data.get('images'),
            availability_rules=data.get('availability_rules'),
            requires_approval=data.get('requires_approval', True),
            status=data.get('status', 'draft')
        )
        
        if error:
            return jsonify({
                'error': 'Validation Error',
                'message': error
            }), 400
        
        return jsonify({
            'message': 'Resource created successfully',
            'resource': resource.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while creating the resource'
        }), 500


@resources_bp.route('/<int:resource_id>', methods=['PUT', 'PATCH'])
@login_required
def update_resource(resource_id):
    """
    Update a resource.
    
    PUT/PATCH /api/resources/:id
    
    Requires: Authentication (owner or admin)
    
    Request Body:
        {
            "title": "Updated Title",
            "description": "Updated description",
            ...
        }
    
    Returns:
        200: Resource updated
        400: Validation error
        403: Not authorized
        404: Resource not found
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body is required'
            }), 400
        
        # Update resource
        resource, error = ResourceService.update_resource(
            resource_id=resource_id,
            user=current_user,
            **data
        )
        
        if error:
            if 'not found' in error.lower():
                return jsonify({
                    'error': 'Not Found',
                    'message': error
                }), 404
            elif 'permission' in error.lower():
                return jsonify({
                    'error': 'Forbidden',
                    'message': error
                }), 403
            else:
                return jsonify({
                    'error': 'Validation Error',
                    'message': error
                }), 400
        
        return jsonify({
            'message': 'Resource updated successfully',
            'resource': resource.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while updating the resource'
        }), 500


@resources_bp.route('/<int:resource_id>', methods=['DELETE'])
@login_required
def delete_resource(resource_id):
    """
    Delete (archive) a resource.
    
    DELETE /api/resources/:id
    
    Requires: Authentication (owner or admin)
    
    Returns:
        200: Resource deleted
        403: Not authorized
        404: Resource not found
    """
    try:
        success, error = ResourceService.delete_resource(
            resource_id=resource_id,
            user=current_user
        )
        
        if not success:
            if 'not found' in error.lower():
                return jsonify({
                    'error': 'Not Found',
                    'message': error
                }), 404
            elif 'permission' in error.lower():
                return jsonify({
                    'error': 'Forbidden',
                    'message': error
                }), 403
            else:
                return jsonify({
                    'error': 'Bad Request',
                    'message': error
                }), 400
        
        return jsonify({
            'message': 'Resource deleted successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while deleting the resource'
        }), 500


@resources_bp.route('/<int:resource_id>/publish', methods=['POST'])
@login_required
def publish_resource(resource_id):
    """
    Publish a draft resource.
    
    POST /api/resources/:id/publish
    
    Requires: Authentication (owner or admin)
    
    Returns:
        200: Resource published
        400: Validation error
        403: Not authorized
        404: Resource not found
    """
    try:
        resource, error = ResourceService.publish_resource(
            resource_id=resource_id,
            user=current_user
        )
        
        if error:
            if 'not found' in error.lower():
                return jsonify({
                    'error': 'Not Found',
                    'message': error
                }), 404
            elif 'permission' in error.lower():
                return jsonify({
                    'error': 'Forbidden',
                    'message': error
                }), 403
            else:
                return jsonify({
                    'error': 'Bad Request',
                    'message': error
                }), 400
        
        return jsonify({
            'message': 'Resource published successfully',
            'resource': resource.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while publishing the resource'
        }), 500


@resources_bp.route('/search', methods=['GET'])
def search_resources():
    """
    Search resources.
    
    GET /api/resources/search?q=study&category=study_room
    
    Query Parameters:
        q: Search term (required)
        category: Filter by category
        location: Filter by location
        limit: Max results (default: 20, max: 50)
    
    Returns:
        200: Search results
        400: Missing search term
    """
    try:
        search_term = request.args.get('q', '').strip()
        
        if not search_term:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Search term (q) is required'
            }), 400
        
        category = request.args.get('category')
        location = request.args.get('location')
        limit = min(int(request.args.get('limit', 20)), 50)
        
        results = ResourceService.search_resources(
            search_term=search_term,
            category=category,
            location=location,
            limit=limit
        )
        
        return jsonify({
            'query': search_term,
            'count': len(results),
            'results': results
        }), 200
    
    except ValueError:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid limit value'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while searching resources'
        }), 500


@resources_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    Get all available resource categories.
    
    GET /api/resources/categories
    
    Returns:
        200: List of categories
    """
    try:
        categories = ResourceService.get_categories()
        
        return jsonify({
            'categories': categories
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching categories'
        }), 500


@resources_bp.route('/my-resources', methods=['GET'])
@login_required
def get_my_resources():
    """
    Get current user's resources.
    
    GET /api/resources/my-resources?status=published
    
    Requires: Authentication
    
    Query Parameters:
        status: Filter by status
    
    Returns:
        200: List of user's resources
    """
    try:
        status = request.args.get('status')
        
        resources = ResourceService.get_user_resources(
            user_id=current_user.id,
            status=status
        )
        
        return jsonify({
            'count': len(resources),
            'resources': resources
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching your resources'
        }), 500


@resources_bp.route('/popular', methods=['GET'])
def get_popular_resources():
    """
    Get popular resources.
    
    GET /api/resources/popular?limit=10
    
    Query Parameters:
        limit: Max results (default: 10, max: 50)
    
    Returns:
        200: List of popular resources
    """
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
        
        resources = ResourceService.get_popular_resources(limit=limit)
        
        return jsonify({
            'count': len(resources),
            'resources': resources
        }), 200
    
    except ValueError:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid limit value'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching popular resources'
        }), 500
