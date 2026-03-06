# Worker Verification & Authentication Flow

## Overview
Worker verification is now fully integrated with authentication. Workers cannot login until their verification is approved.

## Complete Worker Registration Flow

### Step 1: Register as Worker
```bash
POST /api/auth/register
{
  "email": "worker@example.com",
  "password": "password123",
  "full_name": "John Worker",
  "phone": "+254712345678",
  "role": "worker"
}

Response:
{
  "message": "User registered. Check phone for OTP.",
  "user_id": "user-uuid",
  "requires_verification": true
}
```

**What happens:**
- User account created with `is_active = False`
- SMS OTP sent to phone
- Worker cannot login yet

### Step 2: Verify Phone
```bash
POST /api/auth/verify-otp
{
  "user_id": "user-uuid",
  "otp_code": "123456"
}

Response:
{
  "message": "Phone verified successfully"
}
```

**What happens:**
- Phone marked as verified
- Account still inactive (workers need full verification)
- Customer accounts would be activated here

### Step 3: Create Worker Profile
```bash
POST /api/workers
Authorization: Bearer <token>
{
  "hourly_rate": 500,
  "location": "Nairobi",
  "bio": "Experienced plumber",
  "skills": [
    {
      "category_id": "plumbing-uuid",
      "experience_years": 5
    }
  ]
}

Response:
{
  "message": "Worker profile created",
  "worker_id": "worker-uuid"
}
```

**What happens:**
- Worker profile created
- Verification record auto-created
- Worker still cannot login

### Step 4: Complete Verification

#### 4a. Upload National ID
```bash
POST /api/verification/upload-id
Authorization: Bearer <token>
{
  "national_id_number": "12345678",
  "front_url": "https://storage.com/id-front.jpg",
  "back_url": "https://storage.com/id-back.jpg"
}

Response:
{
  "message": "ID uploaded successfully",
  "overall_score": 25,
  "flagged": false
}
```

**Score: +25 points**

#### 4b. Verify Phone (Worker Verification)
```bash
POST /api/verification/verify-phone
Authorization: Bearer <token>
{
  "otp_code": "123456"
}

Response:
{
  "message": "Phone verified",
  "overall_score": 45
}
```

**Score: +20 points (Total: 45)**

#### 4c. Upload Selfie
```bash
POST /api/verification/upload-selfie
Authorization: Bearer <token>
{
  "selfie_url": "https://storage.com/selfie.jpg"
}

Response:
{
  "message": "Selfie uploaded",
  "face_match_score": 0.85,
  "overall_score": 70,
  "flagged": false
}
```

**Score: +25 points (Total: 70)**

**If score >= 60: AUTO-APPROVED! ✅**

#### 4d. Upload Skills (Optional)
```bash
POST /api/verification/upload-skills
Authorization: Bearer <token>
{
  "documents_urls": [
    "https://storage.com/cert1.pdf",
    "https://storage.com/cert2.pdf"
  ]
}

Response:
{
  "message": "Skill documents uploaded (optional bonus)",
  "overall_score": 85,
  "auto_approved": true,
  "manual_review_required": false
}
```

**Score: +15 points (Total: 85)**

### Step 5: Auto-Approval or Manual Review

#### If Score >= 60: Auto-Approved
```
System automatically:
1. Sets worker.verification_status = 'verified'
2. Sets user.is_active = True
3. Sends notification: "Account verified! You can now login."
```

#### If Score 45-59: Manual Review Required
```
System:
1. Flags for manual review
2. Admin reviews via /api/verification/admin/review/<id>
3. If approved: Account activated
4. If rejected: Account remains inactive
```

#### If Score < 45: Flagged
```
System:
1. Flags verification
2. Requires manual admin review
3. Cannot login until approved
```

### Step 6: Login (After Verification)

#### Before Verification
```bash
POST /api/auth/login
{
  "email": "worker@example.com",
  "password": "password123"
}

Response: 401 Unauthorized
{
  "error": "Your worker verification is pending. Please complete verification or wait for admin approval."
}
```

