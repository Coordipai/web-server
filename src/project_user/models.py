from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from src.config.database import Base


class ProjectUser(Base):
    __tablename__ = "project_user"

    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    role = Column(String(50))

    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="members")
