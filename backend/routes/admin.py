"""
Admin Routes
REST API endpoints for admin dashboard and management.
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from backend.services.admin_service import AdminService
from backend.services.review_service import ReviewService
from backend.middleware.auth import admin_required

# Create admin blueprint
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/analytics', methods=['GET'])
@admin_required
def get_analytics():
    """
    Get system-wide analytics and statistics.
    
    GET /api/admin/analytics
    
    Requires: Admin authentication
    
    Returns:
        200: System analytics data
        401: Not authenticated
        403: Not authorized (not admin)
    """
    try:
        analytics = AdminService.get_system_analytics()
        
        return jsonify(analytics), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching analytics'
        }), 500


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """
    Get list of all users with filtering.
    
    GET /api/admin/users?role=student&status=active&page=1&per_page=20
    
    Requires: Admin authentication
    
    Query Parameters:
        role: Filter by role ('student', 'staff', 'admin')
        status: Filter by status ('active', 'suspended', 'inactive')
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
    
    Returns:
        200: List of users with pagination
        401: Not authenticated
        403: Not authorized
    """
    try:
        # Get query parameters
        role = request.args.get('role')
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Get users list
        result, error = AdminService.get_users_list(
            admin=current_user,
            role=role,
            status=status,
            page=page,
            per_page=per_page
        )
        
        if error:
            return jsonify({
                'error': 'Forbidden',
                'message': error
            }), 403
        
        return jsonify(result), 200
    
    except ValueError:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid page or per_page value'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching users'
        }), 500


@admin_bp.route('/users/<int:user_id>/role', methods=['PUT', 'PATCH'])
@admin_required
def update_user_role(user_id):
    """
    Update a user's role.
    
    PUT/PATCH /api/admin/users/:id/role
    
    Requires: Admin authentication
    
    Request Body:
        {
            "role": "staff"
        }
    
    Returns:
        200: User role updated
        400: Validation error
        403: Not authorized
        404: User not found
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body is required'
            }), 400
        
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({
                'error': 'Validation Error',
                'message': 'role is required'
            }), 400
        
        # Update user role
        user, error = AdminService.update_user_role(
            user_id=user_id,
            new_role=new_role,
            admin=current_user
        )
        
        if error:
            if 'not found' in error.lower():
                return jsonify({
                    'error': 'Not Found',
                    'message': error
                }), 404
            elif 'cannot change' in error.lower():
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
            'message': 'User role updated successfully',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while updating user role'
        }), 500


@admin_bp.route('/users/<int:user_id>/status', methods=['PUT', 'PATCH'])
@admin_required
def update_user_status(user_id):
    """
    Update a user's account status.
    
    PUT/PATCH /api/admin/users/:id/status
    
    Requires: Admin authentication
    
    Request Body:
        {
            "status": "suspended"
        }
    
    Returns:
        200: User status updated
        400: Validation error
        403: Not authorized
        404: User not found
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body is required'
            }), 400
        
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({
                'error': 'Validation Error',
                'message': 'status is required'
            }), 400
        
        # Update user status
        user, error = AdminService.update_user_status(
            user_id=user_id,
            new_status=new_status,
            admin=current_user
        )
        
        if error:
            if 'not found' in error.lower():
                return jsonify({
                    'error': 'Not Found',
                    'message': error
                }), 404
            elif 'cannot change' in error.lower():
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
            'message': 'User status updated successfully',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while updating user status'
        }), 500


@admin_bp.route('/resources', methods=['GET'])
@admin_required
def get_resources_moderation():
    """
    Get all resources for moderation.
    
    GET /api/admin/resources?status=draft&page=1&per_page=20
    
    Requires: Admin authentication
    
    Query Parameters:
        status: Filter by status ('published', 'draft', 'archived')
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
    
    Returns:
        200: List of resources with pagination
        401: Not authenticated
        403: Not authorized
    """
    try:
        # Get query parameters
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Get resources for moderation
        result, error = AdminService.get_resources_for_moderation(
            admin=current_user,
            status=status,
            page=page,
            per_page=per_page
        )
        
        if error:
            return jsonify({
                'error': 'Forbidden',
                'message': error
            }), 403
        
        return jsonify(result), 200
    
    except ValueError:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid page or per_page value'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching resources'
        }), 500


@admin_bp.route('/reviews/flagged', methods=['GET'])
@admin_required
def get_flagged_reviews():
    """
    Get all flagged reviews for moderation.
    
    GET /api/admin/reviews/flagged?page=1&per_page=20
    
    Requires: Admin authentication
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
    
    Returns:
        200: List of flagged reviews
        401: Not authenticated
        403: Not authorized
    """
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Get flagged reviews
        result, error = ReviewService.get_flagged_reviews(
            user=current_user,
            page=page,
            per_page=per_page
        )
        
        if error:
            return jsonify({
                'error': 'Forbidden',
                'message': error
            }), 403
        
        return jsonify(result), 200
    
    except ValueError:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid page or per_page value'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching flagged reviews'
        }), 500


@admin_bp.route('/reviews/<int:review_id>/hide', methods=['POST'])
@admin_required
def hide_review(review_id):
    """
    Hide a review (moderation action).
    
    POST /api/admin/reviews/:id/hide
    
    Requires: Admin authentication
    
    Request Body (optional):
        {
            "moderation_notes": "Inappropriate language"
        }
    
    Returns:
        200: Review hidden
        403: Not authorized
        404: Review not found
    """
    try:
        data = request.get_json() or {}
        moderation_notes = data.get('moderation_notes')
        
        # Hide review
        review, error = ReviewService.hide_review(
            review_id=review_id,
            user=current_user,
            moderation_notes=moderation_notes
        )
        
        if error:
            if 'not found' in error.lower():
                return jsonify({
                    'error': 'Not Found',
                    'message': error
                }), 404
            else:
                return jsonify({
                    'error': 'Bad Request',
                    'message': error
                }), 400
        
        return jsonify({
            'message': 'Review hidden successfully',
            'review': review.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while hiding the review'
        }), 500


@admin_bp.route('/reviews/<int:review_id>/unhide', methods=['POST'])
@admin_required
def unhide_review(review_id):
    """
    Unhide a review (reverse moderation).
    
    POST /api/admin/reviews/:id/unhide
    
    Requires: Admin authentication
    
    Returns:
        200: Review unhidden
        403: Not authorized
        404: Review not found
    """
    try:
        # Unhide review
        review, error = ReviewService.unhide_review(
            review_id=review_id,
            user=current_user
        )
        
        if error:
            if 'not found' in error.lower():
                return jsonify({
                    'error': 'Not Found',
                    'message': error
                }), 404
            else:
                return jsonify({
                    'error': 'Bad Request',
                    'message': error
                }), 400
        
        return jsonify({
            'message': 'Review unhidden successfully',
            'review': review.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while unhiding the review'
        }), 500


@admin_bp.route('/reports/activity', methods=['GET'])
@admin_required
def get_activity_report():
    """
    Get activity report for specified time period.
    
    GET /api/admin/reports/activity?days=30
    
    Requires: Admin authentication
    
    Query Parameters:
        days: Number of days to look back (default: 30, max: 365)
    
    Returns:
        200: Activity report data
        401: Not authenticated
        403: Not authorized
    """
    try:
        days = min(int(request.args.get('days', 30)), 365)
        
        report = AdminService.get_activity_report(days=days)
        
        return jsonify(report), 200
    
    except ValueError:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid days value'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while generating activity report'
        }), 500
