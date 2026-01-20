from sqlalchemy import Integer, String, Column, Float, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from database.database import Base

class Affiliate_Applications(Base):
    __tablename__ = "affiliate_applications"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    photo_url = Column(String)
    email = Column(String)
    full_name = Column(String)
    from_data = Column(JSON)
    submitted_at = Column(DateTime)
    status = Column(String)
    commision_rate = Column(Integer)
    promo_code = Column(Integer)
    discount = Column(Integer)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(String)
    notes = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)