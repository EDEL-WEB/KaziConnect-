from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.offline_sync_service import OfflineSyncService
from datetime import datetime

bp = Blueprint('sync', __name__, url_prefix='/api/sync')

@bp.route('/queue', methods=['POST'])
@jwt_required()
def queue_action():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        sync_id = OfflineSyncService.queue_offline_action(
            user_id=user_id,
            device_id=data['device_id'],
            action_type=data['action_type'],
            payload=data['payload'],
            client_timestamp=datetime.fromisoformat(data['client_timestamp'])
        )
        
        return jsonify({'sync_id': sync_id, 'status': 'queued'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/batch', methods=['POST'])
@jwt_required()
def batch_sync():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        actions = data.get('actions', [])
        
        queued_ids = []
        for action in actions:
            sync_id = OfflineSyncService.queue_offline_action(
                user_id=user_id,
                device_id=action['device_id'],
                action_type=action['action_type'],
                payload=action['payload'],
                client_timestamp=datetime.fromisoformat(action['client_timestamp'])
            )
            queued_ids.append(sync_id)
        
        results = OfflineSyncService.process_sync_queue(user_id)
        
        return jsonify({'queued': len(queued_ids), 'processed': len(results), 'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/status', methods=['GET'])
@jwt_required()
def sync_status():
    try:
        user_id = get_jwt_identity()
        pending_count = OfflineSyncService.get_pending_count(user_id)
        return jsonify({'pending_count': pending_count, 'status': 'ok'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
