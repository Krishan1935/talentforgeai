from sqlalchemy import Column, Integer, Text, String, Date, DateTime, ForeignKey, ARRAY, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from app.config import Base

class Project(Base):

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    project_url = Column(String(255), nullable=True)
    skills_used = Column(ARRAY(String(100)), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    institution = Column(String(255), nullable=True)
    is_ongoing = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="projects")