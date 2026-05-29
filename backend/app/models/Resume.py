from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, func, Date
from sqlalchemy.orm import relationship
from ..config import Base 

class Resume(Base):
    __tablename__="resumes"

    id = Column(Integer, primary_key=True,index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title = Column(String(255), nullable=False)
    file_url = Column(String(255), nullable=False)
    is_primary = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="resumes")