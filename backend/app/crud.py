from sqlalchemy.orm import Session
from sqlalchemy import or_
import uuid
from datetime import datetime, timezone

from . import models, schemas
from .utils import hash_password
from .models import User, Profile

def create_user(db: Session, user: schemas.UserCreate, ip: str):
	hashed_password = hash_password(user.password)

	db_user = User(
		email=user.email, 
		fullname=user.fullname, 
		username=user.username,
		password_hash=hashed_password,
		last_login_at=datetime.now(timezone.utc),
		last_login_ip=ip
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
		last_login_ip = user.ip,
	)

	db_profile = Profile(
		display_name= db_user.fullname
	)
	db_user.profile = db_profile

	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	return db_user

def update_last_login_info(db: Session, user, login_info: LoginInfo):
	user.last_login_at = login_info.last_login_at
	user.last_login_ip = login_info.last_login_ip

	db.add(user)
	db.commit()
	db.refresh(user)
	return user

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