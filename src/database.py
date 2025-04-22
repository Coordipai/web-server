from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL


engine = create_engine(DATABASE_URL, echo=True)
session = sessionmaker(bind=engine)

Base = declarative_base()


def initialize_database():
    print("⏳ Initializing Database")
    print("🚨 Dropping all tables... (only for dev mode)")

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("✅ Database Initializing complete!")


async def get_db():
    """
    Create SQLAlchemy Sessoin
    """
    db = session()
    try:
        yield db
    except:
        db.close()
