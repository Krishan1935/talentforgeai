from sqlalchemy.orm import Session
from sqlalchemy import or_, delete, select, func
import uuid
from datetime import datetime, timezone, timedelta

from app import models, schemas
from app.utils import hash_password, REFRESH_TOKEN_EXPIRE_DAYS
from app.models import User, Profile, UserSession, PasswordResetToken

def create_user(db: Session, user: schemas.UserCreate):
	hashed_password = hash_password(user.password)

	db_user = User(
		email=user.email, 
		fullname=user.fullname, 
		username=user.username,
		password_hash=hashed_password,
		last_login_at=datetime.utcnow(),
		provider="local"
	)

	db_profile = Profile(
		display_name = db_user.fullname
	)

	db_user.profile = db_profile

	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	return db_user

def get_user(db: Session, id: int):
	return db.query(User).filter(User.id == id).first()

def get_user_by_email(db: Session, email: str):
	return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
	return db.query(User).filter(User.username == username).first()

def get_user_by_identifier(db: Session, identifier : str):
	return db.query(User).filter(
		or_(User.email == identifier, 
			User.username == identifier)
		).first()

def get_all_users(db: Session):
	return db.query(User).all()

