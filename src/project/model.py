from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Identity, Integer, String
from src.database import Base


class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, Identity(), primary_key=True, index=True)
    name = Column(String(255))
    repo_name = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    sprint_unit = Column(Integer)
    discord_channel_id = Column(Integer, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
