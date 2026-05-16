from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, func
from sqlalchemy.orm import relationship
from ..database import Base 

class Profile(Base):
	__tablename__="profiles"

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
	display_name = Column(String(255), nullable=True)
	bio = Column(Text, nullable=True)
	avatar_url = Column(Text, nullable=True)
	date_of_birth = Column(DateTime(timezone=True), nullable=True)
	gender = Column(String(20), nullable=True)

	user = relationship("User", back_populates="profile")
