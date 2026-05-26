from sqlalchemy.orm import Session
from sqlalchemy import or_, delete, select, func
import uuid
from datetime import datetime, timezone, timedelta

from app import schemas
from app.models import User, Profile
from app.schemas import ProfileBase


def update_profile(profile: ProfileBase, db: Session):
    profile_data = profile.model_dump()

    filled = sum()