from fastapi import APIRouter, Request, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import jwt
import os
import logging

from ..config import get_db, oauth
from .. import schemas, models, crud
from ..utils import create_access_token, create_refresh_token, verify_password
from ..schemas import UserResponse, UserCreate, AuthResponse, AuthBase, OAuthUserCreate

router = APIRouter()

logger = logging.getLogger(__name__)

REFRESH_TOKEN_COOKIE_NAME = 'talentforge_refresh_token'


@router.get("/google/login")
async def google_login(request: Request):
	# redirect_uri = request.url_for("google_callback")
	redirect_uri = "http://localhost:8000/auth/google/callback"
	return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback", name="google_callback", response_model=AuthResponse)
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
	        	ip=ip
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

	response.set_cookie(key=REFRESH_TOKEN_COOKIE_NAME, value=refresh_token)

	return {
		"user": db_user,
		"access_token": access_token,
		"token_type": "bearer"
	}