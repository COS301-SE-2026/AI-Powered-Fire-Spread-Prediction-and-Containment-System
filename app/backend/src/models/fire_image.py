from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datatime, timezone
import uuid
from db import Base

class Fire_Image(Base):
    __tablename__ = "fire_images"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String, ForeignKey("fire_reports.id"), nullable=False, index=True)
    object_key = Column(String, nullable=False, unique=True)
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datatime.now(timezone.utc))
    
    user = relationship("User")
    fire_report = relationship("FireReports", backref="fire_image")