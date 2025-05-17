from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config.config import DATABASE_URL
from src.config.logger_config import setup_logger
from src.response.error_definitions import SQLError

engine = create_engine(DATABASE_URL, echo=False)
session = sessionmaker(bind=engine)

Base = declarative_base()

logger = setup_logger(__name__)


def initialize_database():
    logger.info("⏳ Initializing Database")
    logger.info("🚨 Dropping all tables... (only for dev mode)")

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    logger.info("✅ Database Initializing complete!")


def get_db():
    """
    Create SQLAlchemy Sessoin
    """
    db = session()
    try:
        yield db
    except SQLAlchemyError as e:
        raise SQLError(detail=str(e))
    finally:
        db.close()
