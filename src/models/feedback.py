from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.db.database import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True)
    box_id = Column(Integer, ForeignKey("boxes.id"), nullable=False)
    text = Column(String, nullable=False)
    status = Column(String, nullable=False, default="approved")
    moderation_notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    box = relationship("Box", back_populates="feedbacks")
    replies = relationship("Reply", back_populates="feedback", cascade="all, delete-orphan")