from sqlalchemy import Column, Identity, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from src.config.database import Base


class UserRepository(Base):
    __tablename__ = "user_repository"

    id = Column(Integer, Identity(), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    repo_fullname = Column(String(255))

    user = relationship("User", back_populates="repos")
