from sqlalchemy import BIGINT, String, Column, DateTime, Float, ForeignKey, Integer
from database.database import Base

class SuccessfulTrades(Base):
    __tablename__ = "successful_trades"
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, ForeignKey("users.user_id"))
    trade_id = Column(BIGINT, ForeignKey("trades.trade_id"))
    
    # Параметры сделки
    symbol = Column(String)
    side = Column(String)          # long / short
    exchange = Column(String)
    timeframe = Column(String)
    entry_price = Column(Float)
    stop_loss = Column(Float)
    take_profit_1 = Column(Float)
    take_profit_2 = Column(Float)
    take_profit_3 = Column(Float)
    quantity = Column(Float)
    
    # Результат
    tps_hit = Column(Integer)      # сколько TP сработало (1, 2 или 3)
    pnl = Column(Float)
    pnl_percent = Column(Float)
    created_at = Column(DateTime)  # время открытия
    closed_at = Column(DateTime)   # время закрытия
    
    # Технические индикаторы в момент сигнала
    rsi = Column(Float)
    ema_fast = Column(Float)
    ema_slow = Column(Float)
    volume = Column(Float)
    atr = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    bb_upper = Column(Float)
    bb_lower = Column(Float)
    
    # Доп. признаки для ML
    sl_distance_pct = Column(Float)   # % расстояние от входа до SL
    tp1_distance_pct = Column(Float)  # % расстояние от входа до TP1
    risk_reward = Column(Float)       # соотношение риск/прибыль
    
    def __str__(self):
        return f"{self.symbol} {self.side} pnl={self.pnl}"
