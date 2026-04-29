pip install -r requirements.txt  
python manage.py makemigrations  
python manage.py migrate  
python manage.py runserver  

celery -A config worker --loglevel=info

# Playto Payout Engine

## 🚀 Overview

This project implements a minimal payout engine similar to Playto Pay.

Merchants receive credits from international payments and can request payouts to Indian bank accounts. The system ensures:

* Money integrity
* Concurrency safety
* Idempotent APIs
* Reliable payout processing

---

## 🧱 Tech Stack

* Backend: Django + Django REST Framework
* Database: PostgreSQL
* Background Jobs: Celery + Redis
* Deployment: Render

---

## ⚙️ Setup Instructions

### 1. Clone Repo

```bash
git clone https://github.com/gopi9753/ptp.git
cd ptp/backend
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables

```env
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=5432
CELERY_BROKER_URL=your_redis_url
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Run Server

```bash
python manage.py runserver
```

---

## 🧪 API Endpoints

### Check Balance

GET /api/v1/balance

### Create Payout

POST /api/v1/payouts

Headers:
Idempotency-Key: <UUID>

Body:

```json
{
  "amount_paise": 5000,
  "bank_account_id": "123"
}
```

---

## 🌐 Live Deployment

https://ptp-y16f.onrender.com

---

## ✅ Features Implemented

* Ledger-based balance system
* Idempotent payout API
* Concurrency-safe balance deduction
* Background payout processor
* Retry mechanism with backoff
* Docker + production deployment

---

## 🧪 Tests Covered

* Idempotency test
* Concurrency test

---

## 📌 Notes

* All amounts stored in paise (integer)
* No floating point usage
* Strong transactional guarantees
