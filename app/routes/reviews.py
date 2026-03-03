from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.review_service import ReviewService
from app.utils.decorators import role_required
from app.utils.validators import validate_rating

bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')

@bp.route('', methods=['POST'])
@jwt_required()
@role_required('customer')
def create_review():
    try:
        customer_id = get_jwt_identity()
        data = request.get_json()
        
        if not validate_rating(data.get('rating')):
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        review = ReviewService.create_review(
            job_id=data['job_id'],
            customer_id=customer_id,
            rating=data['rating'],
            comment=data.get('comment')
        )
        
        return jsonify({'message': 'Review created', 'review_id': review.id}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to create review'}), 500

@bp.route('/worker/<worker_id>', methods=['GET'])
def get_worker_reviews(worker_id):
    try:
        limit = request.args.get('limit', 20, type=int)
        reviews = ReviewService.get_worker_reviews(worker_id, limit)
        
        return jsonify({
            'reviews': [{
                'id': r.id,
                'rating': r.rating,
                'comment': r.comment,
                'created_at': r.created_at.isoformat()
            } for r in reviews]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get reviews'}), 500
