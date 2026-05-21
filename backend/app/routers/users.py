from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from sqlalchemy import func
from datetime import datetime, timezone

from ..config import get_db
from .. import schemas, models, crud
from ..utils import create_access_token, create_refresh_token, verify_password, hash_refresh_token
from ..schemas import UserResponse, UserCreate, AuthResponse, AuthBase ,UserSession, APIResponse

router = APIRouter()

logger = logging.getLogger(__name__)

REFRESH_TOKEN_COOKIE_NAME = 'talentforge_refresh_token'

@router.post("/register", response_model=APIResponse)
def register(request: Request, response: Response, user: UserCreate, db: Session=Depends(get_db)):
	try:
		ip = request.client.host if request.client else None
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
		refresh_token_hash = hash_refresh_token(refresh_token)

		device_name = request.headers.get("X-Device-Name")

		crud.create_user_session(db, UserSession(
			user_id=user.id,
			refresh_token_hash=refresh_token_hash,
			device_name=device_name,
			ip_address=ip
		))
	except Exception as e:
		logger.exception("Token Generation Failed")
		
		raise HTTPException(
			status_code=500,
			detail="Account created succesfully, but automatic login failed. Please log in manually"
		)

	response.set_cookie(key='talentforge_refresh_token', value=refresh_token, httponly=True, secure=False, max_age=30*24*60*60)

	return APIResponse(
		success=True,
		message="Account Created Succesfully",
		data=AuthResponse(user=user, access_token=access_token, token_type="bearer")
	)


@router.post("/login", response_model=APIResponse)
def login(request: Request, response: Response, user: AuthBase, db: Session=Depends(get_db)):

	db_user = crud.get_user_by_identifier(db, user.identifier)
	ip = request.client.host if request.client else None

	if not db_user:
		raise HTTPException(
			status_code=404,
			detail="Username or email not found"
		)

	if db_user.provider == 'google':
		raise HTTPException(
			status_code=400,
			detail="This account was created using Google Sign-In. Please continue with Google."
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
	refresh_token_hash = hash_refresh_token(refresh_token)

	device_name = request.headers.get("X-Device-Name")

	crud.create_user_session(db, UserSession(
		user_id=db_user.id,
		refresh_token_hash=refresh_token_hash,
		device_name=device_name,
		ip_address=ip
	))
	db_user.last_login_at = datetime.now(timezone.utc)
	db.commit()
	db.refresh(db_user)

	response.set_cookie(key=REFRESH_TOKEN_COOKIE_NAME, value=refresh_token, httponly=True, secure=False, max_age=30*24*60*60)

	return APIResponse(
		success=True,
		message="Logged In Succesfully",
		data=AuthResponse(user=db_user, access_token=access_token, token_type="bearer")
	)


@router.get("/get-all", response_model=list[UserResponse])
def fetch_all(response: Response, db: Session=Depends(get_db)):
	userList = crud.get_all_users(db)
	return userList