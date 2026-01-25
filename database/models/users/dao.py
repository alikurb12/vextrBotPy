from dao.base import BaseDao
from database.models.users.models import Users
from database.database import async_session_maker
from sqlalchemy import select, delete

class UsersDAO(BaseDao):
    model = Users

    @classmethod
    async def get_by_id(cls, user_id : int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(user_id = user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    @classmethod
    async def delete(cls, user_id : int):
         async with async_session_maker() as session:
            user = await cls.get_by_id(user_id)
            if not user:
                raise ValueError(f"Пользователь с ID {user_id} не найден")
            
            query = delete(cls.model).where(cls.model.user_id == user_id)
            result = await session.execute(query)
            await session.commit()
            
            return result.rowcount

    @classmethod
    async def add_or_update(cls, **kwargs):
        user_id = kwargs.get("user_id")
        if user_id:
            existing_user = await cls.get_by_id(user_id = user_id)
            if existing_user:
                for key, value in kwargs.items():
                    setattr(existing_user, key, value)
                return existing_user
        
        return await cls.add(**kwargs)