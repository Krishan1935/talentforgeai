from sqlalchemy.orm import Session
from sqlalchemy import or_, delete, select, func
import uuid
from datetime import datetime, timezone, timedelta

from app import schemas
from app.models import User, Profile
from app.schemas import ProfileBase


def update_profile(db: Session, profile: ProfileBase, user_id: int):
    profile_data = profile.model_dump(exclude_unset=True)

    existing = db.query(Profile).filter(
        Profile.user_id == user_id
    ).first()

    for key, value in profile_data.items():
        setattr(existing, key, value)

    fields = [
        existing.display_name,
        existing.bio,
        existing.avatar_url,
        existing.date_of_birth,
        existing.gender,
        existing.linkedin_link,
        existing.github_link
    ]

    filled = sum(1 for value in fields if value is not None and value != "")
    total = len(fields)
    
    existing.profile_progress = int((filled/total) * 100) if total > 0 else 0

    db.commit()
    db.refresh(existing)
    return existing
