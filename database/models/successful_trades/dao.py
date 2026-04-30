from database.dao.base import BaseDao
from database.models.successful_trades.models import SuccessfulTrades
from database.database import async_session_maker
from sqlalchemy import select

class SuccessfulTradesDAO(BaseDao):
    model = SuccessfulTrades

    @classmethod
    async def add(cls, **kwargs):
        async with async_session_maker() as session:
            obj = cls.model(**kwargs)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    @classmethod
    async def get_all_for_user(cls, user_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(user_id=user_id)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_all(cls):
        async with async_session_maker() as session:
            query = select(cls.model)
            result = await session.execute(query)
            return result.scalars().all()
