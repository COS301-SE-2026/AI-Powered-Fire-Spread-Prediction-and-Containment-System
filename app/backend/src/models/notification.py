import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from app.backend.db import Base
from app.backend.src.enums.notification_type import NotificationType
from app.backend.src.enums.severity import Severity


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fire_report_id = Column(
        String,
        ForeignKey("fire_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(Enum(NotificationType), nullable=False)
    severity = Column(Enum(Severity), nullable=False)
    message = Column(String, nullable=False)
    fire_location = Column(
        String, nullable=False
    )  # snapshots - frozen at creation time so history doesn't shift if fire report or user location changes later
    distance = Column(Float, nullable=False)
    read = Column(Boolean, default=False, nullable=False)
    time = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    fire_report = relationship("FireReports")
