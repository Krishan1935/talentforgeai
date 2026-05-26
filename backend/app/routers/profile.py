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
from app.services import crud, redis
from app.schemas import ProfileBase, ProfileResponse, APIResponse, UserResponse
from app.utils import get_current_user

router = APIRouter()

@router.post("/update", response_model=APIResponse)
def update_profile(body: ProfileBase, db: Session = Depends(get_db), user: UserResponse = Depends(get_current_user)):
    email = user.email

    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(APIResponse(
            success=True,
            message="update profile",
            data=user
        ))
    )