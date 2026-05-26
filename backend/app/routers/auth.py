from fastapi import APIRouter, Request, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.encoders import jsonable_encoder
import jwt
import os
import logging
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timezone
import pyotp
import time

from app.config import get_db, oauth, send_mail, EmailSchema, redis_client
from app import schemas, models
from app.services import crud, redis
from app.utils import (create_password_reset_token, 
	hash_password_reset_token, hash_password, generate_otp)
from app.utils import create_access_token, create_refresh_token, verify_password, hash_refresh_token
from app.schemas import (UserResponse, UserCreate, 
	AuthResponse, AuthBase, 
	OAuthUserCreate, UserSession, 
	APIResponse, ForgotPasswordTokenRequest, 
	ForgotPasswordRequest,
	ChangePasswordRequest,
	OTPRequest, OTPVerify)
from app.services import redis


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
		return JSONResponse(
			status_code=400,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="Failed to fetch user info from google",
				data=None
			))
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

	return JSONResponse(
		status_code=200,
		content=jsonable_encoder(APIResponse(
			success=True,
			message="Googel Login Succesful",
			data=AuthResponse(user=db_user, access_token=access_token, token_type="bearer")
	)))

# forgot password
@router.post("/password/reset", response_model=APIResponse)
async def reset_password_token(body: ForgotPasswordTokenRequest, db:Session = Depends(get_db)):
	try:
		email = body.email
		# print("email: ", email)
		user = crud.get_user_by_email(db, email)
		# print(user)

		if not user:
			return JSONResponse(
				status_code=404,
				content=jsonable_encoder(APIResponse(
					success=False,
					message="Email not found!",
					data=None
				))
			)
		
		if user.provider != 'local':
			return JSONResponse(
				status=400,
				content=jsonable_encoder(APIResponse(
				success=False,
				message="Please login using google.",
				data=None
			)))

		try:
			forgot_password_cooldown = f"fp_cooldown:{user.email}"

			exists = redis.track_rate_limit(forgot_password_cooldown, 900)
			if exists and int(exists) > 3:
				return JSONResponse(
					status_code=429,
					content=jsonable_encoder(APIResponse(
						success=False,
						message="You changed your password recently, try again later."
					))
				)

			token, token_hash = create_password_reset_token()

			saved = crud.save_password_reset_token(db, user.id, token_hash)
		except Exception as e:
			db.rollback()
			# print(e)
			return JSONResponse(
				status_code=500,
				content=jsonable_encoder(APIResponse(
					success=False,
					message="Couldn't create or save token",
					data=None
				))
			)

		body = f"Your password reset link is : http://localhost:8000/auth/password/reset-password/{token}"
		mail_response = await send_mail("Password Reset Token", body, email=EmailSchema(email=[email]))

		return JSONResponse(
			status_code=500,
			content=jsonable_encoder(APIResponse(
			success=True,
			message="A password reset link has been sent on your mail.",
			data=None
		)))
	except Exception as e:
		print(e)
		return JSONResponse(
			status_code=500,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="Internal Server Error",
				data=None
			))
		)

@router.post("/password/reset-password/{token}", response_model=APIResponse)
async def reset_password(token: str, data: ForgotPasswordRequest, db: Session = Depends(get_db)):
	token_hash = hash_password_reset_token(token)
	reset_session = crud.get_password_reset_token(db, token_hash)

	if not reset_session or reset_session.used or reset_session.expires_at < datetime.utcnow():
		return JSONResponse(
			status=400,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="Invalid or expired password reset token",
				data=None
			))
		)

	if data.new_password != data.confirm_password:
		return JSONResponse(
			status=400,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="Both the passwords must match",
				data=None
			))
		)

	user = crud.get_user(db, reset_session.user_id)

	if not user:
		return JSONResponse(
			status=404,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="User does not exist",
				data=None
			))
		)

	try: 
		crud.update_password(db, data.new_password, user)
	except IntegrityError as e:
		db.rollback()
		return JSONResponse(
			status=500,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="Couldn't Update Password",
				data=None
			))
		)
	except Exception as e:
		print(e)
		return JSONResponse(
			status=500,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="Internal Server Error",
				data=None
			))
		)

	body = """
	Hello,

	Your password was successfully updated.

	If you made this change, no further action is required.

	If you did not change your password, please secure your account immediately and contact support.

	For security reasons, all active sessions may have been signed out.

	Thank you."""

	subject="Your Password Has Been Updated"

	await send_mail(subject, body, EmailSchema(email=[user.email]))

	return JSONResponse(
		status_code=200,
		content=jsonable_encoder(APIResponse(
		success=True,
		message="Password Updated Succesfully",
		data=None
	)))


