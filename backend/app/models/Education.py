from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, func, Date
from sqlalchemy.orm import relationship
from ..config import Base 
from datetime import datetime, UTC


class Education(Base):
    __tablename__ = "educations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=True)
    field_of_study = Column(String(255), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    grade = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default= datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), onupdate= datetime.now(UTC))
    
    user = relationship("User", back_populates="educations")