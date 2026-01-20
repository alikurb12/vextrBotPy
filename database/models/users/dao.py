from dao.base import BaseDao
from database.models.users.models import Users
from database.database import async_session_maker
from sqlalchemy import select

class UsersDAO(BaseDao):
    model = Users

    @classmethod
    async def get_by_id(cls, user_id):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(user_id = user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()