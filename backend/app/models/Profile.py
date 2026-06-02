from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, func, ARRAY
from sqlalchemy.orm import relationship
from ..config import Base 

class Profile(Base):
	__tablename__="profiles"

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
	display_name = Column(String(255), nullable=True)
	bio = Column(Text, nullable=True)
	avatar_url = Column(Text, nullable=True)
	date_of_birth = Column(DateTime(timezone=True), nullable=True)
	gender = Column(String(20), nullable=True)
	profile_progress = Column(Integer, default=0)
	github_link = Column(String(255), nullable=True)
	linkedin_link = Column(String(255), nullable=True)
	skills = Column(ARRAY(String(100)), nullable=True)
	user = relationship("User", back_populates="profile")
