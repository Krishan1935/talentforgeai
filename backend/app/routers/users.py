from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from ..database import get_db
from .. import schemas, models, crud
from ..utils import create_access_token, create_refresh_token
from ..schemas import UserResponse, UserCreate, AuthResponse

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/register", response_model=AuthResponse)
def register(response: Response, user: schemas.UserCreate, db: Session=Depends(get_db)):
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

	response.set_cookie(key='talentforge_refresh_token', value=refresh_token, httponly=True, secure=False, max_age=40*24*60*60)

	return {
		"user": user,
		"access_token": access_token,
		"token_type": "bearer"
	}



@router.get("/get-all", response_model=list[UserResponse])
def fetch_all(response: Response, db: Session=Depends(get_db)):
	userList = crud.get_all_users(db)
	return userList