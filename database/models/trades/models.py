from sqlalchemy import BIGINT, Integer, String, Column, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Trades(Base):
    __tablename__ = "trades"

    trade_id = Column(BIGINT, primary_key=True)
    user_id = Column(BIGINT, ForeignKey("users.user_id"))
    order_id = Column(String)
    symbol = Column(String)
    side = Column(String)
    position_side = Column(String)
    quantity = Column(Float)
    entry_price = Column(Float)
    stop_loss = Column(Float)
    take_profit_1 = Column(Float)
    take_profit_2 = Column(Float)
    take_profit_3 = Column(Float)
    sl_order_id = Column(String)
    tp1_order_id = Column(String)
    tp2_order_id = Column(String)
    tp3_order_id = Column(String)
    status = Column(String)
    created_at = Column(DateTime)
    exchange = Column(String)

    user = relationship("Users", backref="trades")