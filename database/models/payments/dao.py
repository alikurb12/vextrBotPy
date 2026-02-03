from dao.base import BaseDao
from database.models.payments.models import Payments
from database.database import async_session_maker
from sqlalchemy import select, delete

class PaymentsDAO(BaseDao):
    model = Payments

    @classmethod
    async def get_by_id(cls, invoice_id):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(invoice_id = invoice_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    @classmethod
    async def delete(cls, invoice_id : int):
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(invoice_id = invoice_id)
            await session.execute(query)
            await session.commit()