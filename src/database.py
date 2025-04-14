from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL


engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


async def initialize_database():
    print("⏳ Initializing Database")
    print("🚨 Dropping all tables... (only for dev mode )")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Database Initialzing complete!")


async def get_db():
    """
    Create SQLAlchemy Sessoin
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
