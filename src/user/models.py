from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Identity, Integer, String
from src.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, Identity(), primary_key=True, index=True)
    name = Column(String(255))
    discord_id = Column(Integer, unique=True, index=True)
    github_id = Column(Integer, unique=True, index=True)
    github_name = Column(String(255))
    github_access_token = Column(String(255))
    category = Column(String(255))
    career = Column(String(255))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
