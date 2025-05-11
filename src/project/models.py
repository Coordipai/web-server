from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Identity, Integer, String
from sqlalchemy.orm import relationship

from src.config.database import Base


class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, Identity(), primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    owner = Column(Integer, index=True)
    repo_fullname = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    sprint_unit = Column(Integer)
    discord_channel_id = Column(String(50))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    design_doc_paths = Column(JSON)

    members = relationship(
        "ProjectUser", back_populates="project", cascade="all, delete-orphan"
    )
    issue_rescheduling_list = relationship(
        "IssueRescheduling", back_populates="project", cascade="all, delete-orphan"
    )
