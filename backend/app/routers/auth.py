from fastapi import APIRouter, Request, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import jwt
import os
import logging

from ..config import get_db, oauth, send_mail, EmailSchema
from .. import schemas, models, crud
from ..utils import create_password_refresh_token
from ..utils import create_access_token, create_refresh_token, verify_password, hash_refresh_token
from ..schemas import UserResponse, UserCreate, AuthResponse, AuthBase, OAuthUserCreate, UserSession, APIResponse, ForgotPasswordRequest, ForgotPasswordResponse

router = APIRouter()

logger = logging.getLogger(__name__)

REFRESH_TOKEN_COOKIE_NAME = 'talentforge_refresh_token'


@router.get("/google/login")
async def google_login(request: Request):
	# redirect_uri = request.url_for("google_callback")
	redirect_uri = "http://localhost:8000/auth/google/callback"
	response = await oauth.google.authorize_redirect(request, redirect_uri)
	return response

@router.get("/google/callback", name="google_callback", response_model=APIResponse)
async def google_callback(request: Request, response: Response, db: Session = Depends(get_db)):
	token = await oauth.google.authorize_access_token(request)
	user_info = token.get("userinfo")

	ip = request.client.host

	if not user_info:
		raise HTTPException(
			status_code=400,
			detail="Failed to fetch user info from google"
		)

	db_user = crud.get_user_by_email(db, email=user_info['email'])
	if not db_user:
	    try:
	        db_user = crud.create_oauth_user(db, OAuthUserCreate(
	        	email= user_info['email'],
	        	fullname= user_info['name'],
	        	provider= "google",
	        	provider_id=user_info['sub'],
	        ))
	    except IntegrityError:
	        db.rollback()
	        # race condition or duplicate -- just fetch the existing user
	        db_user = crud.get_user_by_email(db, email=user_info['email'])

	data = {
	"id": db_user.id,
	"email":db_user.email,
	"username":db_user.username
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

	response.set_cookie(key=REFRESH_TOKEN_COOKIE_NAME, value=refresh_token, httponly=True, secure=False, max_age=30*24*60*60)

	return APIResponse(
		success=True,
		message="Googel Login Succesful",
		data=AuthResponse(user=db_user, access_token=access_token, token_type="bearer")
	)

# forgot password
@router.post("/password/reset")
async def reset_password(request: Request, response: Response, body: ForgotPasswordRequest, db:Session = Depends(get_db)):
	try:
		email = body.email
		print("email: ", email)
		user = crud.get_user_by_email(db, email)
		print(user)

		if not user:
			raise HTTPException(status_code=404, detail="Email not found!")

		try:
			reset_token = create_password_refresh_token()

			saved = crud.save_password_reset_token(db, reset_token, user.id)
		except Exception as e:
			raise HTTPException(status_code=500, detail="Couldn't create or save token")

		body = f"Your password reset link is : http://localhost:8000/auth/password/reset-password/{saved.token_hash}"
		mail_response = await send_mail("Password Reset Token", body, email=EmailSchema(email=[email]))

		return APIResponse(
			success=True,
			message="A password reset link has been sent on your mail.",
			data=None
		)
	except Exception as e:
		print(e)