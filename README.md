# 🤖 VextrBot — Automated Trading Signal Bot

An automated trading system that receives signals from TradingView via webhook and opens positions on **BingX** and **OKX** exchanges for all registered users. Users are managed and notified through a **Telegram bot**.

---

## ✨ How It Works

```
TradingView Alert (with RSI, MACD, ATR, EMA, Volume)
      ↓
POST /webhook  (FastAPI)
      ↓
Signal added to Redis queue
      ↓
Celery Worker processes one by one
      ↓
   BUY / SELL → Sync trades with exchange (close stale DB records)
                → Open position on BingX + OKX for all active users
                → Notify users via Telegram
      ↓
   MOVE_SL    → Save trade to ML dataset (successful_trades)
                → Move Stop Loss to breakeven on BingX + OKX
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
| Charts & Analytics | **Matplotlib** |
| Web server | **Nginx + SSL (Let's Encrypt)** |
| Admin panel | **SQLAdmin** |
| Language | **Python 3.10+** |

---

## 🆕 New Features

### ⏸ Trading Pause
Users can pause and resume auto-trading directly from the Telegram bot. When paused, no new positions will be opened for that user.

### 📊 Statistics & Charts
The bot generates personal trading statistics including:
- Total trades, win rate, profit/loss
- Best and worst trades
- Equity curve chart (cumulative P&L over time)
- P&L bar chart per trade

### 🔄 Trade Synchronization
Automatically syncs open trades in the database with real positions on the exchange. Stale records (positions that no longer exist on the exchange) are automatically closed in the DB.

### 🧠 ML Dataset Collection
Every time a MOVE_SL signal is received (meaning TP1 was hit), the trade is saved to a `successful_trades` table with full technical indicator context for future ML model training:
- RSI, MACD, ATR, EMA Fast/Slow, Volume
- SL/TP distances in %, Risk/Reward ratio
- Timeframe, entry price, side, exchange

---

## 📁 Project Structure

```
vextrBotPy/
├── backend/
│   ├── webhook.py                          # FastAPI entry point
│   ├── tasks.py                            # Celery tasks
│   ├── admin/
│   │   ├── auth.py
│   │   ├── config.py
│   │   └── models.py
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
│   │           ├── move_sl_to_breakeven.py
│   │           ├── get_balance.py
│   │           ├── get_open_positions.py
│   │           ├── get_symbol_info.py
│   │           ├── set_leverage.py
│   │           └── close_position.py
│   ├── services/
│   │   ├── sync_trades.py                  # Sync DB trades with exchange
│   │   └── save_successful_trade.py        # Save TP1+ trades to ML dataset
│   └── utils/
│       ├── signal_shema.py                 # Webhook payload schema (with indicators)
│       └── send_notification.py
├── bot/
│   ├── bot.py
│   ├── instance.py
│   ├── handlers/
│   │   ├── start.py
│   │   ├── main_menu.py
│   │   ├── my_status.py
│   │   ├── statistics.py                   # 📊 Statistics & charts
│   │   ├── toggle_trading.py               # ⏸ Pause/resume trading
│   │   ├── sync_trades.py                  # 🔄 Manual sync
│   │   ├── get_my_positions.py
│   │   ├── registration.py
│   │   ├── moderation.py
│   │   └── ...
│   ├── keyboards/
│   └── states/
├── database/
│   ├── database.py
│   ├── dao/
│   │   └── base.py
│   └── models/
│       ├── users/
│       ├── payments/
│       ├── trades/
│       ├── successful_trades/              # 🧠 ML dataset table
│       └── affiliate_applications/
├── alembic/
│   ├── env.py
│   └── versions/
├── config/
│   └── config.py
├── celery_app.py
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
| `vextr_api` | FastAPI webhook server |
| `vextr_celery` | Celery worker for signal processing |
| `vextr_bot` | Telegram bot |

```bash
sudo systemctl start vextr_api vextr_celery vextr_bot
sudo systemctl enable vextr_api vextr_celery vextr_bot
```

---

## 🌐 Webhook API

### `POST /webhook`

Receives trading signals from TradingView. Supports technical indicators for ML dataset collection.

**Request body:**

```json
{
  "action": "BUY",
  "symbol": "BTCUSDT.P",
  "price": 65000.0,
  "stop_loss": 63000.0,
  "take_profit_1": 67000.0,
  "take_profit_2": 69000.0,
  "take_profit_3": 72000.0,
  "rsi": 62.5,
  "ema_fast": 64800.0,
  "ema_slow": 63500.0,
  "volume": 1250.5,
  "atr": 850.0,
  "macd": 120.5,
  "macd_signal": 95.3,
  "timeframe": "60"
}
```

**Supported actions:**

| Action | Description |
|--------|-------------|
| `BUY` | Open a long position for all active users |
| `SELL` | Open a short position for all active users |
| `MOVE_SL` | Move Stop Loss to breakeven + save to ML dataset |

### `GET /health`

```json
{
  "result": "OK",
  "service": "vextr_api"
}
```

---

## 🔐 Admin Panel

Available at `/admin` — protected by username and password.

Features:
- View and manage users
- Monitor subscriptions and payments
- Track open and closed trades
- View ML dataset (successful trades)

---

## 🤖 Telegram Bot Features

| Feature | Description |
|---------|-------------|
| Registration | Register with email and exchange selection |
| Subscription | View status and manage payments |
| Promo codes | Apply discount codes |
| My Status | View subscription info and balance |
| Positions | View currently open positions |
| **Statistics** | View win rate, P&L, equity curve chart |
| **Pause Trading** | Pause/resume auto-trading |
| **Sync Positions** | Sync DB with real exchange positions |
| Moderation | Admin tools for user management |

---

## 🧠 ML Dataset

The `successful_trades` table accumulates data for training a prediction model. A record is saved every time TP1 is hit (MOVE_SL signal received).

**Features collected:**

| Feature | Description |
|---------|-------------|
| `rsi` | RSI at signal time |
| `macd` / `macd_signal` | MACD values |
| `atr` | Volatility (ATR) |
| `ema_fast` / `ema_slow` | EMA values |
| `volume` | Candle volume |
| `sl_distance_pct` | SL distance from entry in % |
| `tp1_distance_pct` | TP1 distance from entry in % |
| `risk_reward` | Risk/reward ratio |
| `side` | long / short |
| `timeframe` | Signal timeframe |
| `tps_hit` | Number of TPs hit (1, 2 or 3) |

---

## 🧪 Running Tests

```bash
python -m pytest tests/
```
