"""
Authentication Service
Business logic layer for user authentication and registration.
Handles validation, user creation, and authentication workflows.
"""

import re
from typing import Optional, Tuple, Dict, Any
from data_access.user_repository import UserRepository
from models.user import User


class AuthService:
    """
    Service layer for authentication operations.
    Provides business logic for user registration and authentication.
    """
    
    # Email validation regex pattern
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    
    # Valid roles
    VALID_ROLES = {'student', 'staff', 'admin'}
    
    # Valid statuses
    VALID_STATUSES = {'active', 'pending', 'suspended'}
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"
        
        if not AuthService.EMAIL_REGEX.match(email):
            return False, "Invalid email format"
        
        if len(email) > 120:
            return False, "Email is too long (max 120 characters)"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < AuthService.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {AuthService.MIN_PASSWORD_LENGTH} characters long"
        
        if len(password) > AuthService.MAX_PASSWORD_LENGTH:
            return False, f"Password is too long (max {AuthService.MAX_PASSWORD_LENGTH} characters)"
        
        # Check for at least one letter and one number
        has_letter = any(c.isalpha() for c in password)
        has_number = any(c.isdigit() for c in password)
        
        if not has_letter or not has_number:
            return False, "Password must contain at least one letter and one number"
        
        return True, None
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user name.
        
        Args:
            name: Name to validate
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not name:
            return False, "Name is required"
        
        if len(name) < 2:
            return False, "Name must be at least 2 characters long"
        
        if len(name) > 100:
            return False, "Name is too long (max 100 characters)"
        
        return True, None
    
    @staticmethod
    def validate_role(role: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user role.
        
        Args:
            role: Role to validate
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if role not in AuthService.VALID_ROLES:
            return False, f"Invalid role. Must be one of: {', '.join(AuthService.VALID_ROLES)}"
        
        return True, None
    
    @staticmethod
    def register_user(name: str, email: str, password: str, 
                     role: str = 'student', department: Optional[str] = None) -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new user with validation.
        
        Args:
            name: User's full name
            email: User's email address
            password: Plain text password
            role: User role (default: 'student')
            department: User's department (optional)
        
        Returns:
            Tuple[Optional[User], Optional[str]]: (user_object, error_message)
                Returns (user, None) on success
                Returns (None, error_message) on failure
        """
        # Validate name
        is_valid, error = AuthService.validate_name(name)
        if not is_valid:
            return None, error
        
        # Validate email
        is_valid, error = AuthService.validate_email(email)
        if not is_valid:
            return None, error
        
        # Check if email already exists
        if UserRepository.exists_by_email(email):
            return None, "Email is already registered"
        
        # Validate password
        is_valid, error = AuthService.validate_password(password)
        if not is_valid:
            return None, error
        
        # Validate role
        is_valid, error = AuthService.validate_role(role)
        if not is_valid:
            return None, error
        
        # Validate department if provided
        if department and len(department) > 100:
            return None, "Department name is too long (max 100 characters)"
        
        # Create user
        user = UserRepository.create(
            name=name,
            email=email,
            password=password,
            role=role,
            department=department
        )
        
        if not user:
            return None, "Failed to create user account. Please try again."
        
        return user, None
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """
        Authenticate a user by email and password.
        
        Args:
            email: User's email address
            password: Plain text password
        
        Returns:
            Tuple[Optional[User], Optional[str]]: (user_object, error_message)
                Returns (user, None) on success
                Returns (None, error_message) on failure
        """
        if not email or not password:
            return None, "Email and password are required"
        
        # Get user by email
        user = UserRepository.get_by_email(email)
        
        if not user:
            return None, "Invalid email or password"
        
        # Check password
        if not user.check_password(password):
            return None, "Invalid email or password"
        
        # Check if account is active
        if user.status != 'active':
            if user.status == 'pending':
                return None, "Your account is pending approval"
            elif user.status == 'suspended':
                return None, "Your account has been suspended"
            else:
                return None, "Your account is not active"
        
        return user, None
    
    @staticmethod
    def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user profile information.
        
        Args:
            user_id: User's ID
        
        Returns:
            Optional[Dict]: User profile data or None if not found
        """
        user = UserRepository.get_by_id(user_id)
        
        if not user:
            return None
        
        return user.to_dict(include_email=True)
    
    @staticmethod
    def update_user_profile(user_id: int, **kwargs) -> Tuple[Optional[User], Optional[str]]:
        """
        Update user profile information.
        
        Args:
            user_id: User's ID
            **kwargs: Fields to update (name, department, profile_image)
        
        Returns:
            Tuple[Optional[User], Optional[str]]: (updated_user, error_message)
        """
        user = UserRepository.get_by_id(user_id)
        
        if not user:
            return None, "User not found"
        
        # Validate name if provided
        if 'name' in kwargs:
            is_valid, error = AuthService.validate_name(kwargs['name'])
            if not is_valid:
                return None, error
        
        # Validate department if provided
        if 'department' in kwargs and kwargs['department']:
            if len(kwargs['department']) > 100:
                return None, "Department name is too long (max 100 characters)"
        
        # Filter allowed fields for profile updates
        allowed_fields = {'name', 'department', 'profile_image'}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not filtered_kwargs:
            return None, "No valid fields to update"
        
        try:
            updated_user = UserRepository.update(user, **filtered_kwargs)
            return updated_user, None
        except Exception as e:
            return None, f"Failed to update profile: {str(e)}"
    
    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        Change user password.
        
        Args:
            user_id: User's ID
            current_password: Current password for verification
            new_password: New password to set
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        user = UserRepository.get_by_id(user_id)
        
        if not user:
            return False, "User not found"
        
        # Verify current password
        if not user.check_password(current_password):
            return False, "Current password is incorrect"
        
        # Validate new password
        is_valid, error = AuthService.validate_password(new_password)
        if not is_valid:
            return False, error
        
        # Check that new password is different from current
        if user.check_password(new_password):
            return False, "New password must be different from current password"
        
        try:
            user.set_password(new_password)
            UserRepository.update(user)
            return True, None
        except Exception as e:
            return False, f"Failed to change password: {str(e)}"
    
    @staticmethod
    def can_user_access(user: User, required_role: str) -> bool:
        """
        Check if user has required role or higher privileges.
        
        Args:
            user: User object to check
            required_role: Required role ('student', 'staff', 'admin')
        
        Returns:
            bool: True if user has access, False otherwise
        
        Role hierarchy: student < staff < admin
        """
        if not user or not user.is_active_user():
            return False
        
        # Define role hierarchy
        role_hierarchy = {
            'student': 1,
            'staff': 2,
            'admin': 3
        }
        
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