#### After Verification
```bash
POST /api/auth/login
{
  "email": "worker@example.com",
  "password": "password123"
}

Response: 200 OK
{
  "token": "jwt-token",
  "user": {
    "id": "user-uuid",
    "email": "worker@example.com",
    "role": "worker"
  }
}
```

**Worker can now login and accept jobs!**

## Admin Review Process

### Get Pending Reviews
```bash
GET /api/verification/admin/pending
Authorization: Bearer <admin-token>

Response:
{
  "pending_reviews": [
    {
      "id": "verification-uuid",
      "worker_id": "worker-uuid",
      "overall_score": 55,
      "flagged": false,
      "created_at": "2024-03-03T10:00:00"
    }
  ]
}
```

### Approve Worker
```bash
POST /api/verification/admin/review/verification-uuid
Authorization: Bearer <admin-token>
{
  "approved": true,
  "notes": "All documents verified"
}

Response:
{
  "message": "Review completed",
  "approved": true
}
```

**What happens:**
1. Worker verification status set to 'verified'
2. User account activated (`is_active = True`)
3. SMS/Push notification sent: "Account approved!"
4. Worker can now login

### Reject Worker
```bash
POST /api/verification/admin/review/verification-uuid
Authorization: Bearer <admin-token>
{
  "approved": false,
  "notes": "ID photo unclear, please resubmit"
}

Response:
{
  "message": "Review completed",
  "approved": false
}
```

**What happens:**
1. Worker verification status set to 'rejected'
2. Account remains inactive
3. SMS/Push notification sent with rejection reason
4. Worker cannot login

## Verification Status Check

```bash
GET /api/verification/status
Authorization: Bearer <worker-token>

Response:
{
  "overall_score": 70,
  "id_verified": true,
  "phone_verified": true,
  "face_verified": true,
  "skill_verified": false,
  "auto_approved": true,
  "manual_review_required": false,
  "flagged": false
}
```

## Account States

### Customer Account States
```
1. Registered → is_active = False, phone_verified = False
2. Phone Verified → is_active = True, phone_verified = True
3. Can Login → ✅
```

### Worker Account States
```
1. Registered → is_active = False, phone_verified = False
2. Phone Verified → is_active = False, phone_verified = True
3. Profile Created → is_active = False, verification_status = 'pending'
4. Verification Started → is_active = False, overall_score = 0
5. ID Uploaded → is_active = False, overall_score = 25
6. Phone Verified → is_active = False, overall_score = 45
7. Selfie Uploaded → is_active = False, overall_score = 70
8. Auto-Approved → is_active = True, verification_status = 'verified'
9. Can Login → ✅
```

## Error Messages

### Worker Tries to Login Before Verification
```
Error: "Your worker verification is pending. Please complete verification or wait for admin approval."
```

### Customer Tries to Login Before Phone Verification
```
Error: "Please verify your phone number first."
```

### Worker Verification Rejected
```
Error: "Your worker verification was not approved. Reason: [admin notes]"
```

## Notifications

### Auto-Approval Notification
```
Title: "Account Verified"
Message: "Congratulations! Your worker account has been verified. You can now start accepting jobs."
Type: SMS (if offline) or Push (if online)
```

### Admin Approval Notification
```
Title: "Account Approved"
Message: "Your worker account has been approved by admin. You can now login and start accepting jobs."
Type: SMS (if offline) or Push (if online)
```

### Rejection Notification
```
Title: "Verification Rejected"
Message: "Your worker verification was not approved. Reason: [admin notes]"
Type: SMS (if offline) or Push (if online)
```

## Summary

✅ Workers cannot login until verified
✅ Auto-approval at 60+ points activates account
✅ Manual admin approval activates account
✅ Notifications sent on approval/rejection
✅ Clear error messages for each state
✅ Verification record auto-created with worker profile
✅ Customers can login after phone verification
✅ Workers need full verification before login
