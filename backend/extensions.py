"""
Flask Extensions Module
Initializes Flask extensions for use throughout the application.
Extensions are created here and initialized in the app factory.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

# Initialize extensions
# These will be configured in the app factory (app.py)

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
cors = CORS()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",  # Use memory for development, Redis for production
    strategy="fixed-window"
)


def init_extensions(app):
    """
    Initialize Flask extensions with the app instance.
    
    Args:
        app: Flask application instance
    """
    # Database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Authentication
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Password hashing
    bcrypt.init_app(app)
    
    # CORS - Allow React frontend to make requests
    cors.init_app(
        app,
        origins=app.config.get('CORS_ORIGINS', ['http://localhost:5173']),
        supports_credentials=app.config.get('CORS_SUPPORTS_CREDENTIALS', True),
        allow_headers=['Content-Type', 'Authorization', 'X-CSRF-Token'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
    )
    
    # CSRF Protection - Enable for all state-changing requests
    csrf.init_app(app)
    
    # Rate Limiting - Protect against abuse
    limiter.init_app(app)
    
    # Security Headers - Protect against common web vulnerabilities
    # Configure Talisman with appropriate settings
    csp = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'"],  # Allow inline scripts for React
        'style-src': ["'self'", "'unsafe-inline'"],   # Allow inline styles
        'img-src': ["'self'", 'data:', 'https:'],     # Allow images from data URIs and HTTPS
        'font-src': ["'self'", 'data:'],
        'connect-src': ["'self'", 'http://localhost:5173', 'ws://localhost:5173'],  # Allow frontend connections
    }
    
    Talisman(
        app,
        force_https=app.config.get('TALISMAN_FORCE_HTTPS', False),  # Disable in development
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,  # 1 year
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src'],
        frame_options='SAMEORIGIN',
        referrer_policy='strict-origin-when-cross-origin',
        feature_policy={
            'geolocation': "'none'",
            'microphone': "'none'",
            'camera': "'none'",
        }
    )


@login_manager.user_loader
def load_user(user_id):
    """
    User loader callback for Flask-Login.
    Loads a user from the database by ID.
    
    Args:
        user_id (int): User ID from session
    
    Returns:
        User: User object or None
    """
    # Import here to avoid circular imports
    from backend.models.user import User
    return User.query.get(int(user_id))
