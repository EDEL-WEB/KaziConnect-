# KaziConnect Backend API

Production-ready REST API for a service marketplace platform built with Flask and PostgreSQL.

## Features

- **User Authentication**: JWT-based auth with bcrypt password hashing
- **Role-Based Access**: Customer, Worker, Admin roles
- **Worker Profiles**: Skills, rates, location, verification, ratings
- **Job Booking**: Complete status flow (pending → accepted → in_progress → completed)
- **Escrow Payments**: Secure payment holding with 10-15% commission
- **Wallet System**: Transaction logs and balance management
- **Reviews & Ratings**: Auto-updating worker averages
- **PostgreSQL Transactions**: Prevents double payouts

## Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. **Initialize database**:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

4. **Run the application**:
```bash
python run.py
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Users
- `GET /api/users/me` - Get current user profile

### Workers
- `POST /api/workers` - Create worker profile
- `GET /api/workers/search` - Search workers
- `GET /api/workers/<id>` - Get worker details

### Categories
- `POST /api/categories` - Create category (admin)
- `GET /api/categories` - List categories

### Jobs
- `POST /api/jobs` - Create job (customer)
- `POST /api/jobs/<id>/accept` - Accept job (worker)
- `PATCH /api/jobs/<id>/status` - Update job status
- `GET /api/jobs/<id>` - Get job details

### Payments
- `POST /api/payments/release/<job_id>` - Release payment (customer)
- `POST /api/payments/refund/<job_id>` - Refund payment (admin/customer)
- `GET /api/payments/wallet` - Get wallet balance
- `GET /api/payments/transactions` - Get transaction history

### Reviews
- `POST /api/reviews` - Create review (customer)
- `GET /api/reviews/worker/<id>` - Get worker reviews

## Architecture

```
app/
├── models/          # SQLAlchemy models
├── routes/          # Flask blueprints
├── services/        # Business logic
└── utils/           # Validators, decorators
```

## Security Features

- JWT token authentication
- Bcrypt password hashing
- Role-based access control
- Input validation
- SQL injection prevention (SQLAlchemy ORM)
- Transaction locking for payments
