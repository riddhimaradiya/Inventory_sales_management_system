# Inventory Management System

A Django REST Framework backend for managing products, customers, and orders — with automated GST calculation, WhatsApp/email notifications, promotional sale campaigns, and async background jobs via Celery.

## Features

- **Product management** — CRUD, bulk create, low-stock filtering, stock movement audit log (restock/sale/return)
- **Customer management** — CRUD with Indian mobile number validation
- **Order processing** — stock validation, per-product GST calculation, simulated payment, atomic transactions
- **Sale campaigns** — time-bound percentage/flat discounts, auto-applied at checkout, WhatsApp broadcast to customers
- **Notifications** — WhatsApp (Twilio) order confirmations & payment alerts, low-stock and daily stock report emails, all tracked in a central delivery log
- **Async jobs** — Celery + Celery Beat for scheduled daily stock reports and campaign broadcasts, using a self-contained filesystem broker (no Redis/external service required)

## Tech Stack

- Python, Django, Django REST Framework
- PostgreSQL
- Celery, Celery Beat (filesystem broker + Django DB result backend)
- Twilio WhatsApp API
- django-filter

## Project Structure

```
Inventory_Management_system/
├── config/          # Settings, root URLs, Celery app
├── products/        # Product, stock movement, low-stock alerts, daily report task
├── customers/        # Customer CRUD
├── orders/          # Order creation, GST calc, payment simulation
├── payments/         # Payment model & simulated payment service
├── notifications/    # Twilio WhatsApp service, NotificationLog
├── campaigns/         # Sale campaigns, discount logic, WhatsApp broadcast task
└── common/            # Shared pagination, etc.
```

## Setup

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/riddhimaradiya/Inventory_Management_system.git
cd Inventory_Management_system
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
# Database
DB_NAME=inventory_db
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email (SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
ADMIN_EMAIL=admin@example.com

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
TWILIO_WHATSAPP_CONTENT_SID=your_approved_content_sid
```

> `EMAIL_HOST_PASSWORD` must be a Gmail **App Password** (not your normal login password) if using Gmail SMTP with 2-Step Verification enabled.

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

### 6. Start Celery (for async notifications, scheduled reports, campaign broadcasts)

In two separate terminals, with the venv activated:

```bash
celery -A config worker --loglevel=info --pool=solo
celery -A config beat --loglevel=info
```

> `--pool=solo` is required on Windows; Celery's default prefork pool doesn't work there.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/products/` | Create a product (single object or array for bulk create) |
| `GET` | `/api/products/` | List products (filter: `?is_active=`, `?low_stock=true`) |
| `GET` | `/api/products/<id>/` | Get product detail |
| `PATCH` | `/api/products/<id>/` | Update product (e.g. reactivate: `is_active: true`) |
| `PATCH` | `/api/products/<id>/stock/` | Adjust stock (`RESTOCK` / `SALE` / `RETURN`) |
| `GET` | `/api/products/<id>/stock-movements/` | View stock movement history |
| `POST` | `/api/customers/` | Create a customer |
| `GET` | `/api/customers/` | List customers |
| `GET` | `/api/customers/<id>/` | Get customer detail |
| `POST` | `/api/orders/` | Place an order (validates stock, calculates GST, simulates payment, sends WhatsApp) |
| `POST` | `/api/notifications/test-whatsapp/` | Send a direct WhatsApp test message |
| `POST` | `/api/campaigns/` | Create a sale campaign |
| `GET` | `/api/campaigns/` | List campaigns |
| `GET` | `/api/campaigns/<id>/` | Get campaign detail |
| `PATCH` | `/api/campaigns/<id>/` | Update campaign |
| `POST` | `/api/campaigns/<id>/broadcast/` | Queue a WhatsApp broadcast to all active customers (async) |

## Background Jobs

| Task | Trigger | Purpose |
|---|---|---|
| `send_daily_stock_report_task` | Celery Beat, daily 8 AM | Emails admin a CSV of all active products' stock levels |
| `send_campaign_broadcast_task` | `/api/campaigns/<id>/broadcast/` | WhatsApp-blasts a campaign to all active customers |

