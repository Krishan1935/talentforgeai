from sqlalchemy.orm import Session

from . import models, schemas
from .utils import hash_password

def create_user(db: Session, user: schemas.UserCreate):
	hashed_password = hash_password(user.password)

	db_user = models.User(
		email=user.email, 
		name=user.name, 
		password=hashed_password
	)

	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	return db_user

def get_user(db: Session, id: int):
	return db.query(models.User).filter(models.User.id == id).first()

def get_user_by_email(db: Session, email: str):
	return db.query(models.User).filter(models.User.email == email).first()