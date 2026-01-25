from sqlalchemy import BigInteger ,Integer, String, Column, DateTime, Boolean
from database.database import Base

class Users(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String)
    subscription_end = Column(DateTime)
    subscription_type = Column(String)
    refferal_uuid = Column(String)
    api_key = Column(String)
    secret_key = Column(String)
    exchange = Column(String)
    passphrase = Column(String)
    chat_id = Column(BigInteger)
    email = Column(String)
    terms_accepted = Column(Boolean)
    affirmate_username = Column(String)