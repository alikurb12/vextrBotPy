from dao.base import BaseDao
from database.models.trades.models import Trades
from database.database import async_session_maker
from sqlalchemy import select, delete

class UsersDAO(BaseDao):
    model = Trades

    @classmethod
    async def get_by_id(cls, trade_id):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(trade_id = trade_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        
    @classmethod
    async def delete(cls, trade_id : int):
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(trade_id = trade_id)
            await session.execute(query)
            await session.commit()