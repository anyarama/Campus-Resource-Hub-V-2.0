"""
Messages Routes
REST API endpoints for messaging system.
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from backend.services.message_service import MessageService
from backend.middleware.auth import login_required
from backend.extensions import limiter

# Create messages blueprint
messages_bp = Blueprint('messages', __name__)


@messages_bp.route('', methods=['GET'])
@login_required
def list_threads():
    """
    List all message threads for current user.
    
    GET /api/messages?page=1&per_page=20
    
    Requires: Authentication
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 50)
    
    Returns:
        200: List of threads with pagination
        401: Not authenticated
    """
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)
        
        # Get user's threads
        result = MessageService.get_user_threads(
            user_id=current_user.id,
            page=page,
            per_page=per_page
        )
        
        return jsonify(result), 200
    
    except ValueError:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid page or per_page value'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching threads'
        }), 500


@messages_bp.route('/thread/<thread_id>', methods=['GET'])
@login_required
def get_thread_messages(thread_id):
    """
    Get all messages in a thread.
    
    GET /api/messages/thread/:threadId?page=1&per_page=50
    
    Requires: Authentication (participant in thread)
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 50, max: 100)
    
    Returns:
        200: List of messages with pagination
        403: Access denied
        404: Thread not found
    """
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        
        # Get thread messages
        result, error = MessageService.get_thread_messages(
            thread_id=thread_id,
            user_id=current_user.id,
            page=page,
            per_page=per_page
        )
        
        if error:
            return jsonify({
                'error': 'Not Found',
                'message': error
            }), 404
        
        # Mark thread as read when viewing
        MessageService.mark_thread_as_read(thread_id, current_user.id)
        
        return jsonify(result), 200
    
    except ValueError:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid page or per_page value'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching messages'
        }), 500


@messages_bp.route('', methods=['POST'])
@login_required
@limiter.limit("30 per hour")
def send_message():
    """
    Send a new message.
    
    POST /api/messages
    
    Requires: Authentication
    
    Request Body:
        {
            "receiver_id": 2,
            "content": "Hello, is this resource available?",
            "thread_id": "thread_1_2_resource_5" (optional),
            "booking_id": 10 (optional),
            "resource_id": 5 (optional)
        }
    
    Returns:
        201: Message sent
        400: Validation error
        401: Not authenticated
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body is required'
            }), 400
        
        # Validate required fields
        receiver_id = data.get('receiver_id')
        content = data.get('content')
        
        if not receiver_id:
            return jsonify({
                'error': 'Validation Error',
                'message': 'receiver_id is required'
            }), 400
        
        if not content:
            return jsonify({
                'error': 'Validation Error',
                'message': 'content is required'
            }), 400
        
        # Optional fields
        thread_id = data.get('thread_id')
        booking_id = data.get('booking_id')
        resource_id = data.get('resource_id')
        
        # Send message
        message, error = MessageService.send_message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            content=content,
            thread_id=thread_id,
            booking_id=booking_id,
            resource_id=resource_id
        )
        
        if error:
            return jsonify({
                'error': 'Validation Error',
                'message': error
            }), 400
        
        return jsonify({
            'message': 'Message sent successfully',
            'data': message.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while sending the message'
        }), 500


@messages_bp.route('/<int:message_id>/read', methods=['PUT', 'PATCH'])
@login_required
def mark_as_read(message_id):
    """
    Mark a message as read.
    
    PUT/PATCH /api/messages/:id/read
    
    Requires: Authentication (must be receiver)
    
    Returns:
        200: Message marked as read
        403: Not authorized
        404: Message not found
    """
    try:
        message, error = MessageService.mark_message_as_read(
            message_id=message_id,
            user_id=current_user.id
        )
        
        if error:
            return jsonify({
                'error': 'Not Found',
                'message': error
            }), 404
        
        return jsonify({
            'message': 'Message marked as read',
            'data': message.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while marking message as read'
        }), 500


@messages_bp.route('/unread-count', methods=['GET'])
@login_required
def get_unread_count():
    """
    Get count of unread messages for current user.
    
    GET /api/messages/unread-count
    
    Requires: Authentication
    
    Returns:
        200: Unread message count
        401: Not authenticated
    """
    try:
        count = MessageService.get_unread_count(current_user.id)
        
        return jsonify({
            'unread_count': count
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching unread count'
        }), 500


@messages_bp.route('/search', methods=['GET'])
@login_required
def search_messages():
    """
    Search messages by content.
    
    GET /api/messages/search?q=resource&limit=50
    
    Requires: Authentication
    
    Query Parameters:
        q: Search term (required, min 2 characters)
        limit: Max results (default: 50, max: 100)
    
    Returns:
        200: Search results
        400: Missing or invalid search term
        401: Not authenticated
    """
    try:
        search_term = request.args.get('q', '').strip()
        
        if not search_term:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Search term (q) is required'
            }), 400
        
        limit = min(int(request.args.get('limit', 50)), 100)
        
        messages, error = MessageService.search_messages(
            user_id=current_user.id,
            search_term=search_term,
            limit=limit
        )
        
        if error:
            return jsonify({
                'error': 'Validation Error',
                'message': error
            }), 400
        
        return jsonify({
            'query': search_term,
            'count': len(messages),
            'messages': messages
        }), 200
    
    except ValueError:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid limit value'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while searching messages'
        }), 500
