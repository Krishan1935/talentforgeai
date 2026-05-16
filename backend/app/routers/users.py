from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging
from argon2.exceptions import VerifyMismatchError, InvalidHashError


from ..config import get_db
from .. import schemas, models, crud
from ..utils import create_access_token, create_refresh_token, verify_password
from ..schemas import UserResponse, UserCreate, AuthResponse, AuthBase

router = APIRouter()

logger = logging.getLogger(__name__)

REFRESH_TOKEN_COOKIE_NAME = 'talentforge_refresh_token'

@router.post("/register", response_model=AuthResponse)
def register(response: Response, user: UserCreate, db: Session=Depends(get_db)):
	try:
		user = crud.create_user(db, user)
	
	except IntegrityError as e:
		db.rollback()

		logger.warning("Registration conflict: %s", e.orig)
		raise HTTPException(
			status_code=409,
			detail="A user with this email or username already exists"
		)

	try:
		data = {
			"id": user.id,
			"email": user.email,
			"username": user.username
		}

		access_token = create_access_token(data)
		refresh_token = create_refresh_token(data)

	except Exception as e:
		logger.exception("Token Generation Failed")
		raise HTTPException(
			status_code=500,
			detail="Account created succesfully, but automatic login failed. Please log in manually"
		)

	response.set_cookie(key='talentforge_refresh_token', value=refresh_token, httponly=True, secure=False, max_age=30*24*60*60)

	return {
		"user": user,
		"access_token": access_token,
		"token_type": "bearer"
	}


@router.post("/login", response_model=AuthResponse)
def login(response: Response, user: AuthBase, db: Session=Depends(get_db)):
	try:
		db_user = crud.get_user_by_identifier(db, user.identifier)

		if not db_user:
			raise HTTPException(
				status_code=404,
				detail="Username or email not found"
			)
	except IntegrityError:
		raise HTTPException(
			status_code=500,
			detail="Internal Server Error"
		)

	password = user.password
	hashed_password = db_user.password_hash 

	try:
		verify_password(password, hashed_password)
	except (VerifyMismatchError, InvalidHashError):
		raise HTTPException(
			status_code=401,
			detail="Invalid Credentials"
		)

	data = {
		'id': db_user.id,
		'email':db_user.email,
		'username': db_user.username
	}
	access_token = create_access_token(data)
	refresh_token = create_refresh_token(data)

	response.set_cookie(key=REFRESH_TOKEN_COOKIE_NAME, value=refresh_token, httponly=True, secure=False, max_age=30*24*60*60)
	return {
		"user":db_user,
		"access_token": access_token,
		"token_type": "bearer"
	}


@router.get("/get-all", response_model=list[UserResponse])
def fetch_all(response: Response, db: Session=Depends(get_db)):
	userList = crud.get_all_users(db)
	return userList