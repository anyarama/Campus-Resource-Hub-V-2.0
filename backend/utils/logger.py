"""
Secure Logging Utility
Provides structured logging with security best practices.
Prevents sensitive data from being logged.
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import traceback


class SensitiveDataFilter(logging.Filter):
    """Filter to prevent sensitive data from being logged."""
    
    # Fields that should never be logged
    SENSITIVE_FIELDS = {
        'password', 'secret', 'token', 'api_key', 'access_token',
        'refresh_token', 'private_key', 'credit_card', 'ssn', 'csrf_token'
    }
    
    # Patterns to redact
    REDACTION_PATTERNS = [
        'password',
        'secret',
        'token',
        'key',
        'credential',
        'auth',
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log records to redact sensitive information.
        
        Args:
            record: Log record to filter
            
        Returns:
            bool: Always True (we modify but don't block records)
        """
        # Redact sensitive data in message
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self._redact_sensitive_data(record.msg)
        
        # Redact sensitive data in args
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, dict):
                record.args = self._redact_dict(record.args)
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(self._redact_sensitive_data(str(arg)) for arg in record.args)
        
        return True
    
    def _redact_sensitive_data(self, text: str) -> str:
        """
        Redact sensitive data from text.
        
        Args:
            text: Text to redact
            
        Returns:
            str: Redacted text
        """
        if not text:
            return text
        
        # Check for sensitive patterns
        text_lower = text.lower()
        for pattern in self.REDACTION_PATTERNS:
            if pattern in text_lower:
                # Don't show the actual value
                return "[REDACTED - SENSITIVE DATA]"
        
        return text
    
    def _redact_dict(self, data: dict) -> dict:
        """
        Redact sensitive fields in dictionary.
        
        Args:
            data: Dictionary to redact
            
        Returns:
            dict: Dictionary with sensitive fields redacted
        """
        redacted = {}
        for key, value in data.items():
            if key.lower() in self.SENSITIVE_FIELDS:
                redacted[key] = "[REDACTED]"
            elif isinstance(value, dict):
                redacted[key] = self._redact_dict(value)
            elif isinstance(value, (list, tuple)):
                redacted[key] = [self._redact_dict(v) if isinstance(v, dict) else v for v in value]
            else:
                redacted[key] = value
        return redacted


