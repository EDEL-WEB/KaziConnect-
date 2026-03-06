from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.job_update_service import JobUpdateService
from app.services.notification_service import NotificationService
from app.models import Job, Worker

bp = Blueprint('job_updates', __name__, url_prefix='/api/jobs')

@bp.route('/<job_id>/progress', methods=['PATCH'])
@jwt_required()
def update_progress(job_id):
    """
    Worker updates job progress (0-100%)
    Notifies customer if online, SMS if offline
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        update = JobUpdateService.update_progress(
            job_id=job_id,
            user_id=user_id,
            progress_percentage=data['progress_percentage'],
            note=data.get('note')
        )
        
        # Notify customer
        job = Job.query.get(job_id)
        message = f"Job '{job.title}' is {data['progress_percentage']}% complete"
        NotificationService.send_notification(
            job.customer_id,
            message,
            title="Job Progress Update",
            job_id=job_id
        )
        
        return jsonify({
            'message': 'Progress updated',
            'update_id': update.id,
            'progress': update.progress_percentage
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<job_id>/notes', methods=['POST'])
@jwt_required()
def add_note(job_id):
    """
    Add note to job (worker or customer)
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        update = JobUpdateService.add_note(
            job_id=job_id,
            user_id=user_id,
            note=data['note']
        )
        
        return jsonify({
            'message': 'Note added',
            'update_id': update.id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<job_id>/photos', methods=['POST'])
@jwt_required()
def upload_photos(job_id):
    """
    Upload proof photos (before/after, progress)
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        update = JobUpdateService.upload_photos(
            job_id=job_id,
            user_id=user_id,
            photo_urls=data['photo_urls'],
            note=data.get('note')
        )
        
        # Notify other party
        job = Job.query.get(job_id)
        worker = Worker.query.filter_by(user_id=user_id).first()
        
        if worker:
            # Worker uploaded, notify customer
            message = f"Worker uploaded photos for job: {job.title}"
            NotificationService.send_notification(
                job.customer_id,
                message,
                title="New Photos",
                job_id=job_id
            )
        else:
            # Customer uploaded, notify worker
            message = f"Customer uploaded photos for job: {job.title}"
            NotificationService.send_notification(
                job.worker.user_id,
                message,
                title="New Photos",
                job_id=job_id
            )
        
        return jsonify({
            'message': 'Photos uploaded',
            'update_id': update.id,
            'photo_count': len(data['photo_urls'])
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<job_id>/updates', methods=['GET'])
@jwt_required()
def get_updates(job_id):
    """
    Get all updates for a job (timeline)
    """
    try:
        updates = JobUpdateService.get_job_updates(job_id)
        
        return jsonify({
            'updates': [{
                'id': u.id,
                'type': u.update_type,
                'progress_percentage': u.progress_percentage,
                'note': u.note,
                'photo_urls': u.photo_urls,
                'created_at': u.created_at.isoformat(),
                'created_offline': u.created_offline
            } for u in updates]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<job_id>/timeline', methods=['GET'])
@jwt_required()
def get_timeline(job_id):
    """
    Get complete job timeline with all events
    """
    try:
        timeline = JobUpdateService.get_job_timeline(job_id)
        
        return jsonify({'timeline': timeline}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
