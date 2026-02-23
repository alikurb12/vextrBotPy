# 🤖 VextrBot — Automated Trading Signal Bot

An automated trading system that receives signals from TradingView via webhook and opens positions on **BingX** exchange for all registered users. Users are managed and notified through a **Telegram bot**.

---

## ✨ How It Works

```
TradingView Alert
      ↓
POST /webhook  (FastAPI)
      ↓
   BUY / SELL → Open position on BingX for all users
                → Notify users via Telegram
      ↓
   MOVE_SL    → Move Stop Loss to breakeven on BingX
                → Notify users via Telegram
```

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Webhook server | **FastAPI** |
| Telegram bot | **aiogram** |
| Exchange | **BingX API** |
| Database | **SQLAlchemy + Alembic** |
| Language | **Python 3.9+** |

---

## 📁 Project Structure

```
vextrBotPy/
├── backend/
│   ├── webhook.py                          # FastAPI entry point
│   ├── exchange_apis/
│   │   ├── bingx/
│   │   │   ├── router.py                   # BingX main router
│   │   │   └── services/
│   │   │       ├── create_main_order.py
│   │   │       ├── set_sl_order.py
│   │   │       ├── set_tp_orders.py
│   │   │       ├── move_sl_to_breakeven.py
│   │   │       ├── get_open_positions.py
│   │   │       ├── get_balance.py
│   │   │       ├── set_leverage.py
│   │   │       └── ...
│   │   ├── bybit/
│   │   ├── bitget/
│   │   └── okx/
│   ├── services/
│   │   └── services.py
│   └── utils/
│       ├── signal_schema.py                # Webhook payload schema
│       ├── send_notification.py            # Telegram notifications
│       └── utils.py
├── bot/
│   ├── bot.py                              # Telegram bot entry point
│   ├── instance.py                         # Bot instance
│   ├── handlers/
│   │   ├── __init__.py                     # Router registry
│   │   ├── start.py
│   │   ├── registration.py
│   │   ├── main_menu.py
│   │   ├── get_payment.py
│   │   ├── check_payment.py
│   │   ├── process_email.py
│   │   ├── process_promo_code.py
│   │   ├── process_exchange_selection.py
│   │   ├── get_my_positions.py
│   │   ├── my_status.py
│   │   ├── moderation.py
│   │   └── ...
│   ├── keyboards/
│   │   └── keyboards.py
│   ├── states/
│   │   └── register_states.py
│   └── utils/
│       ├── create_check_payment.py
│       └── video_sender.py
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
│   └── versions/                           # Migration files
├── config/
│   └── config.py
├── tests/
│   ├── test_create_main_order.py
│   ├── test_set_sl_order.py
│   ├── test_move_sl_to_breakeven.py
│   └── ...
├── .env
└── requirements.txt
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/vextrBotPy.git
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

### 4. Create a `.env` file

```env
# Telegram
BOT_TOKEN=your_telegram_bot_token

# BingX
BINGX_API_KEY=your_bingx_api_key
BINGX_SECRET_KEY=your_bingx_secret_key

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
```

### 5. Run database migrations

```bash
alembic upgrade head
```

---

## 🚀 Running

### Start the webhook server

```bash
uvicorn backend.webhook:app --host 0.0.0.0 --port 8000
```

### Start the Telegram bot

```bash
python bot/bot.py
```

---

## 🌐 Webhook API

### `POST /webhook`

Receives trading signals from TradingView.

**Request body:**

```json
{
  "action": "BUY",
  "symbol": "BTC-USDT",
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
  "message": "Webhook received successfully"
}
```

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