class SecurityLogger:
    """Centralized security-focused logging."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure one logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger if not already initialized."""
        if not SecurityLogger._initialized:
            self._setup_logging()
            SecurityLogger._initialized = True
    
    def _setup_logging(self):
        """Set up logging configuration."""
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'logs'
        )
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure root logger
        self.logger = logging.getLogger('campus_resource_hub')
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(SensitiveDataFilter())
        
        # File handler for general logs
        file_handler = logging.FileHandler(
            os.path.join(log_dir, 'app.log')
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(SensitiveDataFilter())
        
        # File handler for security events
        security_handler = logging.FileHandler(
            os.path.join(log_dir, 'security.log')
        )
        security_handler.setLevel(logging.WARNING)
        security_formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        security_handler.setFormatter(security_formatter)
        security_handler.addFilter(SensitiveDataFilter())
        
        # Error handler
        error_handler = logging.FileHandler(
            os.path.join(log_dir, 'error.log')
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s\n%(exc_info)s'
        )
        error_handler.setFormatter(error_formatter)
        error_handler.addFilter(SensitiveDataFilter())
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(security_handler)
        self.logger.addHandler(error_handler)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], 
                          level: str = 'warning', user_id: Optional[int] = None):
        """
        Log security-related events.
        
        Args:
            event_type: Type of security event
            details: Event details (will be redacted if sensitive)
            level: Log level (info, warning, error)
            user_id: User ID associated with event (if applicable)
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details
        }
        
        message = f"Security Event: {event_type} - {json.dumps(log_data)}"
        
        if level == 'error':
            self.logger.error(message)
        elif level == 'warning':
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def log_authentication_attempt(self, email: str, success: bool, 
                                   reason: Optional[str] = None, ip_address: Optional[str] = None):
        """
        Log authentication attempts.
        
        Args:
            email: User email (will be partially redacted)
            success: Whether authentication succeeded
            reason: Reason for failure (if applicable)
            ip_address: IP address of request
        """
        # Partially redact email for privacy
        redacted_email = self._redact_email(email) if email else 'unknown'
        
        event_type = 'auth_success' if success else 'auth_failure'
        details = {
            'email': redacted_email,
            'ip_address': ip_address,
            'reason': reason
        }
        
        level = 'info' if success else 'warning'
        self.log_security_event(event_type, details, level=level)
    
    def log_authorization_failure(self, user_id: int, resource: str, 
                                 action: str, ip_address: Optional[str] = None):
        """
        Log authorization failures.
        
        Args:
            user_id: User ID
            resource: Resource being accessed
            action: Action being attempted
            ip_address: IP address of request
        """
        details = {
            'resource': resource,
            'action': action,
            'ip_address': ip_address
        }
        
        self.log_security_event('authz_failure', details, level='warning', user_id=user_id)
    
    def log_input_validation_failure(self, field: str, value_preview: str, 
                                    reason: str, user_id: Optional[int] = None):
        """
        Log input validation failures (potential attack attempts).
        
        Args:
            field: Field name that failed validation
            value_preview: Preview of invalid value (truncated)
            reason: Reason for validation failure
            user_id: User ID (if available)
        """
        # Truncate value preview to avoid logging large payloads
        if len(value_preview) > 100:
            value_preview = value_preview[:100] + '...[truncated]'
        
        details = {
            'field': field,
            'value_preview': value_preview,
            'reason': reason
        }
        
        self.log_security_event('input_validation_failure', details, level='warning', user_id=user_id)
    
    def log_exception(self, exception: Exception, context: Optional[Dict[str, Any]] = None,
                     user_id: Optional[int] = None):
        """
        Log exceptions with context.
        
        Args:
            exception: Exception to log
            context: Additional context (will be redacted if sensitive)
            user_id: User ID (if available)
        """
        error_details = {
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'traceback': traceback.format_exc(),
            'context': context or {},
            'user_id': user_id
        }
        
        self.logger.error(f"Exception occurred: {json.dumps(error_details)}")
    
    def log_rate_limit_exceeded(self, endpoint: str, ip_address: str):
        """
        Log rate limit violations.
        
        Args:
            endpoint: API endpoint
            ip_address: IP address that exceeded rate limit
        """
        details = {
            'endpoint': endpoint,
            'ip_address': ip_address
        }
        
        self.log_security_event('rate_limit_exceeded', details, level='warning')
    
    def log_data_access(self, user_id: int, resource_type: str, 
                       resource_id: int, action: str):
        """
        Log data access for audit trail.
        
        Args:
            user_id: User accessing data
            resource_type: Type of resource (e.g., 'booking', 'resource')
            resource_id: ID of resource
            action: Action performed (e.g., 'read', 'update', 'delete')
        """
        details = {
            'resource_type': resource_type,
            'resource_id': resource_id,
            'action': action
        }
        
        self.log_security_event('data_access', details, level='info', user_id=user_id)
    
    @staticmethod
    def _redact_email(email: str) -> str:
        """
        Partially redact email for privacy.
        
        Args:
            email: Email to redact
            
        Returns:
            str: Partially redacted email (e.g., u***r@example.com)
        """
        if '@' not in email:
            return '***'
        
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            redacted_local = '*' * len(local)
        else:
            redacted_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        return f"{redacted_local}@{domain}"
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)


# Global logger instance
logger = SecurityLogger()


def log_exceptions(func):
    """
    Decorator to automatically log exceptions.
    
    Usage:
        @log_exceptions
        def my_function():
            # function code
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.log_exception(e, context={'function': func.__name__})
            raise
    
    return wrapper


def get_client_ip(request) -> str:
    """
    Get client IP address from request, considering proxies.
    
    Args:
        request: Flask request object
        
    Returns:
        str: Client IP address
    """
    # Check for forwarded IP (behind proxy/load balancer)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr or 'unknown'
