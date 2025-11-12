"""
Authentication Middleware
RBAC (Role-Based Access Control) decorators and utilities.
Provides decorators for protecting routes with authentication and role requirements.
"""

from functools import wraps
from flask import jsonify
from flask_login import current_user
from backend.services.auth_service import AuthService


def login_required(f):
    """
    Decorator to require user authentication.
    
    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            return 'This is protected'
    
    Returns:
        401 Unauthorized if user is not authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication is required to access this resource.'
            }), 401
        
        # Check if user account is active
        if not current_user.is_active_user():
            return jsonify({
                'error': 'Forbidden',
                'message': 'Your account is not active.'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def role_required(*allowed_roles):
    """
    Decorator to require specific user role(s).
    Uses role hierarchy: student < staff < admin
    
    Usage:
        @app.route('/admin')
        @login_required
        @role_required('admin')
        def admin_route():
            return 'Admin only'
        
        @app.route('/staff-or-admin')
        @login_required
        @role_required('staff', 'admin')
        def staff_route():
            return 'Staff or Admin'
    
    Args:
        *allowed_roles: One or more role strings ('student', 'staff', 'admin')
    
    Returns:
        403 Forbidden if user doesn't have required role
        401 Unauthorized if user is not authenticated
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First check if user is authenticated
            if not current_user.is_authenticated:
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Authentication is required to access this resource.'
                }), 401
            
            # Check if user account is active
            if not current_user.is_active_user():
                return jsonify({
                    'error': 'Forbidden',
                    'message': 'Your account is not active.'
                }), 403
            
            # Check if user has any of the allowed roles using hierarchy
            has_access = False
            for role in allowed_roles:
                if AuthService.can_user_access(current_user, role):
                    has_access = True
                    break
            
            if not has_access:
                return jsonify({
                    'error': 'Forbidden',
                    'message': f'You do not have permission to access this resource. Required role: {" or ".join(allowed_roles)}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def admin_required(f):
    """
    Decorator to require admin role.
    Convenience wrapper around @role_required('admin').
    
    Usage:
        @app.route('/admin/users')
        @login_required
        @admin_required
        def admin_users():
            return 'Admin only'
    
    Returns:
        403 Forbidden if user is not an admin
        401 Unauthorized if user is not authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication is required to access this resource.'
            }), 401
        
        if not current_user.is_active_user():
            return jsonify({
                'error': 'Forbidden',
                'message': 'Your account is not active.'
            }), 403
        
        if not current_user.is_admin():
            return jsonify({
                'error': 'Forbidden',
                'message': 'You do not have permission to access this resource. Admin role required.'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def staff_required(f):
    """
    Decorator to require staff or admin role.
    Convenience wrapper around @role_required('staff').
    
    Usage:
        @app.route('/staff/resources')
        @login_required
        @staff_required
        def staff_resources():
            return 'Staff or Admin only'
    
    Returns:
        403 Forbidden if user is not staff or admin
        401 Unauthorized if user is not authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication is required to access this resource.'
            }), 401
        
        if not current_user.is_active_user():
            return jsonify({
                'error': 'Forbidden',
                'message': 'Your account is not active.'
            }), 403
        
        if not (current_user.is_staff() or current_user.is_admin()):
            return jsonify({
                'error': 'Forbidden',
                'message': 'You do not have permission to access this resource. Staff role required.'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def optional_auth(f):
    """
    Decorator for routes that work with or without authentication.
    Allows both authenticated and anonymous access.
    Authenticated users will have current_user available.
    
    Usage:
        @app.route('/public')
        @optional_auth
        def public_route():
            if current_user.is_authenticated:
                return f'Hello {current_user.name}'
            return 'Hello Guest'
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow access regardless of authentication status
        return f(*args, **kwargs)
    
    return decorated_function
