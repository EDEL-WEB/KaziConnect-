import uuid
from datetime import datetime
from app import db

class SyncQueue(db.Model):
    __tablename__ = 'sync_queue'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    device_id = db.Column(db.String(100), nullable=False)
    action_type = db.Column(db.Enum('create_job', 'update_job', 'upload_photo', 'add_note', name='sync_actions'), nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    client_timestamp = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('pending', 'processing', 'completed', 'failed', name='sync_statuses'), default='pending', index=True)
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    processed_at = db.Column(db.DateTime)

class SMSLog(db.Model):
    __tablename__ = 'sms_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = db.Column(db.String(20), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    direction = db.Column(db.Enum('inbound', 'outbound', name='sms_directions'), nullable=False)
    status = db.Column(db.String(50))
    external_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class USSDSession(db.Model):
    __tablename__ = 'ussd_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'))
    state = db.Column(db.String(50), default='start')
    context_data = db.Column(db.JSON, default={})
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
