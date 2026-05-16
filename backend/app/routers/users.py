from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db
from .. import schemas, models, crud
import logging

from ..schemas import UserResponse, UserCreate

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserResponse)
def register(user: schemas.UserCreate, db: Session=Depends(get_db)):
	try:
		return crud.create_user(db, user)
		
	except IntegrityError as e:
		db.rollback()

		logger.warning("Registration conflict: %s", e.orig)
		raise HTTPException(
			status_code=409,
			detail="A user with this email or username already exists"
		)




@router.get("/get-all", response_model=UserResponse)
def fetch_all(db: Session=Depends(get_db)):
	userList = crud.get_all_users(db)