from fastapi import APIRouter, Depends, HTTPException, Response, Request, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from sqlalchemy import func
from datetime import datetime, timezone
import uuid

from app.config import get_db
from app.config import redis_client
from app.services import redis
# from app import schemas, models
import app.schemas, app.models
from app.services import crud
from app.utils import create_access_token, create_refresh_token, verify_password, hash_refresh_token,get_current_user
from app.schemas import UserResponse, UserCreate, AuthResponse, AuthBase ,UserSession, APIResponse, TokenData

router = APIRouter()

logger = logging.getLogger(__name__)

REFRESH_TOKEN_COOKIE_NAME = 'talentforge_refresh_token'

@router.post("/register", response_model=APIResponse)
def register(request: Request, response: Response, user: UserCreate, db: Session=Depends(get_db)):
	try:
		ip = request.client.host if request.client else None
		existing_user = crud.get_user_by_email(db, user.email)

		if existing_user:
			return JSONResponse(
				status_code=409,
				content=jsonable_encoder(APIResponse(
					success=False,
					message="A user with this email or username already exists",
					data=None
				))
			)
		verified = redis_client.get(f"verified:{user.email}")

		if not verified:
			return JSONResponse(
				status_code=403,
				content=jsonable_encoder(APIResponse(
					success=False,
					message="Please verify your email first"
				))
			)
		user = crud.create_user(db, user)

		redis_client.delete(f"verified:{user.email}")
	
	except IntegrityError as e:
		db.rollback()

		logger.warning("Registration conflict: %s", e.orig)
		return JSONResponse(
			status_code=409,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="A user with this email or username already exists",
				data=None
			))
		)

	try:
		session_id = str(uuid.uuid4())
		data = {
			"id": user.id,
			"email": user.email,
			"username": user.username,
			"session_id":session_id
		}

		access_token = create_access_token(data)
		refresh_token = create_refresh_token(data)
		refresh_token_hash = hash_refresh_token(refresh_token)

		device_name = request.headers.get("X-Device-Name")
		
		crud.create_user_session(db, UserSession(
			user_id=user.id,
			refresh_token_hash=refresh_token_hash,
			device_name=device_name,
			ip_address=ip,
			session_id=session_id
		))
	except Exception as e:
		logger.exception("Token Generation Failed")
		return JSONResponse(
			status_code=500,
			content=jsonable_encoder(APIResponse(
				success=True,
				message="Account created succesfully, but automatic login failed. Please log in manually",
				data=None
			))
		)

	response.set_cookie(key='talentforge_refresh_token', value=refresh_token, httponly=True, secure=False, max_age=30*24*60*60)

	return JSONResponse(
		status_code=200,
		content=jsonable_encoder(APIResponse(
		success=True,
		message="Account Created Succesfully",
		data=AuthResponse(user=user, access_token=access_token, token_type="bearer")
	)))


@router.post("/login", response_model=APIResponse)
def login(request: Request, response: Response, user: AuthBase, db: Session=Depends(get_db)):

	db_user = crud.get_user_by_identifier(db, user.identifier)
	ip = request.client.host if request.client else None

	if not db_user:
		return JSONResponse(
			status_code=404,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="Username or email not found",
				data=None
			))
		)

	
	key = f"login_cooldown:{db_user.email}"

	attempts = redis.track_rate_limit(key, 300)
	if attempts and int(attempts) > 3:
		return JSONResponse(
			status_code=429,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="Try again later!"
			))
		)

	if db_user.provider == 'google':
		return JSONResponse(
			status_code=400,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="This account was created using Google Sign-In. Please continue with Google",
				data=None
			))
		)

	password = user.password
	hashed_password = db_user.password_hash 

	try:
		verify_password(password, hashed_password)
	except (VerifyMismatchError, InvalidHashError):
		return JSONResponse(
			status_code=401,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="Invalid Credentials",
				data=None
			))
		)

	session_id = str(uuid.uuid4())
	print("\n\n SESSION ID: ", session_id, "\n\n")
	data = {
		'id': db_user.id,
		'email':db_user.email,
		'username': db_user.username,
		'session_id':session_id
	}
	access_token = create_access_token(data)
	refresh_token = create_refresh_token(data)
	refresh_token_hash = hash_refresh_token(refresh_token)

	device_name = request.headers.get("X-Device-Name")

	crud.create_user_session(db, UserSession(
		user_id=db_user.id,
		refresh_token_hash=refresh_token_hash,
		device_name=device_name,
		ip_address=ip,
		session_id=session_id
	))
	db_user.last_login_at = datetime.now(timezone.utc)
	db.commit()
	db.refresh(db_user)

	response.set_cookie(key=REFRESH_TOKEN_COOKIE_NAME, 
	value=refresh_token, 
	httponly=True, 
	secure=False, 
	max_age=30*24*60*60)

	return APIResponse(
		success=True,
		message="Logged In Succesfully",
		data=AuthResponse(
			user=db_user,
			access_token=access_token,
			token_type="bearer"
		)
	)


@router.post("/logout", response_model=APIResponse)
async def logout(request: Request, response: Response, user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
	crud.revoke_session(db, session_id=user.session_id)

	response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME)

	return JSONResponse(
		status_code=200,
		content=jsonable_encoder(APIResponse(
		success=True,
		message="Logged Out",
		data=jsonable_encoder(response)
	)))

@router.get("/get-all", response_model=APIResponse)
def fetch_all(response: Response, db: Session=Depends(get_db)):
	userList = crud.get_all_users(db)
	users = jsonable_encoder(userList)
	return JSONResponse(
		status_code=200,
		content=jsonable_encoder(APIResponse(
		success= True,
		message= "All Users",
		data= user
	)))