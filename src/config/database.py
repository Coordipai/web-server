from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.config import DATABASE_URL
from src.config.logger_config import setup_logger, add_daily_file_handler
from src.exceptions.definitions import SQLError

engine = create_engine(DATABASE_URL, echo=False)
session = sessionmaker(bind=engine)

Base = declarative_base()

logger = setup_logger(__name__)
add_daily_file_handler(logger)


def initialize_database():
    logger.info("⏳ Initializing Database")
    logger.info("🚨 Dropping all tables... (only for dev mode)")

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    logger.info("✅ Database Initializing complete!")


async def get_db():
    """
    Create SQLAlchemy Sessoin
    """
    db = session()
    try:
        yield db
    except:
        raise SQLError()
    finally:
        db.close()
