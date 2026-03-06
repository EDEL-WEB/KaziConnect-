# Escrow Payment System - Beginner's Guide

## Overview
KaziConnect uses a secure escrow system to protect both customers and workers during transactions.

## Payment Flow (Step by Step)

### STEP 1: Customer Creates Job + Pre-Authorization
```
Customer posts a job → System pre-authorizes payment (reserves funds)
```

**Endpoint**: `POST /api/escrow/jobs/create`

**What happens:**
- Job is created with status: `pending`
- Payment is pre-authorized (funds reserved but not charged)
- Escrow status: `pre_authorized`

**Example Request:**
```json
POST /api/escrow/jobs/create
Authorization: Bearer <customer-token>

{
  "category_id": "plumbing-uuid",
  "title": "Fix leaking pipe",
  "description": "Kitchen sink is leaking",
  "location": "Nairobi",
  "budget": 2000
}
```

**Response:**
```json
{
  "message": "Job created and payment pre-authorized",
  "job_id": "job-uuid",
  "amount": "2000",
  "commission": "300",
  "worker_payout": "1700",
  "escrow_status": "pre_authorized",
  "status": "pending"
}
```

### STEP 2: Worker Accepts Job + Payment Held
```
Worker accepts job → Customer is charged → Money held in escrow
```

**Endpoint**: `POST /api/escrow/jobs/<job_id>/accept`

**What happens:**
- Worker accepts the job
- Customer is charged (money leaves customer's account)
- Money is held in escrow (locked, cannot be used)
- Job status: `accepted`
- Escrow status: `held`

**Example Request:**
```json
POST /api/escrow/jobs/abc123/accept
Authorization: Bearer <worker-token>
```

**Response:**
```json
{
  "message": "Job accepted and payment held in escrow",
  "job_id": "abc123",
  "escrow_status": "held",
  "status": "accepted",
  "amount_held": "2000"
}
```

### STEP 3: Worker Completes Job
```
Worker finishes work → Marks job as completed → Waits for customer approval
```

**Endpoint**: `POST /api/escrow/jobs/<job_id>/complete`

**What happens:**
- Job status changes to `completed`
- Customer is notified to approve
- Money still held in escrow (not released yet)

**Example Request:**
```json
POST /api/escrow/jobs/abc123/complete
Authorization: Bearer <worker-token>
```

**Response:**
```json
{
  "message": "Job marked as completed. Waiting for customer approval.",
  "job_id": "abc123",
  "status": "completed",
  "escrow_status": "held"
}
```

### STEP 4: Customer Approves + Payment Released
```
Customer approves work → Money released to worker → Commission deducted
```

**Endpoint**: `POST /api/escrow/jobs/<job_id>/approve`

**What happens:**
- Money is transferred from escrow to worker's wallet
- Platform commission (15%) is deducted
- Worker receives 85% of job amount
- Escrow status: `released`

**Example Request:**
```json
POST /api/escrow/jobs/abc123/approve
Authorization: Bearer <customer-token>
```

**Response:**
```json
{
  "message": "Payment released to worker",
  "job_id": "abc123",
  "worker_payout": "1700",
  "commission": "300",
  "escrow_status": "released",
  "released_at": "2024-03-03T15:30:00"
}
```

## Alternative Flows

### Cancel Job (Before Completion)
```
POST /api/escrow/jobs/<job_id>/cancel
```

**What happens:**
- Job is cancelled
- Full amount refunded to customer
- No commission charged
- Escrow status: `refunded`

### Dispute Resolution (Admin Only)
```
POST /api/escrow/admin/disputes/<job_id>/resolve
```

**Admin can decide:**
- 0% refund = Full payment to worker
- 100% refund = Full refund to customer
- 50% refund = Split 50/50

**Example:**
```json
{
  "resolution": "Customer was partially satisfied",
  "refund_percentage": 50
}
```

## Escrow Status Flow

```
none → pre_authorized → held → released
                         ↓
                      refunded
```

## Job Status Flow

```
pending → accepted → in_progress → completed
                                      ↓
                                  disputed
```

## Security Features

1. **Row Locking**: Prevents double payout using database locks
2. **Authorization Checks**: Only authorized users can perform actions
3. **Status Validation**: Cannot skip steps in the flow
4. **Audit Trail**: All transactions logged with timestamps

## Commission Calculation

```
Job Amount: KES 2000
Commission (15%): KES 300
Worker Payout: KES 1700
```

## API Endpoints Summary

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/api/escrow/jobs/create` | POST | Customer | Create job + pre-authorize |
| `/api/escrow/jobs/<id>/accept` | POST | Worker | Accept job + hold payment |
| `/api/escrow/jobs/<id>/complete` | POST | Worker | Mark job completed |
| `/api/escrow/jobs/<id>/approve` | POST | Customer | Approve + release payment |
| `/api/escrow/jobs/<id>/cancel` | POST | Both | Cancel + refund |
| `/api/escrow/jobs/<id>/status` | GET | Both | Check status |
| `/api/escrow/admin/disputes/<id>/resolve` | POST | Admin | Resolve dispute |

## Testing the Flow

### 1. Create Job (Customer)
```bash
curl -X POST http://localhost:5000/api/escrow/jobs/create \
  -H "Authorization: Bearer <customer-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": "cat-uuid",
    "title": "Plumbing repair",
    "description": "Fix leak",
    "location": "Nairobi",
    "budget": 2000
  }'
```

### 2. Accept Job (Worker)
```bash
curl -X POST http://localhost:5000/api/escrow/jobs/<job-id>/accept \
  -H "Authorization: Bearer <worker-token>"
```

### 3. Complete Job (Worker)
```bash
curl -X POST http://localhost:5000/api/escrow/jobs/<job-id>/complete \
  -H "Authorization: Bearer <worker-token>"
```

### 4. Approve & Release (Customer)
```bash
curl -X POST http://localhost:5000/api/escrow/jobs/<job-id>/approve \
  -H "Authorization: Bearer <customer-token>"
```

## Database Models

### Job Model
- `customer_id`: Who posted the job
- `worker_id`: Who accepted the job
- `amount`: Total job amount
- `status`: Current job status
- `escrow_status`: Current payment status

### Payment Model
- `job_id`: Linked job
- `amount`: Total amount
- `commission`: Platform fee
- `worker_payout`: Amount worker receives
- `status`: Payment status
- `paid_at`: When customer was charged
- `released_at`: When worker was paid

### Wallet Model
- `user_id`: User who owns wallet
- `balance`: Current balance

### Transaction Model
- `wallet_id`: Which wallet
- `payment_id`: Related payment
- `type`: credit or debit
- `amount`: Transaction amount
- `description`: What happened
- `balance_after`: Balance after transaction

## Production Integration

In production, integrate with:
- **M-Pesa API** for mobile money
- **Stripe/Paystack** for card payments
- **SMS Gateway** for notifications

Replace simulation code with actual payment gateway calls.
