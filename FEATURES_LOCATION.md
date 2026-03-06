# SMS, USSD & Offline Notifications - Feature Location Guide

## ✅ All Features Are Already Implemented!

### 📱 SMS Service
**Location**: `app/services/sms_service.py`

**Features**:
- ✅ Send SMS via Africa's Talking
- ✅ Job notifications
- ✅ OTP codes
- ✅ Status updates
- ✅ Payment notifications
- ✅ Two-way SMS (YES/NO replies)
- ✅ SMS logging

**Example Usage**:
```python
from app.services.sms_service import SMSService

sms = SMSService()
sms.send_sms("+254712345678", "Your job has been accepted!")
sms.send_job_notification(phone, "Plumbing repair", job_id)
```

**API Endpoints**: `app/routes/sms.py`
- `POST /api/sms/callback` - Handle incoming SMS
- `POST /api/sms/send` - Send SMS manually

---

### 📞 USSD Service
**Location**: `app/services/ussd_service.py`

**Features**:
- ✅ USSD menu navigation
- ✅ Book jobs via USSD (*384*1234#)
- ✅ Check job status
- ✅ Session management
- ✅ Feature phone support

**USSD Flow**:
```
Dial *384*1234#
→ Main Menu
→ 1. Book Service
→ Select Category
→ Enter Location
→ Enter Budget
→ Job Created!
```

**API Endpoint**: `app/routes/ussd.py`
- `POST /api/ussd/callback` - USSD session handler

---

### 🔔 Smart Notification Service
**Location**: `app/services/notification_service.py`

**Features**:
- ✅ Online/offline detection
- ✅ Automatic routing (push vs SMS)
- ✅ Send push if online
- ✅ Send SMS if offline
- ✅ Notification queue
- ✅ Retry failed notifications

**How It Works**:
```python
# Automatically chooses push or SMS based on user status
NotificationService.send_notification(
    user_id=worker_id,
    message="New job available!",
    title="Job Alert",
    job_id=job_id
)

# If user is ONLINE → Push notification
# If user is OFFLINE → SMS sent automatically
```

**Key Functions**:
- `is_user_online(user_id)` - Check if user online
- `send_notification()` - Smart routing
- `notify_job_created()` - Notify workers
- `notify_job_accepted()` - Notify customer
- `notify_job_completed()` - Notify customer
- `notify_payment_released()` - Notify worker

**API Endpoints**: `app/routes/notifications.py`
- `POST /api/notifications/heartbeat` - Update online status
- `POST /api/notifications/offline` - Mark offline
- `GET /api/notifications/pending` - Get notifications

---

### 📴 Offline Queue Service
**Location**: `app/services/offline_sync_service.py`

**Features**:
- ✅ Queue actions when offline
- ✅ Auto-sync when online
- ✅ Conflict resolution
- ✅ Duplicate prevention
- ✅ Timestamp validation

**Supported Actions**:
- `create_job` - Create job offline
- `update_job` - Update job status
- `add_note` - Add notes
- `update_progress` - Update progress
- `upload_photo` - Upload photos

**API Endpoints**: `app/routes/sync.py`
- `POST /api/sync/queue` - Queue single action
- `POST /api/sync/batch` - Batch upload
- `GET /api/sync/status` - Check pending count

---

## 🎯 Complete Workflow Examples

### Example 1: Worker Offline, Customer Books Job
```
1. Customer creates job via app
   → POST /api/escrow/jobs/create

2. System checks worker status
   → NotificationService.is_user_online(worker_id)
   → Returns: False (offline)

3. System sends SMS automatically
   → SMSService.send_sms(worker.phone, "New job available...")
   → SMS logged in database

4. Worker receives SMS on phone
   → Even without app open

5. Worker opens app later
   → Sends heartbeat
   → POST /api/notifications/heartbeat

6. Worker accepts job
   → POST /api/escrow/jobs/<id>/accept

7. Customer notified (push or SMS based on status)
```

### Example 2: Worker Updates Progress Offline
```
1. Worker offline, updates progress
   → Mobile app queues action locally

2. Action sent to server when possible
   → POST /api/sync/queue
   → {
       "action_type": "update_progress",
       "payload": {
         "job_id": "abc123",
         "progress_percentage": 50
       }
     }

3. Worker comes online
   → Sends heartbeat
   → POST /api/notifications/heartbeat

4. Sync triggered automatically
   → POST /api/sync/batch
   → All queued actions processed

5. Customer notified of progress
   → If online: Push notification
   → If offline: SMS sent
```

### Example 3: Customer Books via USSD
```
1. Customer dials *384*1234#
   → USSD session starts

2. Africa's Talking sends request
   → POST /api/ussd/callback
   → {
       "sessionId": "session-123",
       "phoneNumber": "+254712345678",
       "text": ""
     }

3. System shows menu
   → "CON KaziConnect\n1. Book Service\n2. My Jobs"

4. Customer selects option
   → Multiple requests back and forth

5. Job created
   → "END Job created! ID: abc12345"

6. Workers notified
   → If online: Push
   → If offline: SMS
```

### Example 4: Worker Accepts via SMS
```
1. Worker receives SMS
   → "New job: Plumbing repair. Reply YES abc123 to accept"

2. Worker replies via SMS
   → "YES abc123"

3. Africa's Talking forwards to webhook
   → POST /api/sms/callback
   → {
       "from": "+254712345678",
       "text": "YES abc123"
     }

4. System processes reply
   → SMSService.handle_incoming_sms()
   → Finds worker by phone
   → Accepts job automatically

5. Customer notified
   → "Your job has been accepted!"
```

---

## 📊 Database Models

### SMS Logging
**Model**: `app/models/offline.py` → `SMSLog`
- Logs all SMS (inbound/outbound)
- Tracks delivery status
- Stores external IDs

### USSD Sessions
**Model**: `app/models/offline.py` → `USSDSession`
- Tracks USSD sessions
- Stores user state
- Context data for multi-step flows

### Notifications
**Model**: `app/models/notification.py` → `Notification`
- Queue for push/SMS notifications
- Priority levels
- Retry tracking

### User Presence
**Model**: `app/models/notification.py` → `UserPresence`
- Online/offline status
- Last heartbeat timestamp
- Device information

### Offline Queue
**Model**: `app/models/offline.py` → `SyncQueue`
- Queued offline actions
- Processing status
- Retry count

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# SMS Gateway
AFRICASTALKING_USERNAME=your-username
AFRICASTALKING_API_KEY=your-api-key

# Database
DATABASE_URL=postgresql://user:pass@localhost/kaziconnect

# JWT
JWT_SECRET_KEY=your-secret-key

# Commission
COMMISSION_RATE=0.15
```

---

## 🧪 Testing

### Test SMS
```bash
curl -X POST http://localhost:5000/api/sms/send \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+254712345678",
    "message": "Test SMS from KaziConnect"
  }'
