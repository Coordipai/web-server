from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Identity, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.config.database import Base

class IssueRescheduleRequest(Base):
    __tablename__ = "issue_reschedule_request"

    id = Column(Integer, Identity(), primary_key=True, index=True)
    issue_num = Column(Integer, nullable=False, index=True)  # GitHub 이슈 번호 또는 내부 식별자
    reason = Column(String(1000), nullable=False)  # 변경 요청 사유
    assignee = Column(Integer, ForeignKey("user.id"))  # 요청 시점의 이슈 담당자
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    status = Column(String(50), default="pending")  # 요청 상태 (예: pending, approved, rejected)

    # 관계 설정
    user = relationship("User", back_populates="reschedule_requests")
