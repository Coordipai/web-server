from sqlalchemy import JSON, Column, ForeignKey, Identity, Integer, String
from sqlalchemy.orm import relationship

from src.config.database import Base


class IssueRescheduling(Base):
    __tablename__ = "issue_rescheduling"

    id = Column(Integer, Identity(), primary_key=True, index=True)
    issue_number = Column(Integer)
    requester = Column(Integer)
    reason = Column(String(501))
    new_iteration = Column(Integer)
    new_assignees = Column(JSON)
    project_id = Column(Integer, ForeignKey("project.id"))

    project = relationship("Project", back_populates="issue_rescheduling_list")
