# Offline & SMS/USSD Integration Guide

## Overview
KaziConnect supports low-data, offline-first operations for African markets with SMS and USSD integration.

## Features

### 1. Offline Sync Queue
- Queue actions offline (create jobs, update status, add notes)
- Automatic conflict resolution on sync
- Prevents duplicate submissions
- Timestamp-based validation

### 2. SMS Integration (Africa's Talking)
- Job notifications to workers
- Two-way SMS replies (YES/NO to accept jobs)
- OTP verification
- Payment notifications
- Status updates

### 3. USSD Integration
- Feature phone support (no smartphone needed)
- Book services via USSD menu
- Check job status
- Cancel jobs
- Session-based navigation

## API Endpoints

### Offline Sync
```
POST /api/sync/queue - Queue single offline action
POST /api/sync/batch - Batch upload multiple actions
GET /api/sync/status - Check pending sync count
```

### SMS
```
POST /api/sms/callback - Webhook for incoming SMS
POST /api/sms/send - Send SMS manually
```

### USSD
```
POST /api/ussd/callback - USSD session handler
```

## Usage Examples

### Mobile Client - Queue Offline Job
```json
POST /api/sync/queue
{
  "device_id": "device-123",
  "action_type": "create_job",
  "client_timestamp": "2024-03-03T10:00:00",
  "payload": {
    "category_id": "cat-uuid",
    "title": "Plumbing repair",
    "description": "Fix leaking pipe",
    "location": "Nairobi",
    "budget": 2000
  }
}
```

### Batch Sync When Online
```json
POST /api/sync/batch
{
  "actions": [
    {
      "device_id": "device-123",
      "action_type": "create_job",
      "client_timestamp": "2024-03-03T10:00:00",
      "payload": {...}
    },
    {
      "device_id": "device-123",
      "action_type": "update_job",
      "client_timestamp": "2024-03-03T10:05:00",
      "payload": {
        "job_id": "job-uuid",
        "status": "in_progress"
      }
    }
  ]
}
```

### SMS Worker Notification
```python
from app.services.sms_service import SMSService

sms = SMSService()
sms.send_job_notification(
    phone="+254712345678",
    job_title="Plumbing repair",
    job_id="job-uuid"
)
```

Worker receives: "New job: Plumbing repair. Reply YES job-uuid to accept or NO job-uuid to decline."

### USSD Flow
```
Dial: *384*1234#

CON KaziConnect
1. Book Service
2. My Jobs
3. Cancel Job

User enters: 1

CON Select Category:
1. Plumbing
2. Electrical
3. Cleaning

User enters: 1

CON Enter location:
User enters: Nairobi

CON Enter budget (KES):
User enters: 2000

END Job created! ID: abc12345. SMS updates coming.
```

## Configuration

Add to `.env`:
```
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your-api-key
```

## Conflict Resolution

### Duplicate Prevention
- Checks for existing jobs with same title and timestamp
- Returns existing job ID instead of creating duplicate

### Stale Updates
- Compares client timestamp with server updated_at
- Ignores updates older than server state

### Payment Safety
- Payments only execute on server after job completion
- Never processed from offline queue
- Requires explicit customer confirmation

## Database Models

### SyncQueue
- Stores offline actions with timestamps
- Tracks processing status (pending/processing/completed/failed)
- Retry count for failed syncs

### SMSLog
- Logs all inbound/outbound SMS
- Tracks delivery status
- Links to external provider message IDs

### USSDSession
- Maintains session state across USSD interactions
- Stores context data (selected category, location, etc.)
- Auto-expires inactive sessions

## Testing

### Test SMS (Sandbox)
```bash
curl -X POST http://localhost:5000/api/sms/send \
  -H "Content-Type: application/json" \
  -d '{"phone": "+254712345678", "message": "Test message"}'
```

### Test USSD (Simulator)
Use Africa's Talking USSD simulator at:
https://simulator.africastalking.com:1517/

## Production Checklist
- [ ] Configure Africa's Talking production credentials
- [ ] Set up SMS webhook URL (publicly accessible)
- [ ] Set up USSD callback URL
- [ ] Configure USSD short code
- [ ] Test offline sync with poor connectivity
- [ ] Monitor sync queue for failed items
- [ ] Set up retry mechanism for failed syncs
