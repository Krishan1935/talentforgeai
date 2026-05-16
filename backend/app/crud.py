from sqlalchemy.orm import Session

from . import models, schemas
from .utils import hash_password
from .models import User, Profile

def create_user(db: Session, user: schemas.UserCreate):
	hashed_password = hash_password(user.password)

	db_user = User(
		email=user.email, 
		fullname=user.fullname, 
		username=user.username,
		password_hash=hashed_password
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

def get_all_users(db: Session):
	return db.query(User)