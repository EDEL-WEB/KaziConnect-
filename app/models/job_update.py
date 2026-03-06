import uuid
from datetime import datetime
from app import db

class JobUpdate(db.Model):
    __tablename__ = 'job_updates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = db.Column(db.String(36), db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Update type: progress, note, photo, status_change
    update_type = db.Column(db.Enum('progress', 'note', 'photo', 'status_change', name='update_types'), nullable=False)
    
    # Progress percentage (0-100)
    progress_percentage = db.Column(db.Integer)
    
    # Text note
    note = db.Column(db.Text)
    
    # Photo URLs (JSON array)
    photo_urls = db.Column(db.JSON)
    
    # Status change
    old_status = db.Column(db.String(50))
    new_status = db.Column(db.String(50))
    
    # Offline tracking
    created_offline = db.Column(db.Boolean, default=False)
    synced_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
