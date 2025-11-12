"""
Bookings Routes
REST API endpoints for booking management.
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from datetime import datetime
from backend.services.booking_service import BookingService
from backend.middleware.auth import login_required
from backend.extensions import limiter

# Create bookings blueprint
bookings_bp = Blueprint('bookings', __name__)


@bookings_bp.route('', methods=['POST'])
@login_required
@limiter.limit("10 per hour")
def create_booking():
    """
    Create a new booking.
    
    POST /api/bookings
    
    Requires: Authentication
    
    Request Body:
        {
            "resource_id": 1,
            "start_datetime": "2025-01-15T10:00:00Z",
            "end_datetime": "2025-01-15T12:00:00Z",
            "notes": "Optional booking notes"
        }
    
    Returns:
        201: Booking created
        400: Validation error
        401: Not authenticated
        409: Conflict with existing booking
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body is required'
            }), 400
        
        # Validate required fields
        resource_id = data.get('resource_id')
        start_datetime_str = data.get('start_datetime')
        end_datetime_str = data.get('end_datetime')
        notes = data.get('notes')
        
        if not resource_id:
            return jsonify({
                'error': 'Validation Error',
                'message': 'resource_id is required'
            }), 400
        
        if not start_datetime_str:
            return jsonify({
                'error': 'Validation Error',
                'message': 'start_datetime is required'
            }), 400
        
        if not end_datetime_str:
            return jsonify({
                'error': 'Validation Error',
                'message': 'end_datetime is required'
            }), 400
        
        # Parse datetime strings
        try:
            start_datetime = datetime.fromisoformat(start_datetime_str.replace('Z', '+00:00'))
            end_datetime = datetime.fromisoformat(end_datetime_str.replace('Z', '+00:00'))
        except ValueError as e:
            return jsonify({
                'error': 'Validation Error',
                'message': 'Invalid datetime format. Use ISO 8601 format (e.g., 2025-01-15T10:00:00Z)'
            }), 400
        
        # Create booking
        booking, error = BookingService.create_booking(
            requester_id=current_user.id,
            resource_id=resource_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            notes=notes
        )
        
        if error:
            if 'conflict' in error.lower():
                return jsonify({
                    'error': 'Conflict',
                    'message': error
                }), 409
            else:
                return jsonify({
                    'error': 'Validation Error',
                    'message': error
                }), 400
        
        return jsonify({
            'message': 'Booking created successfully',
            'booking': booking.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while creating the booking'
        }), 500


@bookings_bp.route('', methods=['GET'])
@login_required
def list_bookings():
    """
    List current user's bookings with filtering and pagination.
    
    GET /api/bookings?status=pending&page=1&per_page=20
    
    Requires: Authentication
    
    Query Parameters:
        status: Filter by status ('pending', 'approved', 'rejected', 'cancelled', 'completed')
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
    
    Returns:
        200: List of bookings with pagination
        401: Not authenticated
    """
    try:
        # Get query parameters
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Validate status if provided
        if status and status not in BookingService.VALID_STATUSES:
            return jsonify({
                'error': 'Validation Error',
                'message': f'Invalid status. Must be one of: {", ".join(BookingService.VALID_STATUSES)}'
            }), 400
        
        # Get user's bookings
        result = BookingService.list_user_bookings(
            user_id=current_user.id,
            status=status,
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
            'message': 'An error occurred while fetching bookings'
        }), 500


@bookings_bp.route('/<int:booking_id>', methods=['GET'])
@login_required
def get_booking(booking_id):
    """
    Get a specific booking by ID.
    
    GET /api/bookings/:id
    
    Requires: Authentication (requester, resource owner, or admin)
    
    Returns:
        200: Booking details
        403: Access denied
        404: Booking not found
    """
    try:
        booking = BookingService.get_booking(booking_id)
        
        if not booking:
            return jsonify({
                'error': 'Not Found',
                'message': 'Booking not found'
            }), 404
        
        # Check if user can view this booking
        if not BookingService.can_user_view(booking, current_user):
            return jsonify({
                'error': 'Forbidden',
                'message': 'You do not have permission to view this booking'
            }), 403
        
        return jsonify(booking.to_dict()), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching the booking'
        }), 500


@bookings_bp.route('/<int:booking_id>/approve', methods=['POST'])
@login_required
def approve_booking(booking_id):
    """
    Approve a pending booking.
    
    POST /api/bookings/:id/approve
    
    Requires: Authentication (resource owner, staff, or admin)
    
    Request Body (optional):
        {
            "approval_notes": "Approved for use"
        }
    
    Returns:
        200: Booking approved
        400: Invalid status or conflict
        403: Not authorized
        404: Booking not found
    """
    try:
        data = request.get_json() or {}
        approval_notes = data.get('approval_notes')
        
        # Approve booking
        booking, error = BookingService.approve_booking(
            booking_id=booking_id,
            approver=current_user,
            approval_notes=approval_notes
        )
        
        if error:
            if 'not found' in error.lower():
                return jsonify({
                    'error': 'Not Found',
                    'message': error
                }), 404
            elif 'permission' in error.lower():
                return jsonify({
                    'error': 'Forbidden',
                    'message': error
                }), 403
            elif 'conflict' in error.lower():
                return jsonify({
                    'error': 'Conflict',
                    'message': error
                }), 409
            else:
                return jsonify({
                    'error': 'Bad Request',
                    'message': error
                }), 400
        
        return jsonify({
            'message': 'Booking approved successfully',
            'booking': booking.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while approving the booking'
        }), 500


