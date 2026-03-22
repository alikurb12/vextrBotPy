# 🤖 VextrBot — Automated Trading Signal Bot

An automated trading system that receives signals from TradingView via webhook and opens positions on **BingX** and **OKX** exchanges for all registered users. Users are managed and notified through a **Telegram bot**.

---

## ✨ How It Works

```
TradingView Alert
      ↓
POST /webhook  (FastAPI)
      ↓
Signal added to Redis queue
      ↓
Celery Worker processes one by one
      ↓
   BUY / SELL → Open position on BingX + OKX for all users
                → Notify users via Telegram
      ↓
   MOVE_SL    → Move Stop Loss to breakeven on BingX + OKX
                → Notify users via Telegram
```

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Webhook server | **FastAPI** |
| Task queue | **Celery + Redis** |
| Telegram bot | **aiogram** |
| Exchanges | **BingX API, OKX API** |
| Database | **PostgreSQL + SQLAlchemy + Alembic** |
| Web server | **Nginx + SSL (Let's Encrypt)** |
| Admin panel | **SQLAdmin** |
| Language | **Python 3.10+** |

---

## 📁 Project Structure

```
vextrBotPy/
├── backend/
│   ├── webhook.py                          # FastAPI entry point
│   ├── tasks.py                            # Celery tasks
│   ├── admin/
│   │   ├── auth.py                         # Admin authentication
│   │   ├── config.py                       # Admin configuration
│   │   └── models.py                       # Admin model views
│   ├── exchange_apis/
│   │   ├── bingx/
│   │   │   ├── router.py
│   │   │   └── services/
│   │   │       ├── create_main_order.py
│   │   │       ├── set_sl_order.py
│   │   │       ├── set_tp_orders.py
│   │   │       ├── move_sl_to_breakeven.py
│   │   │       ├── get_open_positions.py
│   │   │       ├── get_balance.py
│   │   │       └── set_leverage.py
│   │   └── okx/
│   │       ├── router.py
│   │       └── services/
│   │           ├── open_position.py
│   │           ├── set_sl_order.py
│   │           ├── set_tp_order.py
│   │           ├── get_balance.py
│   │           ├── get_symbol_info.py
│   │           ├── set_leverage.py
│   │           └── close_position.py
│   └── utils/
│       ├── signal_shema.py                 # Webhook payload schema
│       └── send_notification.py            # Telegram notifications
├── bot/
│   ├── bot.py                              # Telegram bot entry point
│   ├── instance.py
│   ├── handlers/
│   ├── keyboards/
│   ├── states/
│   └── utils/
├── database/
│   ├── database.py
│   ├── dao/
│   │   └── base.py
│   └── models/
│       ├── users/
│       ├── payments/
│       ├── trades/
│       └── affiliate_applications/
├── alembic/
│   ├── env.py
│   └── versions/
├── config/
│   └── config.py
├── celery_app.py                           # Celery configuration
├── .env
└── requirements.txt
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/alikurb12/vextrBotPy.git
cd vextrBotPy
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and start Redis

```bash
# Ubuntu/Debian
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 5. Create a `.env` file

```env
# Telegram
BOT_TOKEN=your_telegram_bot_token
CRYPTO_BOT_TOKEN=your_crypto_bot_token
GROUP_ID=your_group_id
MODERATOR_GROUP_ID=your_moderator_group_id
SUPPORT_CONTACT=your_support_contact

# YooMoney
YOOMONEY_ACCESS_TOKEN=your_yoomoney_token
YOOMONEY_RECEIVER=your_yoomoney_receiver

# BingX
BINGX_API_URL=https://open-api.bingx.com

# OKX
OKX_FLAG=1

# Exchange settings
LEVERAGE_LEVEL=10

# Database
DB_HOST=localhost
DB_NAME=vextr_db
DB_USER=your_db_user
DB_PASS=your_db_password
DB_PORT=5432

# Admin panel
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_admin_password
SECRET_KEY_ADMIN=your_secret_key
```

### 6. Run database migrations

```bash
alembic upgrade head
```

---

## 🚀 Running

### Start the webhook server

```bash
uvicorn backend.webhook:app --host 0.0.0.0 --port 8000
```

### Start the Celery worker

```bash
PYTHONPATH=. celery -A celery_app worker --loglevel=info --pool=solo
```

### Start the Telegram bot

```bash
python bot/bot.py
```

---

## 🖥️ Production Deployment (Ubuntu/Debian)

Three systemd services are used in production:

| Service | Description |
|---------|-------------|
| `vextr_webhook` | FastAPI webhook server |
| `vextr_celery` | Celery worker for signal processing |
| `vextr_bot` | Telegram bot |

```bash
sudo systemctl start vextr_webhook vextr_celery vextr_bot
sudo systemctl enable vextr_webhook vextr_celery vextr_bot
```

---

## 🌐 Webhook API

### `POST /webhook`

Receives trading signals from TradingView.

**Request body:**

```json
{
  "action": "BUY",
  "symbol": "BTCUSDT.P",
  "price": 65000.0,
  "stop_loss": 63000.0,
  "take_profit_1": 67000.0,
  "take_profit_2": 69000.0,
  "take_profit_3": 72000.0
}
```

**Supported actions:**

| Action | Description |
|--------|-------------|
| `BUY` | Open a long position for all users |
| `SELL` | Open a short position for all users |
| `MOVE_SL` | Move Stop Loss to breakeven for all users |

**Response:**

```json
{
  "message": "Signal queued successfully"
}
```

### `GET /health`

Health check endpoint.

```json
{
  "result": "OK"
}
```

---

## 🔐 Admin Panel

Available at `/admin` — protected by username and password.

Features:
- View and manage users
- Monitor subscriptions
- Track open trades

---

## 🤖 Telegram Bot Features

| Feature | Description |
|---------|-------------|
| Registration | Register with email and exchange selection |
| Subscription | View status and manage payments |
| Promo codes | Apply discount codes |
| Positions | View currently open positions |
| Moderation | Admin tools for user management |

---

## 🧪 Running Tests

```bash
python -m pytest tests/
```
