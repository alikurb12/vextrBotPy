from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config.config import settings


class Base(DeclarativeBase):
    pass


def get_engine():
    return create_async_engine(settings.DATABASE_URL)


def get_session_maker(engine=None):
    if engine is None:
        engine = get_engine()
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


engine = get_engine()
async_session_maker = get_session_maker(engine)