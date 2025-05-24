from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Enum, Identity, Integer, String
from sqlalchemy.orm import relationship

from src.config.database import Base
from src.user.schemas import UserCategory


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, Identity(), primary_key=True, index=True)
    name = Column(String(255))
    discord_id = Column(String(30), unique=True)
    github_id = Column(Integer, unique=True, index=True)
    github_name = Column(String(255), unique=True, index=True)
    github_access_token = Column(String(255))
    category = Column(Enum(UserCategory))
    career = Column(String(501))
    profile_img = Column(String(255))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    stat = Column(JSON)

    members = relationship("ProjectUser", back_populates="user")
    repos = relationship("UserRepository", back_populates="user")
