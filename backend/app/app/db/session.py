from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

engine_aio = create_async_engine(settings.ASYNC_SQLALCHEMY_DATABASE_URI, echo=True)
async_session = async_sessionmaker(autoflush=False, bind=engine_aio, expire_on_commit=False)
