# Authentication & Verification System

## Overview
KaziConnect implements a multi-tier authentication system with role-based access and comprehensive worker verification.

## User Roles

### 1. Customer
- **Registration**: Email + Password + Phone
- **2FA Required**: Yes (SMS OTP on every login)
- **Verification**: Phone OTP only

### 2. Worker
- **Registration**: Email + Password + Phone
- **2FA Required**: No (direct login after verification)
- **Verification**: Multi-step process with scoring system

### 3. Admin
- **Creation**: Manual via Flask shell
- **Email**: kaziconnect@26.com
- **2FA Required**: No
- **Access**: Full system access

## Customer Authentication Flow

### Registration
```
POST /api/auth/register
{
  "email": "customer@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "phone": "+254712345678",
  "role": "customer"
}

Response: OTP sent to phone
```

### Verify Phone
```
POST /api/auth/verify-otp
{
  "user_id": "user-uuid",
  "otp_code": "123456"
}

Response: Account activated
```

### Login (2FA)
```
POST /api/auth/login
{
  "email": "customer@example.com",
  "password": "password123"
}

Response: OTP sent to phone, requires_2fa: true
```

### Verify Login OTP
```
POST /api/auth/verify-login-otp
{
  "user_id": "user-uuid",
  "otp_code": "123456"
}

Response: JWT token
```

## Worker Verification System

### Scoring System (0-100 points)

| Component | Points | Requirements |
|-----------|--------|--------------|
| National ID | 25 | Upload front & back, unique ID number |
| Phone Verification | 20 | SMS OTP confirmation |
| Facial Recognition | 30 | Selfie matches ID photo (80%+ match) |
| Skill Documents | 25 | Certificates, portfolio (3+ docs = full points) |

### Auto-Approval Thresholds

- **80+ points**: Auto-approved ✅
- **60-79 points**: Manual review required 👤
- **<60 points**: Flagged for review 🚩

### Verification Flow

#### Step 1: Initiate Verification
```
POST /api/verification/initiate
Headers: Authorization: Bearer <worker-token>

Response: verification_id
```

#### Step 2: Upload National ID
```
POST /api/verification/upload-id
{
  "national_id_number": "12345678",
  "front_url": "https://storage.com/id-front.jpg",
  "back_url": "https://storage.com/id-back.jpg"
}

Response: overall_score, flagged status
```

**Flagging Conditions:**
- Duplicate national ID number
- Invalid ID format

#### Step 3: Verify Phone
```
POST /api/verification/verify-phone
{
  "otp_code": "123456"
}

Response: overall_score updated (+20 points)
```

#### Step 4: Upload Selfie (Facial Recognition)
```
POST /api/verification/upload-selfie
{
  "selfie_url": "https://storage.com/selfie.jpg"
}

Response: face_match_score (0.0-1.0), overall_score
```

**Face Match Scoring:**
- 0.80-1.0: Verified ✅ (+30 points)
- 0.60-0.79: Manual review 👤
- <0.60: Flagged 🚩

#### Step 5: Upload Skill Documents
```
POST /api/verification/upload-skills
{
  "documents_urls": [
    "https://storage.com/cert1.pdf",
    "https://storage.com/cert2.pdf",
    "https://storage.com/portfolio.pdf"
  ]
}

Response: overall_score, auto_approved, manual_review_required
```

**Skill Scoring:**
- 3+ documents: 25 points
- 1-2 documents: 15 points
- 0 documents: 0 points

#### Check Verification Status
```
GET /api/verification/status

Response:
{
  "overall_score": 85,
  "id_verified": true,
  "phone_verified": true,
  "face_verified": true,
  "skill_verified": true,
  "auto_approved": true,
  "manual_review_required": false,
  "flagged": false
}
```

## Admin Review System

### Get Pending Reviews
```
GET /api/verification/admin/pending
Headers: Authorization: Bearer <admin-token>

Response: List of verifications requiring manual review
```

### Review Worker
```
POST /api/verification/admin/review/<verification_id>
{
  "approved": true,
  "notes": "All documents verified"
}

Response: Worker status updated
```

## Security Features

### Login Attempt Tracking
- Logs all login attempts (success/failure)
- Tracks IP address and user agent
- Locks account after 5 failed attempts in 15 minutes

### OTP Security
- 6-digit random code
- 10-minute expiration
- One-time use only
- SMS delivery via Africa's Talking

### Fraud Detection
- Duplicate national ID detection
- Low face match score flagging
- Suspicious login pattern detection

## Create Admin User

### Via Flask Shell
```bash
pipenv run python create_admin.py
```

Or manually:
```bash
pipenv run flask shell

>>> from app.services.auth_service import AuthService
>>> admin = AuthService.create_admin(
...     email='kaziconnect@26.com',
...     password='YourSecurePassword',
...     full_name='Admin Name',
...     phone='+254700000000'
... )
>>> print(f"Admin created: {admin.id}")
```

## API Endpoints Summary

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/verify-otp` - Verify registration OTP
- `POST /api/auth/login` - Login (2FA for customers)
- `POST /api/auth/verify-login-otp` - Verify login OTP

### Worker Verification
- `POST /api/verification/initiate` - Start verification
- `POST /api/verification/upload-id` - Upload national ID
- `POST /api/verification/verify-phone` - Verify phone
- `POST /api/verification/upload-selfie` - Upload selfie
- `POST /api/verification/upload-skills` - Upload skill docs
- `GET /api/verification/status` - Check status

### Admin
- `GET /api/verification/admin/pending` - Pending reviews
- `POST /api/verification/admin/review/<id>` - Review worker

## Database Models

### OTPVerification
- Stores OTP codes with expiration
- Tracks verification status
- Purpose: registration, login, phone_verification

### WorkerVerification
- Comprehensive verification data
- Scoring system fields
- Admin review tracking
- Flagging system

### LoginAttempt
- Security audit trail
- Failed attempt tracking
- IP and user agent logging

## Testing

### Test Customer Registration
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@customer.com",
    "password": "password123",
    "full_name": "Test Customer",
    "phone": "+254712345678",
    "role": "customer"
  }'
```

### Test Worker Verification
```bash
# 1. Register as worker
# 2. Login to get token
# 3. Initiate verification
# 4. Complete all verification steps
# 5. Check if auto-approved or needs review
```

## Production Considerations

1. **Face Recognition API**: Integrate AWS Rekognition or similar
2. **ID Verification API**: Use third-party ID verification service
3. **SMS Provider**: Configure Africa's Talking production credentials
4. **File Storage**: Use S3 or similar for document uploads
5. **Rate Limiting**: Implement rate limiting on OTP endpoints
6. **Monitoring**: Track verification success rates and fraud attempts