```

### Test USSD
Use Africa's Talking USSD simulator:
https://simulator.africastalking.com:1517/

### Test Offline Sync
```bash
# Queue action
curl -X POST http://localhost:5000/api/sync/queue \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "test-device",
    "action_type": "create_job",
    "client_timestamp": "2024-03-03T10:00:00",
    "payload": {
      "category_id": "cat-uuid",
      "title": "Test job",
      "description": "Test",
      "location": "Nairobi",
      "budget": 1000
    }
  }'

# Process queue
curl -X POST http://localhost:5000/api/sync/batch \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"actions": []}'
```

### Test Online/Offline
```bash
# Mark online
curl -X POST http://localhost:5000/api/notifications/heartbeat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"device_id": "test-device"}'

# Mark offline
curl -X POST http://localhost:5000/api/notifications/offline \
  -H "Authorization: Bearer <token>"

# Check status
curl http://localhost:5000/api/notifications/status/<user-id> \
  -H "Authorization: Bearer <token>"
```

---

## 📚 Documentation Files

- `OFFLINE_GUIDE.md` - Offline sync details
- `NOTIFICATIONS_GUIDE.md` - Notification system
- `SYSTEM_OVERVIEW.md` - Complete system overview
- `ESCROW_GUIDE.md` - Payment system
- `AUTH_GUIDE.md` - Authentication

---

## ✅ Summary

**Everything is already implemented and working!**

✅ SMS notifications (Africa's Talking)
✅ USSD booking (*384*1234#)
✅ Offline queue & sync
✅ Smart routing (push vs SMS)
✅ Two-way SMS (YES/NO)
✅ Online/offline detection
✅ Automatic notifications

**Just configure your Africa's Talking credentials in `.env` and you're ready to go!**
