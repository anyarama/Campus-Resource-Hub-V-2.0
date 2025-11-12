"""
Flask Configuration Module
Handles environment-specific settings for development, testing, and production.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration with defaults shared across all environments."""
    
    # Flask Core Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_APP = os.environ.get('FLASK_APP') or 'backend.app'
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Security
    # Enable CSRF protection for all requests
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour CSRF token lifetime
    WTF_CSRF_CHECK_DEFAULT = True  # Check CSRF on all POST/PUT/DELETE
    WTF_CSRF_METHODS = ['POST', 'PUT', 'DELETE', 'PATCH']
    WTF_CSRF_HEADERS = ['X-CSRFToken', 'X-CSRF-Token']  # Accept CSRF token in headers
    
    # Security Headers (Talisman) Settings
    TALISMAN_FORCE_HTTPS = False  # Set to True in production
    
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    
    # File Uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # CORS Settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
    CORS_SUPPORTS_CREDENTIALS = True
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # AI Features (optional)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG = True
    TESTING = False
    
    # SQLite for local development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dev.db')
    
    SQLALCHEMY_ECHO = True  # Log SQL queries in dev mode
    
    # Less strict security for dev
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing environment configuration."""
    
    DEBUG = False
    TESTING = True
    
    # In-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Speed up password hashing for tests
    BCRYPT_LOG_ROUNDS = 4


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG = False
    TESTING = False
    
    # PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        # Heroku uses postgres://, but SQLAlchemy requires postgresql://
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    # Strict security in production
    TALISMAN_FORCE_HTTPS = True  # Enforce HTTPS in production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    def __init__(self):
        """Validate production configuration on initialization."""
        super().__init__()
        
        # Enhanced production validation
        self._validate_production_secrets()
    
    def _validate_production_secrets(self):
        """Validate critical production secrets and configuration."""
        errors = []
        
        # Validate SECRET_KEY
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            errors.append("SECRET_KEY environment variable must be set in production")
        elif len(secret_key) < 64:
            errors.append(
                f"SECRET_KEY is too short for production (minimum 64 characters, got {len(secret_key)}). "
                f"Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        
        # Check for weak secret patterns
        if secret_key:
            weak_patterns = ['dev', 'test', 'demo', 'example', 'changeme', 'default']
            secret_lower = secret_key.lower()
            for pattern in weak_patterns:
                if pattern in secret_lower:
                    errors.append(
                        f"SECRET_KEY contains weak pattern '{pattern}'. "
                        f"Use a cryptographically random key for production."
                    )
        
        # Validate DATABASE_URL
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            errors.append("DATABASE_URL environment variable must be set in production")
        elif database_url.startswith('sqlite'):
            errors.append(
                "SQLite is not recommended for production. "
                "Use PostgreSQL, MySQL, or another production-grade database."
            )
        
        # Validate CORS_ORIGINS
        cors_origins = os.environ.get('CORS_ORIGINS', self.CORS_ORIGINS)
        if isinstance(cors_origins, str):
            origins = cors_origins.split(',')
        else:
            origins = cors_origins
        
        for origin in origins:
            origin = origin.strip()
            if 'localhost' in origin or '127.0.0.1' in origin:
                errors.append(
                    f"Production CORS_ORIGINS should not include localhost: {origin}"
                )
            if origin.startswith('http://') and 'localhost' not in origin:
                errors.append(
                    f"Production CORS_ORIGINS should use HTTPS: {origin}"
                )
        
        # Raise error if any validation failed
        if errors:
            error_message = "\n❌ PRODUCTION CONFIGURATION ERRORS:\n" + "\n".join(
                f"  - {error}" for error in errors
            )
            error_message += "\n\nPlease fix these issues before deploying to production."
            raise ValueError(error_message)


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """
    Get configuration object based on environment.
    
    Args:
        env (str): Environment name ('development', 'testing', 'production')
    
    Returns:
        Config: Configuration object for the specified environment
    """
    env = env or os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
