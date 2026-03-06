from app import db
from app.models.job_update import JobUpdate
from app.models import Job
from datetime import datetime

class JobUpdateService:
    
    @staticmethod
    def update_progress(job_id, user_id, progress_percentage, note=None):
        """Update job progress percentage"""
        job = Job.query.get_or_404(job_id)
        
        if progress_percentage < 0 or progress_percentage > 100:
            raise ValueError('Progress must be between 0 and 100')
        
        update = JobUpdate(
            job_id=job_id,
            user_id=user_id,
            update_type='progress',
            progress_percentage=progress_percentage,
            note=note
        )
        
        db.session.add(update)
        db.session.commit()
        
        return update
    
    @staticmethod
    def add_note(job_id, user_id, note):
        """Add text note to job"""
        update = JobUpdate(
            job_id=job_id,
            user_id=user_id,
            update_type='note',
            note=note
        )
        
        db.session.add(update)
        db.session.commit()
        
        return update
    
    @staticmethod
    def upload_photos(job_id, user_id, photo_urls, note=None):
        """Upload proof photos"""
        update = JobUpdate(
            job_id=job_id,
            user_id=user_id,
            update_type='photo',
            photo_urls=photo_urls,
            note=note
        )
        
        db.session.add(update)
        db.session.commit()
        
        return update
    
    @staticmethod
    def record_status_change(job_id, user_id, old_status, new_status):
        """Record job status change"""
        update = JobUpdate(
            job_id=job_id,
            user_id=user_id,
            update_type='status_change',
            old_status=old_status,
            new_status=new_status
        )
        
        db.session.add(update)
        db.session.commit()
        
        return update
    
    @staticmethod
    def get_job_updates(job_id):
        """Get all updates for a job"""
        return JobUpdate.query.filter_by(job_id=job_id).order_by(JobUpdate.created_at).all()
    
    @staticmethod
    def get_job_timeline(job_id):
        """Get complete job timeline with all events"""
        job = Job.query.get_or_404(job_id)
        updates = JobUpdate.query.filter_by(job_id=job_id).order_by(JobUpdate.created_at).all()
        
        timeline = []
        
        # Job created
        timeline.append({
            'event': 'job_created',
            'timestamp': job.created_at.isoformat(),
            'description': f"Job '{job.title}' created"
        })
        
        # Job accepted
        if job.worker_id:
            timeline.append({
                'event': 'job_accepted',
                'timestamp': job.updated_at.isoformat(),
                'description': 'Job accepted by worker'
            })
        
        # All updates
        for update in updates:
            if update.update_type == 'progress':
                timeline.append({
                    'event': 'progress_update',
                    'timestamp': update.created_at.isoformat(),
                    'description': f"Progress: {update.progress_percentage}%",
                    'note': update.note
                })
            elif update.update_type == 'note':
                timeline.append({
                    'event': 'note_added',
                    'timestamp': update.created_at.isoformat(),
                    'description': update.note
                })
            elif update.update_type == 'photo':
                timeline.append({
                    'event': 'photos_uploaded',
                    'timestamp': update.created_at.isoformat(),
                    'description': f"{len(update.photo_urls)} photos uploaded",
                    'photo_urls': update.photo_urls
                })
            elif update.update_type == 'status_change':
                timeline.append({
                    'event': 'status_changed',
                    'timestamp': update.created_at.isoformat(),
                    'description': f"Status changed: {update.old_status} → {update.new_status}"
                })
        
        # Job completed
        if job.completed_at:
            timeline.append({
                'event': 'job_completed',
                'timestamp': job.completed_at.isoformat(),
                'description': 'Job marked as completed'
            })
        
        return timeline
