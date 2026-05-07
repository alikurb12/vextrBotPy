from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


def _make_session():
    from config.config import settings
    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_size=1,
        max_overflow=0,
        pool_reset_on_return="rollback",
    )
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class BaseDao:
    model = None

    @classmethod
    async def get_all(cls, **kwargs):
        async with _make_session()() as session:
            query = select(cls.model).filter_by(**kwargs)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_by_id(cls, model_id: int):
        async with _make_session()() as session:
            query = select(cls.model).filter_by(id=model_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def add(cls, **kwargs):
        async with _make_session()() as session:
            query = insert(cls.model).values(**kwargs)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def delete(cls, model_id: int):
        async with _make_session()() as session:
            query = delete(cls.model).filter_by(model_id=model_id)
            await session.execute(query)
            await session.commit()
