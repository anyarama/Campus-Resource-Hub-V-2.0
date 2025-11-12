"""
Health Check Blueprint
Provides health check endpoints for monitoring and testing.
"""

from flask import Blueprint, jsonify
from datetime import datetime

health_bp = Blueprint('health', __name__)


@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint - returns API status.
    
    Returns:
        JSON response with status and timestamp
    """
    return jsonify({
        'status': 'ok',
        'message': 'Campus Resource Hub API is running',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': '1.0.0'
    }), 200


@health_bp.route('/api/health/db', methods=['GET'])
def database_health():
    """
    Database health check endpoint.
    
    Returns:
        JSON response with database connection status
    """
    try:
        from backend.extensions import db
        # Try to execute a simple query
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'ok',
            'message': 'Database connection is healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Database connection failed: {str(e)}',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 503