@bookings_bp.route('/<int:booking_id>/reject', methods=['POST'])
@login_required
def reject_booking(booking_id):
    """
    Reject a pending booking.
    
    POST /api/bookings/:id/reject
    
    Requires: Authentication (resource owner, staff, or admin)
    
    Request Body:
        {
            "rejection_reason": "Resource not available at this time"
        }
    
    Returns:
        200: Booking rejected
        400: Invalid status or missing reason
        403: Not authorized
        404: Booking not found
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body is required'
            }), 400
        
        rejection_reason = data.get('rejection_reason')
        
        if not rejection_reason:
            return jsonify({
                'error': 'Validation Error',
                'message': 'rejection_reason is required'
            }), 400
        
        # Reject booking
        booking, error = BookingService.reject_booking(
            booking_id=booking_id,
            approver=current_user,
            rejection_reason=rejection_reason
        )
        
        if error:
            if 'not found' in error.lower():
                return jsonify({
                    'error': 'Not Found',
                    'message': error
                }), 404
            elif 'permission' in error.lower():
                return jsonify({
                    'error': 'Forbidden',
                    'message': error
                }), 403
            else:
                return jsonify({
                    'error': 'Bad Request',
                    'message': error
                }), 400
        
        return jsonify({
            'message': 'Booking rejected successfully',
            'booking': booking.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while rejecting the booking'
        }), 500


@bookings_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """
    Cancel a booking.
    
    POST /api/bookings/:id/cancel
    
    Requires: Authentication (requester, resource owner, or admin)
    
    Request Body (optional):
        {
            "cancellation_reason": "No longer needed"
        }
    
    Returns:
        200: Booking cancelled
        400: Invalid status
        403: Not authorized
        404: Booking not found
    """
    try:
        data = request.get_json() or {}
        cancellation_reason = data.get('cancellation_reason')
        
        # Cancel booking
        booking, error = BookingService.cancel_booking(
            booking_id=booking_id,
            user=current_user,
            cancellation_reason=cancellation_reason
        )
        
        if error:
            if 'not found' in error.lower():
                return jsonify({
                    'error': 'Not Found',
                    'message': error
                }), 404
            elif 'permission' in error.lower():
                return jsonify({
                    'error': 'Forbidden',
                    'message': error
                }), 403
            else:
                return jsonify({
                    'error': 'Bad Request',
                    'message': error
                }), 400
        
        return jsonify({
            'message': 'Booking cancelled successfully',
            'booking': booking.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while cancelling the booking'
        }), 500


@bookings_bp.route('/pending', methods=['GET'])
@login_required
def get_pending_approvals():
    """
    Get pending bookings that require approval.
    
    GET /api/bookings/pending
    
    Requires: Authentication (resource owner, staff, or admin)
    
    Returns:
        200: List of pending bookings
        401: Not authenticated
    """
    try:
        # Get pending bookings that need approval
        bookings = BookingService.get_pending_approvals(current_user)
        
        return jsonify({
            'count': len(bookings),
            'bookings': bookings
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching pending approvals'
        }), 500


@bookings_bp.route('/check-availability', methods=['POST'])
@login_required
def check_availability():
    """
    Check if a resource is available for a time slot.
    
    POST /api/bookings/check-availability
    
    Requires: Authentication
    
    Request Body:
        {
            "resource_id": 1,
            "start_datetime": "2025-01-15T10:00:00Z",
            "end_datetime": "2025-01-15T12:00:00Z"
        }
    
    Returns:
        200: Availability status
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
        resource_id = data.get('resource_id')
        start_datetime_str = data.get('start_datetime')
        end_datetime_str = data.get('end_datetime')
        
        if not resource_id:
            return jsonify({
                'error': 'Validation Error',
                'message': 'resource_id is required'
            }), 400
        
        if not start_datetime_str:
            return jsonify({
                'error': 'Validation Error',
                'message': 'start_datetime is required'
            }), 400
        
        if not end_datetime_str:
            return jsonify({
                'error': 'Validation Error',
                'message': 'end_datetime is required'
            }), 400
        
        # Parse datetime strings
        try:
            start_datetime = datetime.fromisoformat(start_datetime_str.replace('Z', '+00:00'))
            end_datetime = datetime.fromisoformat(end_datetime_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'error': 'Validation Error',
                'message': 'Invalid datetime format. Use ISO 8601 format (e.g., 2025-01-15T10:00:00Z)'
            }), 400
        
        # Check availability
        is_available, message = BookingService.check_availability(
            resource_id=resource_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime
        )
        
        return jsonify({
            'available': is_available,
            'message': message,
            'resource_id': resource_id,
            'start_datetime': start_datetime_str,
            'end_datetime': end_datetime_str
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while checking availability'
        }), 500
