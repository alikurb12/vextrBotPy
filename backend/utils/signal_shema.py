from pydantic import BaseModel
from typing import Optional

class SignalSchema(BaseModel):
    action: str
    symbol: str
    price: float
    stop_loss: float
    take_profit_1: Optional[float] = None
    take_profit_2: Optional[float] = None
    take_profit_3: Optional[float] = None
    rsi: Optional[float] = None
    ema_fast: Optional[float] = None
    ema_slow: Optional[float] = None
    volume: Optional[float] = None
    atr: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_lower: Optional[float] = None
    timeframe: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "BUY сигнал",
                    "value": {
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
                },
                {
                    "summary": "SELL сигнал",
                    "value": {
                        "action": "SELL",
                        "symbol": "BTCUSDT.P",
                        "price": 65000.0,
                        "stop_loss": 67000.0,
                        "take_profit_1": 63000.0,
                        "take_profit_2": 61000.0,
                        "take_profit_3": 58000.0,
                        "rsi": 38.2,
                        "ema_fast": 65200.0,
                        "ema_slow": 66100.0,
                        "volume": 980.3,
                        "atr": 820.0,
                        "macd": -110.2,
                        "macd_signal": -85.1,
                        "timeframe": "60"
                    }
                },
                {
                    "summary": "MOVE_SL сигнал",
                    "value": {
                        "action": "MOVE_SL",
                        "symbol": "BTCUSDT.P",
                        "price": 65000.0,
                        "stop_loss": 65000.0
                    }
                }
            ]
        }
    }
