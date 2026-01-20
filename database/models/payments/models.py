from sqlalchemy import Integer, String, Column, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Payments(Base):
    __tablename__ = "payments"

    invoice_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    affiliate_id = Column(Integer, ForeignKey("affiliate_applications.id"))
    amount = Column(Float)
    currency = Column(String)
    status = Column(String)
    tadiff_id = Column(String)
    payment_method = Column(String)
    yoomoney_label = Column(String)

    user = relationship("Users", backref="payments")
    affiliate = relationship("Affiliate_Applications", backref="payments")