@router.post("/password/change-password", response_model=APIResponse)
async def change_password(body: ChangePasswordRequest, db:Session = Depends(get_db)):
	# print("\n\n body: ", body)
	key = f"fp_cooldown:{body.email}"

	attempts = redis.track_rate_limit(key, 900)

	if attempts and int(attempts) >3:
		return JSONResponse(
			status_code=429,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="You changed your password recently, try again later."
			))
		)

	user = crud.get_user_by_email(db, body.email)

	if not user:
		return JSONResponse(
			status_code=404,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="User not found",
				data=None
			))
		)
	
	if user.provider != "local":
		return JSONResponse(
			status_code=400,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="Please login using google",
				data=None
			))
		)
	
	if body.new_password != body.confirm_password:
		return JSONResponse(
			status_code=400,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="Both passwords must match",
				data=None
			))
		)


	try:
		verify_password(body.old_password, user.password_hash)
	except VerifyMismatchError:
		return JSONResponse(
			status_code=401,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="Incorrect Old Password",
				data=None
			))
		)

	try: 
		crud.update_password(db, body.new_password, user)
	except IntegrityError as e:
		db.rollback()
		return JSONResponse(
			status_code=500,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="Couldn't Update Password",
				data=None
			))
		)

	body = """
	Hello,

	Your password was successfully updated.

	If you made this change, no further action is required.

	If you did not change your password, please secure your account immediately and contact support.

	For security reasons, all active sessions may have been signed out.

	Thank you."""

	subject="Your Password Has Been Updated"

	await send_mail(subject, body, EmailSchema(email=[user.email]))

	return JSONResponse(
		status_code=200,
		content=jsonable_encoder(APIResponse(
		success=True,
		message="Password Updated Succesfully",
		data=None
	)))

@router.post("/otp/request", response_model=APIResponse)
async def request_otp(body: OTPRequest):
	try:
		cooldown_key = f"otp_cooldown:{body.email}"

		exists = redis.track_rate_limit(cooldown_key, 300)

		if exists and int(exists) > 3:
			return JSONResponse(
				status_code=429,
				content=jsonable_encoder(APIResponse(
					success=False,
					message="Please wait before generating another OTP"
				))
			)

		otp = generate_otp()

		otp_saved = redis.save_otp(body.email, otp)

		if not otp_saved:
			return JSONResponse(
				status_code=500,
				content=jsonable_encoder(APIResponse(
					success=False,
					message="Failed to save OTP"
				))
			)
		# print("OTP: ", otp)

		subject="OTP for Email Verification"
		message=f"""
		OTP for verification is: {otp}
		"""
		await send_mail(subject, message, EmailSchema(email=[body.email]))

		return JSONResponse(
			status_code=200,
			content=jsonable_encoder(APIResponse(
				success=True,
				message="OTP Sent Succesfully"
			))
		)
	except Exception as e:
		print(e)
		return JSONResponse(
			status_code=500,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="Failed to send OTP"
			))
		)

@router.post("/otp/verify", response_model=APIResponse)
async def verify_otp(body: OTPVerify):
	try:
		otp = body.otp
		email = body.email
		result = redis.verify_otp(email, otp)


		if not result["success"]:
			return JSONResponse(
				status_code=400,
				content=jsonable_encoder(APIResponse(
					success=False,
					message=result["message"]
				))
			)

		return JSONResponse(
			status_code=200,
			content=jsonable_encoder(APIResponse(
				success=True,
				message="OTP Verified"
			))
		)
	except Exception as e:
		return JSONResponse(
			status_code=500,
			content=jsonable_encoder(APIResponse(
				success=False,
				message="OTP Verificatin Failed"
			))
		)