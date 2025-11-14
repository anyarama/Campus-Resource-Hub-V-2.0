"""
Reviews Routes
REST API endpoints for review and rating system.
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from services.review_service import ReviewService
from middleware.auth import login_required
from extensions import limiter

# Create reviews blueprint
reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/resources/<int:resource_id>/reviews', methods=['GET'])
def get_resource_reviews(resource_id):
    """
    Get all reviews for a resource.
    
    GET /api/reviews/resources/:id/reviews?page=1&per_page=20
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 50)
    
    Returns:
        200: List of reviews with average rating
        400: Invalid parameters
    """
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)
        
        # Get reviews
        result = ReviewService.get_resource_reviews(
            resource_id=resource_id,
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
            'message': 'An error occurred while fetching reviews'
        }), 500


@reviews_bp.route('', methods=['POST'])
@login_required
@limiter.limit("5 per hour")
def create_review():
    """
    Submit a new review for a resource.
    
    POST /api/reviews
    
    Requires: Authentication
    
    Request Body:
        {
            "resource_id": 5,
            "rating": 5,
            "comment": "Great study room, very quiet!",
            "booking_id": 10 (optional)
        }
    
    Returns:
        201: Review created
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
        rating = data.get('rating')
        
        if not resource_id:
            return jsonify({
                'error': 'Validation Error',
                'message': 'resource_id is required'
            }), 400
        
        if rating is None:
            return jsonify({
                'error': 'Validation Error',
                'message': 'rating is required'
            }), 400
        
        # Optional fields
        comment = data.get('comment')
        booking_id = data.get('booking_id')
        
        # Create review
        review, error = ReviewService.create_review(
            resource_id=resource_id,
            reviewer_id=current_user.id,
            rating=rating,
            comment=comment,
            booking_id=booking_id
        )
        
        if error:
            return jsonify({
                'error': 'Validation Error',
                'message': error
            }), 400
        
        return jsonify({
            'message': 'Review submitted successfully',
            'review': review.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while creating the review'
        }), 500


@reviews_bp.route('/<int:review_id>', methods=['PUT', 'PATCH'])
@login_required
def update_review(review_id):
    """
    Update an existing review.
    
    PUT/PATCH /api/reviews/:id
    
    Requires: Authentication (must be reviewer)
    
    Request Body:
        {
            "rating": 4,
            "comment": "Updated review comment"
        }
    
    Returns:
        200: Review updated
        400: Validation error
        403: Not authorized
        404: Review not found
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body is required'
            }), 400
        
        # Get optional fields
        rating = data.get('rating')
        comment = data.get('comment')
        
        # Update review
        review, error = ReviewService.update_review(
            review_id=review_id,
            user_id=current_user.id,
            rating=rating,
            comment=comment
        )
        
        if error:
            if 'not found' in error.lower():
                return jsonify({
                    'error': 'Not Found',
                    'message': error
                }), 404
            elif 'permission' in error.lower() or 'only edit your own' in error.lower():
                return jsonify({
                    'error': 'Forbidden',
                    'message': error
                }), 403
            else:
                return jsonify({
                    'error': 'Validation Error',
                    'message': error
                }), 400
        
        return jsonify({
            'message': 'Review updated successfully',
            'review': review.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while updating the review'
        }), 500


@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(review_id):
    """
    Delete a review.
    
    DELETE /api/reviews/:id
    
    Requires: Authentication (reviewer or admin)
    
    Returns:
        200: Review deleted
        403: Not authorized
        404: Review not found
    """
    try:
        success, error = ReviewService.delete_review(
            review_id=review_id,
            user=current_user
        )
        
        if not success:
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
            'message': 'Review deleted successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while deleting the review'
        }), 500


@reviews_bp.route('/<int:review_id>/flag', methods=['POST'])
@login_required
def flag_review(review_id):
    """
    Flag a review as inappropriate.
    
    POST /api/reviews/:id/flag
    
    Requires: Authentication
    
    Returns:
        200: Review flagged
        400: Validation error
        404: Review not found
    """
    try:
        review, error = ReviewService.flag_review(
            review_id=review_id,
            user_id=current_user.id
        )
        
        if error:
            if 'not found' in error.lower():
                return jsonify({
                    'error': 'Not Found',
                    'message': error
                }), 404
            else:
                return jsonify({
                    'error': 'Validation Error',
                    'message': error
                }), 400
        
        return jsonify({
            'message': 'Review flagged successfully',
            'review': review.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An error occurred while flagging the review'
        }), 500


@reviews_bp.route('/my-reviews', methods=['GET'])
@login_required
def get_my_reviews():
    """
    Get current user's reviews.
    
    GET /api/reviews/my-reviews?page=1&per_page=20
    
    Requires: Authentication
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 50)
    
    Returns:
        200: List of user's reviews
        401: Not authenticated
    """
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)
        
        # Get user's reviews
        result = ReviewService.get_user_reviews(
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
            'message': 'An error occurred while fetching your reviews'
        }), 500
