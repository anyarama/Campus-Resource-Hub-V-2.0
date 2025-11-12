"""
Input Validation Utility
Provides validation functions for user input to prevent injection attacks and data corruption.
"""

import re
from typing import Tuple, Optional
from datetime import datetime
import bleach


class InputValidator:
    """Validates and sanitizes user input."""
    
    # Email validation regex (RFC 5322 compliant)
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    # Username validation (alphanumeric, underscore, hyphen, 3-30 chars)
    USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_-]{3,30}$')
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    
    # String length limits
    MAX_NAME_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 5000
    MAX_TITLE_LENGTH = 200
    
    # Allowed HTML tags for rich text (very restrictive)
    ALLOWED_HTML_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'a']
    ALLOWED_HTML_ATTRS = {'a': ['href', 'title']}
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"
        
        if not isinstance(email, str):
            return False, "Email must be a string"
        
        # Trim whitespace
        email = email.strip()
        
        # Check length
        if len(email) > 254:  # RFC 5321
            return False, "Email is too long (maximum 254 characters)"
        
        # Check format
        if not InputValidator.EMAIL_REGEX.match(email):
            return False, "Invalid email format"
        
        # Check for dangerous characters
        if any(char in email for char in ['<', '>', '"', "'", ';', '--']):
            return False, "Email contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password meets security requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if not isinstance(password, str):
            return False, "Password must be a string"
        
        # Check length
        if len(password) < InputValidator.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {InputValidator.MIN_PASSWORD_LENGTH} characters"
        
        if len(password) > InputValidator.MAX_PASSWORD_LENGTH:
            return False, f"Password is too long (maximum {InputValidator.MAX_PASSWORD_LENGTH} characters)"
        
        # Check complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            return False, "Password must contain uppercase, lowercase, and numbers"
        
        return True, None
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, Optional[str]]:
        """
        Validate username format.
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username:
            return False, "Username is required"
        
        if not isinstance(username, str):
            return False, "Username must be a string"
        
        # Trim whitespace
        username = username.strip()
        
        # Check format
        if not InputValidator.USERNAME_REGEX.match(username):
            return False, "Username must be 3-30 characters, alphanumeric with _ or -"
        
        return True, None
    
    @staticmethod
    def validate_string(
        value: str,
        field_name: str = "Field",
        min_length: int = 0,
        max_length: int = 1000,
        required: bool = True,
        allow_empty: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate general string input.
        
        Args:
            value: String to validate
            field_name: Name of field (for error messages)
            min_length: Minimum length
            max_length: Maximum length
            required: Whether field is required
            allow_empty: Whether empty string is allowed
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            if required:
                return False, f"{field_name} is required"
            return True, None
        
        if not isinstance(value, str):
            return False, f"{field_name} must be a string"
        
        # Trim whitespace
        value = value.strip()
        
        if not value:
            if required and not allow_empty:
                return False, f"{field_name} cannot be empty"
            if allow_empty:
                return True, None
        
        # Check length
        if len(value) < min_length:
            return False, f"{field_name} must be at least {min_length} characters"
        
        if len(value) > max_length:
            return False, f"{field_name} is too long (maximum {max_length} characters)"
        
        # Check for null bytes
        if '\x00' in value:
            return False, f"{field_name} contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_integer(
        value: any,
        field_name: str = "Field",
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        required: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate integer input.
        
        Args:
            value: Value to validate
            field_name: Name of field
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            required: Whether field is required
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            if required:
                return False, f"{field_name} is required"
            return True, None
        
        # Try to convert to int
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            return False, f"{field_name} must be an integer"
        
        # Check range
        if min_value is not None and int_value < min_value:
            return False, f"{field_name} must be at least {min_value}"
        
        if max_value is not None and int_value > max_value:
            return False, f"{field_name} must be at most {max_value}"
        
        return True, None
    
    @staticmethod
    def validate_datetime(
        value: str,
        field_name: str = "Field",
        required: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate datetime string (ISO format).
        
        Args:
            value: Datetime string to validate
            field_name: Name of field
            required: Whether field is required
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value:
            if required:
                return False, f"{field_name} is required"
            return True, None
        
        if not isinstance(value, str):
            return False, f"{field_name} must be a string"
        
        # Try to parse ISO format
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return False, f"{field_name} must be a valid date/time in ISO format"
        
        return True, None
    
    @staticmethod
    def validate_choice(
        value: str,
        field_name: str,
        choices: list,
        required: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate value is one of allowed choices.
        
        Args:
            value: Value to validate
            field_name: Name of field
            choices: List of allowed values
            required: Whether field is required
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value:
            if required:
                return False, f"{field_name} is required"
            return True, None
        
        if value not in choices:
            return False, f"{field_name} must be one of: {', '.join(str(c) for c in choices)}"
        
        return True, None


class InputSanitizer:
    """Sanitizes user input to prevent injection attacks."""
    
    @staticmethod
    def sanitize_html(html: str, allowed_tags: list = None, allowed_attrs: dict = None) -> str:
        """
        Sanitize HTML to prevent XSS attacks.
        
        Args:
            html: HTML string to sanitize
            allowed_tags: List of allowed HTML tags
            allowed_attrs: Dict of allowed attributes per tag
            
        Returns:
            Sanitized HTML string
        """
        if not html:
            return ""
        
        if not isinstance(html, str):
            return str(html)
        
        # Use bleach library for sanitization
        allowed_tags = allowed_tags or InputValidator.ALLOWED_HTML_TAGS
        allowed_attrs = allowed_attrs or InputValidator.ALLOWED_HTML_ATTRS
        
        return bleach.clean(
            html,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        )
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """
        Sanitize general string input.
        
        Args:
            value: String to sanitize
            
        Returns:
            Sanitized string
        """
        if not value:
            return ""
        
        if not isinstance(value, str):
            value = str(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Remove control characters except common whitespace
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
        
        # Trim whitespace
        value = value.strip()
        
        return value
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        if not filename:
            return "unnamed"
        
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Remove leading dots (hidden files)
        filename = filename.lstrip('.')
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename or "unnamed"
    
    @staticmethod
    def sanitize_sql_like(value: str) -> str:
        """
        Sanitize string for use in SQL LIKE clause.
        
        Args:
            value: Value to sanitize
            
        Returns:
            Sanitized value with escaped wildcards
        """
        if not value:
            return ""
        
        # Escape special LIKE characters
        value = value.replace('\\', '\\\\')
        value = value.replace('%', '\\%')
        value = value.replace('_', '\\_')
        
        return value


def validate_request_data(data: dict, schema: dict) -> Tuple[bool, Optional[str], dict]:
    """
    Validate request data against a schema.
    
    Args:
        data: Request data dictionary
        schema: Validation schema with field rules
        
    Returns:
        Tuple of (is_valid, error_message, sanitized_data)
    
    Example schema:
        {
            'email': {'type': 'email', 'required': True},
            'name': {'type': 'string', 'required': True, 'max_length': 100},
            'age': {'type': 'integer', 'required': False, 'min_value': 0}
        }
    """
    sanitized_data = {}
    
    for field, rules in schema.items():
        value = data.get(field)
        field_type = rules.get('type', 'string')
        required = rules.get('required', False)
        
        # Validate based on type
        if field_type == 'email':
            is_valid, error = InputValidator.validate_email(value or "")
            if not is_valid and (required or value):
                return False, f"{field}: {error}", {}
            if value:
                sanitized_data[field] = value.strip().lower()
        
        elif field_type == 'string':
            is_valid, error = InputValidator.validate_string(
                value,
                field_name=field,
                min_length=rules.get('min_length', 0),
                max_length=rules.get('max_length', 1000),
                required=required
            )
            if not is_valid:
                return False, error, {}
            if value:
                sanitized_data[field] = InputSanitizer.sanitize_string(value)
        
        elif field_type == 'integer':
            is_valid, error = InputValidator.validate_integer(
                value,
                field_name=field,
                min_value=rules.get('min_value'),
                max_value=rules.get('max_value'),
                required=required
            )
            if not is_valid:
                return False, error, {}
            if value is not None:
                sanitized_data[field] = int(value)
        
        elif field_type == 'choice':
            is_valid, error = InputValidator.validate_choice(
                value,
                field, choices=rules.get('choices', []),
                required=required
            )
            if not is_valid:
                return False, error, {}
            if value:
                sanitized_data[field] = value
        
        elif field_type == 'html':
            if value:
                sanitized_data[field] = InputSanitizer.sanitize_html(value)
        
        # Add field to sanitized data even if None (if not required)
        if field not in sanitized_data and not required:
            sanitized_data[field] = None
    
    return True, None, sanitized_data
