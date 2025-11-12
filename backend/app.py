"""
Flask Application Factory
Creates and configures the Flask application instance.
Uses the factory pattern for better testing and modularity.
"""

import os
from flask import Flask, jsonify
from backend.config import get_config
from backend.extensions import init_extensions


def create_app(config_name=None):
    """
    Application factory for creating Flask app instances.
    
    Args:
        config_name (str): Configuration environment name
                          ('development', 'testing', 'production')
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Create Flask app instance
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Initialize Flask extensions
    init_extensions(app)
    
    # Import models to ensure they're registered with SQLAlchemy
    # This must happen after extensions are initialized
    from backend import models
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app


def register_blueprints(app):
    """
    Register Flask blueprints for modular routing.
    
    Args:
        app: Flask application instance
    """
    # Import blueprints here to avoid circular imports
    from backend.routes.health import health_bp
    from backend.routes.auth import auth_bp
    from backend.routes.resources import resources_bp
    from backend.routes.bookings import bookings_bp
    from backend.routes.messages import messages_bp
    from backend.routes.reviews import reviews_bp
    from backend.routes.admin import admin_bp
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(resources_bp, url_prefix='/api/resources')
    app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')


def register_error_handlers(app):
    """
    Register error handlers for common HTTP errors.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found on this server.',
            'status': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        # Rollback database session on error
        from backend.extensions import db
        db.session.rollback()
        
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An internal server error occurred. Please try again later.',
            'status': 500
        }), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden errors."""
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource.',
            'status': 403
        }), 403
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """Handle 401 Unauthorized errors."""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource.',
            'status': 401
        }), 401
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors."""
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request could not be understood or was missing required parameters.',
            'status': 400
        }), 400


# CLI commands for Flask
def register_cli_commands(app):
    """
    Register custom CLI commands for the application.
    
    Args:
        app: Flask application instance
    """
    
    @app.cli.command('init-db')
    def init_db():
        """Initialize the database with tables."""
        from backend.extensions import db
        db.create_all()
        print('✓ Database initialized')
    
    @app.cli.command('seed-db')
    def seed_db():
        """Seed the database with sample data for development."""
        from backend.extensions import db
        # TODO: Implement seeding logic
        print('✓ Database seeded with sample data')


# Create app instance for CLI and development
app = create_app()

# Register CLI commands
register_cli_commands(app)


if __name__ == '__main__':
    # Run the development server
    app.run(
        host=os.environ.get('FLASK_RUN_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_RUN_PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )
