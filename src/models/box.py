from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.db.database import Base

class Box(Base):
    __tablename__ = "boxes"

    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True, nullable=False)
    owner_token = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    feedbacks = relationship("Feedback", back_populates="box", cascade="all, delete-orphan")