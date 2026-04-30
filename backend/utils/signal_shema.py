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
    
    rsi: Optional[float] = None          # RSI (14)
    ema_fast: Optional[float] = None     # EMA быстрая (например 9)
    ema_slow: Optional[float] = None     # EMA медленная (например 21)
    volume: Optional[float] = None       # Объём свечи
    atr: Optional[float] = None          # ATR (волатильность)
    macd: Optional[float] = None         # MACD линия
    macd_signal: Optional[float] = None  # MACD сигнальная
    bb_upper: Optional[float] = None     # Bollinger Bands верхняя
    bb_lower: Optional[float] = None     # Bollinger Bands нижняя
    timeframe: Optional[str] = None      # Таймфрейм сигнала (1h, 4h и т.д.)