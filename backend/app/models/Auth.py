from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, func
from sqlalchemy.orm import relationship
from ..config import Base 

class PasswordResetToken(Base):
	__tablename__="password_reset_tokens"

	id = Column(Integer, primary_key=True,index=True)
	user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	token_hash = Column(String(255), nullable=False)
	created_at = Column(DateTime, default=func.now())
	expires_at = Column(DateTime, nullable=False)
	used = Column(Boolean, default=False)

	user = relationship("User")