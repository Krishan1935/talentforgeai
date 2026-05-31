from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, func, Date
from sqlalchemy.orm import relationship
from app.config import Base 
from datetime import datetime, UTC

class Experience(Base):
    
    __tablename__="experiences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    institution = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_present = Column(Boolean, default=False, nullable=False)
    role = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    user = relationship("User", back_populates="experiences")