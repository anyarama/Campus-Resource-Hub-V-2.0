"""
Authentication Routes
Handles user registration, login, logout, and profile endpoints.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user
from backend.services.auth_service import AuthService
from backend.middleware.auth import login_required

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account.
    
    POST /api/auth/register
    
    Request Body:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "SecurePass123",
            "role": "student",  # optional, defaults to 'student'
            "department": "Computer Science"  # optional
        }
    
    Returns:
        201: User created successfully
        400: Validation error or email already exists
        500: Server error
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body is required'
            }), 400
        
        # Extract fields
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        role = data.get('role', 'student').strip().lower()
        department = data.get('department', '').strip() if data.get('department') else None
        
        # Register user through service layer
        user, error = AuthService.register_user(
            name=name,
            email=email,
            password=password,
            role=role,
            department=department
        )
        
        if error:
            return jsonify({
                'error': 'Registration Failed',
                'message': error
            }), 400
        
        # Return user data (excluding sensitive info)
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(include_email=True)
        }), 201
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred during registration'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and create session.
    
    POST /api/auth/login
    
    Request Body:
        {
            "email": "john@example.com",
            "password": "SecurePass123",
            "remember_me": true  # optional, defaults to false
        }
    
    Returns:
        200: Login successful
        401: Invalid credentials or account not active
        400: Bad request
        500: Server error
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body is required'
            }), 400
        
        # Extract fields
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember_me = data.get('remember_me', False)
        
        # Authenticate user
        user, error = AuthService.authenticate_user(email, password)
        
        if error:
            return jsonify({
                'error': 'Authentication Failed',
                'message': error
            }), 401
        
        # Create session using Flask-Login
        login_user(user, remember=remember_me)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(include_email=True)
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred during login'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Logout user and destroy session.
    
    POST /api/auth/logout
    
    Requires: Authentication
    
    Returns:
        200: Logout successful
        401: Not authenticated
    """
    try:
        logout_user()
        
        return jsonify({
            'message': 'Logout successful'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred during logout'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """
    Get current authenticated user's profile.
    
    GET /api/auth/me
    
    Requires: Authentication
    
    Returns:
        200: User profile data
        401: Not authenticated
    """
    try:
        return jsonify({
            'user': current_user.to_dict(include_email=True)
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching user profile'
        }), 500


@auth_bp.route('/me', methods=['PUT', 'PATCH'])
@login_required
def update_current_user():
    """
    Update current user's profile.
    
    PUT/PATCH /api/auth/me
    
    Requires: Authentication
    
    Request Body:
        {
            "name": "John Smith",  # optional
            "department": "Computer Science",  # optional
            "profile_image": "https://..."  # optional
        }
    
    Returns:
        200: Profile updated successfully
        400: Validation error
        401: Not authenticated
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body is required'
            }), 400
        
        # Update profile through service layer
        updated_user, error = AuthService.update_user_profile(
            user_id=current_user.id,
            **data
        )
        
        if error:
            return jsonify({
                'error': 'Update Failed',
                'message': error
            }), 400
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': updated_user.to_dict(include_email=True)
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while updating profile'
        }), 500


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """
    Change current user's password.
    
    POST /api/auth/change-password
    
    Requires: Authentication
    
    Request Body:
        {
            "current_password": "OldPass123",
            "new_password": "NewPass456"
        }
    
    Returns:
        200: Password changed successfully
        400: Validation error or incorrect current password
        401: Not authenticated
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body is required'
            }), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Current password and new password are required'
            }), 400
        
        # Change password through service layer
        success, error = AuthService.change_password(
            user_id=current_user.id,
            current_password=current_password,
            new_password=new_password
        )
        
        if not success:
            return jsonify({
                'error': 'Password Change Failed',
                'message': error
            }), 400
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while changing password'
        }), 500


@auth_bp.route('/check-email', methods=['POST'])
def check_email():
    """
    Check if email is already registered.
    Useful for client-side validation during registration.
    
    POST /api/auth/check-email
    
    Request Body:
        {
            "email": "test@example.com"
        }
    
    Returns:
        200: Email availability status
        400: Bad request
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({
                'error': 'Bad Request',
                'message': 'Email is required'
            }), 400
        
        email = data.get('email', '').strip().lower()
        
        # Validate email format
        is_valid, error = AuthService.validate_email(email)
        if not is_valid:
            return jsonify({
                'available': False,
                'message': error
            }), 200
        
        # Check if exists
        from backend.data_access.user_repository import UserRepository
        exists = UserRepository.exists_by_email(email)
        
        return jsonify({
            'available': not exists,
            'message': 'Email is already registered' if exists else 'Email is available'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while checking email'
        }), 500
