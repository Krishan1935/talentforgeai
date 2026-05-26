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


