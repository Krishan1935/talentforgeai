from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, func
from sqlalchemy.orm import relationship
from ..database import Base 

class User(Base):
	__tablename__ = "users"

	id=Column(Integer, primary_key=True, index=True)
	fullname=Column(String(255), index=True, nullable=False)
	username=Column(String(255), unique=True, index=True, nullable=False)
	email=Column(String(255), unique=True, index=True, nullable=False)
	password_hash=Column(String(255), nullable=False)

	status=Column(String(50), default='pending')
	is_active=Column(Boolean, default=False)
	role=Column(String(100), default='user', nullable=False)

	is_email_verified=Column(Boolean, default=False)
	is_phone_verified=Column(Boolean, default=False)

	last_login_at=Column(DateTime(timezone=True), nullable=True)
	last_login_ip=Column(String(45), nullable=True)
	locked_until=Column(DateTime(timezone=True), nullable=True)

	password_changed_at=Column(DateTime(timezone=True),nullable=True)
	password_reset_token=Column(Text, nullable=True)
	password_reset_expires_at=Column(DateTime(timezone=True), nullable=True)

	created_at=Column(DateTime(timezone=True), server_default=func.now())
	updated_at=Column(DateTime(timezone=True), server_default=func.now())
	deleted_at=Column(DateTime(timezone=True))

	profile = relationship(
		"Profile",
		back_populates="users",
		uselist=False,
		cascade="all, delete-orphan"
	)