from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.notification_service import NotificationService

bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@bp.route('/heartbeat', methods=['POST'])
@jwt_required()
def heartbeat():
    """
    Mobile app sends heartbeat every 30 seconds to indicate online status
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        presence = NotificationService.update_presence(
            user_id=user_id,
            is_online=True,
            device_id=data.get('device_id'),
            device_type=data.get('device_type'),
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'status': 'online',
            'last_seen': presence.last_seen.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/offline', methods=['POST'])
@jwt_required()
def go_offline():
    """Mark user as offline"""
    try:
        user_id = get_jwt_identity()
        
        NotificationService.update_presence(user_id, is_online=False)
        
        return jsonify({'status': 'offline'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/pending', methods=['GET'])
@jwt_required()
def get_pending():
    """Get all pending notifications for current user"""
    try:
        user_id = get_jwt_identity()
        
        notifications = NotificationService.get_pending_notifications(user_id)
        
        return jsonify({
            'notifications': [{
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'type': n.type,
                'priority': n.priority,
                'job_id': n.job_id,
                'created_at': n.created_at.isoformat()
            } for n in notifications]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<notification_id>/mark-read', methods=['POST'])
@jwt_required()
def mark_read(notification_id):
    """Mark notification as read/delivered"""
    try:
        from app.models import Notification
        from datetime import datetime
        
        notification = Notification.query.get_or_404(notification_id)
        notification.status = 'delivered'
        notification.delivered_at = datetime.utcnow()
        
        from app import db
        db.session.commit()
        
        return jsonify({'message': 'Notification marked as read'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/status/<user_id>', methods=['GET'])
@jwt_required()
def check_user_status(user_id):
    """Check if another user is online"""
    try:
        is_online = NotificationService.is_user_online(user_id)
        
        from app.models import UserPresence
        presence = UserPresence.query.filter_by(user_id=user_id).first()
        
        return jsonify({
            'user_id': user_id,
            'is_online': is_online,
            'last_seen': presence.last_seen.isoformat() if presence else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
