# KaziConnect - Quick Start Guide

## ✅ App is Running!

The Flask server is now running on:
- Local: http://127.0.0.1:5000
- Network: http://172.31.4.219:5000

## 🚀 Next Steps

### 1. Initialize Database
```bash
# Create migrations folder
pipenv run flask db init

# Generate migration
pipenv run flask db migrate -m "Initial migration"

# Apply migration
pipenv run flask db upgrade
```

### 2. Test API Endpoints

#### Register a User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@test.com",
    "password": "password123",
    "full_name": "John Doe",
    "phone": "+254712345678",
    "role": "customer"
  }'
```

#### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@test.com",
    "password": "password123"
  }'
```

#### Get Categories
```bash
curl http://localhost:5000/api/categories
```

### 3. Configure Database

Edit `.env` file with your PostgreSQL credentials:
```
DATABASE_URL=postgresql://username:password@localhost:5432/kaziconnect
```

Or create the database:
```bash
sudo -u postgres psql
CREATE DATABASE kaziconnect;
CREATE USER kaziuser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE kaziconnect TO kaziuser;
\q
```

### 4. Test Offline Sync (Mobile Client)

```bash
# Queue offline action
curl -X POST http://localhost:5000/api/sync/queue \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
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
  }'
```

### 5. Test SMS Integration

Configure Africa's Talking in `.env`:
```
AFRICASTALKING_USERNAME=your-username
AFRICASTALKING_API_KEY=your-api-key
```

Send test SMS:
```bash
curl -X POST http://localhost:5000/api/sms/send \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+254712345678",
    "message": "Test message from KaziConnect"
  }'
```

### 6. Test USSD (Simulator)

Use Africa's Talking USSD simulator:
https://simulator.africastalking.com:1517/

Callback URL: `http://your-server.com/api/ussd/callback`

## 📁 Project Structure

```
KaziConnect-/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   └── utils/           # Helpers
├── data/
│   └── categories.json  # ML-ready categories
├── config.py            # App configuration
├── run.py              # Entry point
└── .env                # Environment variables
```

## 🔑 Key Features

✅ JWT Authentication
✅ Role-based Access Control
✅ Escrow Payment System
✅ Offline Sync Queue
✅ SMS Integration (Africa's Talking)
✅ USSD Support (Feature Phones)
✅ ML-Ready Categories
✅ Worker Ratings & Reviews
✅ Job Status Flow
✅ Wallet & Transactions

## 📚 Documentation

- API Endpoints: See `README.md`
- Offline Guide: See `OFFLINE_GUIDE.md`
- Categories: See `data/categories.json`

## 🐛 Troubleshooting

**Database Connection Error:**
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify credentials in `.env`

**Module Not Found:**
- Install dependencies: `pipenv install`

**Port Already in Use:**
- Change port in `run.py`: `app.run(port=5001)`

## 🚀 Production Deployment

1. Set production environment variables
2. Use production WSGI server (gunicorn)
3. Set up SSL/TLS
4. Configure Africa's Talking webhooks
5. Set up database backups
6. Enable monitoring

```bash
# Production run
pipenv run gunicorn -w 4 -b 0.0.0.0:8000 run:app
```
