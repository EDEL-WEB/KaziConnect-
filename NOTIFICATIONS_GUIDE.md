# Smart Notification System

## Overview
KaziConnect uses intelligent notifications that automatically choose between push notifications and SMS based on user's online status.

## How It Works

### Online/Offline Detection
```
User opens app → Sends heartbeat every 30 seconds → Marked as ONLINE
User closes app → Stops heartbeat → Marked as OFFLINE after 5 minutes
```

### Smart Notification Logic
```
IF user is ONLINE:
    → Send push notification (instant, free)
ELSE:
    → Send SMS notification (reliable, costs money)
```

## User Presence Tracking

### Heartbeat (Mobile App)
```
POST /api/notifications/heartbeat
Authorization: Bearer <token>

{
  "device_id": "device-123",
  "device_type": "android"
}
```

**Mobile app should call this every 30 seconds while app is active**

### Go Offline
```
POST /api/notifications/offline
Authorization: Bearer <token>
```

**Call this when app goes to background or user logs out**

### Check User Status
```
GET /api/notifications/status/<user_id>
Authorization: Bearer <token>

Response:
{
  "user_id": "user-uuid",
  "is_online": true,
  "last_seen": "2024-03-03T15:30:00"
}
```

## Notification Flow Examples

### Example 1: Both Users Online
```
Customer creates job
  ↓
System checks: Worker is ONLINE
  ↓
Send PUSH notification to worker
  ↓
Worker sees notification instantly
```

### Example 2: Worker Offline
```
Customer creates job
  ↓
System checks: Worker is OFFLINE
  ↓
Send SMS to worker's phone
  ↓
Worker receives SMS even without app
```

### Example 3: Customer Offline
```
Worker completes job
  ↓
System checks: Customer is OFFLINE
  ↓
Send SMS to customer
  ↓
Customer gets SMS to approve job
```

## Notification Types

### Job Created
- **To**: Nearby workers with matching skills
- **Message**: "New job available: [title] in [location]. Budget: KES [amount]"
- **Priority**: High

### Job Accepted
- **To**: Customer who posted job
- **Message**: "Your job '[title]' has been accepted by a worker!"
- **Priority**: High

### Job Completed
- **To**: Customer
- **Message**: "Job '[title]' has been marked as completed. Please review and approve."
- **Priority**: High

### Payment Released
- **To**: Worker
- **Message**: "Payment of KES [amount] released for job: [title]"
- **Priority**: High

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/notifications/heartbeat` | POST | Update online status |
| `/api/notifications/offline` | POST | Mark as offline |
| `/api/notifications/pending` | GET | Get pending notifications |
| `/api/notifications/<id>/mark-read` | POST | Mark as read |
| `/api/notifications/status/<user_id>` | GET | Check if user online |

## Mobile App Integration

### Android/iOS Implementation

```javascript
// Start heartbeat when app opens
function startHeartbeat() {
  setInterval(() => {
    fetch('/api/notifications/heartbeat', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        device_id: getDeviceId(),
        device_type: 'android'
      })
    });
  }, 30000); // Every 30 seconds
}

// Stop heartbeat when app closes
function stopHeartbeat() {
  fetch('/api/notifications/offline', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
}
```

## SMS Integration

### Automatic SMS Sending
```python
# In notification_service.py
if user_is_offline:
    send_sms(user.phone, message)
else:
    send_push_notification(user.device_token, message)
```

### SMS Gateway (Africa's Talking)
```python
from app.services.sms_service import SMSService

sms = SMSService()
sms.send_sms(phone="+254712345678", message="Your job has been accepted!")
```

## Database Models

### Notification
- `user_id`: Who receives notification
- `job_id`: Related job
- `type`: push, sms, or ussd
- `message`: Notification content
- `status`: pending, sent, delivered, failed
- `priority`: high, normal, low

### UserPresence
- `user_id`: User ID
- `is_online`: Boolean
- `last_seen`: Last activity timestamp
- `last_heartbeat`: Last heartbeat timestamp
- `device_id`: Device identifier

## Offline Queue Integration

When user is offline:
1. Actions queued in `SyncQueue`
2. Notifications queued in `Notification` table
3. SMS sent immediately if offline
4. When user comes online:
   - Sync queue processed
   - Pending push notifications sent
   - SMS notifications marked as delivered

## Cost Optimization

### SMS vs Push Notifications
- **Push**: Free, instant, requires app
- **SMS**: ~KES 1 per message, works without app

### Smart Logic Saves Money
```
If 1000 notifications/day:
- All SMS: KES 1000/day = KES 30,000/month
- Smart (80% push, 20% SMS): KES 200/day = KES 6,000/month
- Savings: KES 24,000/month (80% reduction)
```

## Background Tasks

### Retry Failed Notifications
```python
# Run every 5 minutes
NotificationService.retry_failed_notifications()
```

### Clean Old Notifications
```python
# Delete notifications older than 30 days
Notification.query.filter(
    Notification.created_at < datetime.utcnow() - timedelta(days=30)
).delete()
```

## Testing

### Test Online User
```bash
# 1. Login and get token
# 2. Send heartbeat
curl -X POST http://localhost:5000/api/notifications/heartbeat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"device_id": "test-device"}'

# 3. Create job (should send push notification)
```

### Test Offline User
```bash
# 1. Don't send heartbeat (or wait 5 minutes)
# 2. Create job (should send SMS)
```

## Production Checklist

- [ ] Configure SMS gateway credentials
- [ ] Set up push notification service (FCM/APNS)
- [ ] Implement background task queue (Celery/RQ)
- [ ] Monitor SMS costs
- [ ] Set up notification analytics
- [ ] Implement rate limiting
- [ ] Add notification preferences (user can disable SMS)
