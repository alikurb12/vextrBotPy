from sqlalchemy import Integer, String, Column, DateTime, Boolean
from sqlalchemy.orm import relationship
from database.database import Base

class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    subscription_end = Column(DateTime)
    subscription_type = Column(String)
    refferal_uuid = Column(String)
    api_key = Column(String)
    secret_key = Column(String)
    exchange = Column(String)
    passphrase = Column(String)
    chat_id = Column(Integer)
    email = Column(String)
    terms_accepted = Column(Boolean)
    affirmate_username = Column(String)