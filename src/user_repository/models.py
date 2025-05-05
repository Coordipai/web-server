from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from src.config.database import Base


class UserRepository(Base):
    __tablename__ = "user_repository"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    repo_name = Column(String(255))

    user = relationship("User", back_populates="repos")
