from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db
from .. import schemas, models, crud

from ..schemas import UserResponse, UserCreate

from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: schemas.UserCreate, db: Session=Depends(get_db)):
	db_user = crud.get_user_by_email(db, user.email)

	if db_user:
		raise HTTPException(status_code=400, detail="Email already registered!")
	return crud.create_user(db, user)

@router.get("/get-all", response_model=UserResponse)
def fetch_all(db: Session=Depends(get_db)):
	userList = crud.get_all_users(db)