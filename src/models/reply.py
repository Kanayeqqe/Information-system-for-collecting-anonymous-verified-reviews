from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.db.database import Base

class Reply(Base):
    __tablename__ = "replies"

    id = Column(Integer, primary_key=True)
    feedback_id = Column(Integer, ForeignKey("feedbacks.id"), nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    feedback = relationship("Feedback", back_populates="replies")