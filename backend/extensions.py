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

# Initialize extensions
# These will be configured in the app factory (app.py)

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
cors = CORS()


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
