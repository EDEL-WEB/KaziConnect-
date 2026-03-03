from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.payment_service import PaymentService
from app.utils.decorators import role_required

bp = Blueprint('payments', __name__, url_prefix='/api/payments')

@bp.route('/release/<job_id>', methods=['POST'])
@jwt_required()
@role_required('customer')
def release_payment(job_id):
    try:
        payment = PaymentService.release_payment(job_id)
        return jsonify({'message': 'Payment released', 'payment_id': payment.id}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to release payment'}), 500

@bp.route('/refund/<job_id>', methods=['POST'])
@jwt_required()
@role_required('admin', 'customer')
def refund_payment(job_id):
    try:
        payment = PaymentService.refund_payment(job_id)
        return jsonify({'message': 'Payment refunded', 'payment_id': payment.id}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to refund payment'}), 500

@bp.route('/wallet', methods=['GET'])
@jwt_required()
def get_wallet():
    try:
        user_id = get_jwt_identity()
        wallet = PaymentService.get_wallet_balance(user_id)
        
        return jsonify({
            'wallet_id': wallet.id,
            'balance': str(wallet.balance)
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get wallet'}), 500

@bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 50, type=int)
        transactions = PaymentService.get_transaction_history(user_id, limit)
        
        return jsonify({
            'transactions': [{
                'id': t.id,
                'type': t.type,
                'amount': str(t.amount),
                'description': t.description,
                'balance_after': str(t.balance_after),
                'created_at': t.created_at.isoformat()
            } for t in transactions]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get transactions'}), 500
