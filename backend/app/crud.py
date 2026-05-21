from sqlalchemy.orm import Session
from sqlalchemy import or_
import uuid
from datetime import datetime, timezone, timedelta

from . import models, schemas
from .utils import hash_password, REFRESH_TOKEN_EXPIRE_DAYS
from .models import User, Profile, UserSession

def create_user(db: Session, user: schemas.UserCreate):
	hashed_password = hash_password(user.password)

	db_user = User(
		email=user.email, 
		fullname=user.fullname, 
		username=user.username,
		password_hash=hashed_password,
		last_login_at=datetime.now(timezone.utc),
	)

	db_profile = Profile(
		display_name = db_user.fullname
	)

	db_user.profile = db_profile

	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	return db_user

def create_oauth_user(db: Session, user: schemas.OAuthUserCreate):

	base_username = user.fullname.lower().replace(" ", "_")  # "krishan_kumar"
	username =	f"{base_username}_{str(uuid.uuid4())[:6]}"
	db_user = User(
		email= user.email,
		fullname=user.fullname,
		username = username,
		provider=user.provider,
		provider_id = user.provider_id,
		password_hash= None,
		is_email_verified=True,
		last_login_at=datetime.now(timezone.utc),
	)

	db_profile = Profile(
		display_name= db_user.fullname
	)
	db_user.profile = db_profile

	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	return db_user

def create_user_session(db: Session, user_session: schemas.UserSession):
	db_session = UserSession(
		user_id = user_session.user_id,
		refresh_token_hash = user_session.refresh_token_hash,
		device_name = user_session.device_name,
		ip_address = user_session.ip_address,
		is_revoked=False,
		expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
	)
	db.add(db_session)
	db.commit()

def delete_user_session(db: Session, user_id: int):
	session = db.query(UserSession)\
		.filter(UserSession.user_id == user_id)\
		.order_by(UserSession.created_at.desc())\
		.first()

def get_user(db: Session, id: int):
	return db.query(User).filter(User.id == id).first()

def get_user_by_email(db: Session, email: str):
	return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
	return db.query(User).filter(User.username == username)

def get_user_by_identifier(db: Session, identifier : str):
	return db.query(User).filter(
		or_(User.email == identifier, 
			User.username == identifier)
		).first()

def get_all_users(db: Session):
	return db.query(User).all()