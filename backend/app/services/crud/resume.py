from sqlalchemy.orm import Session
from sqlalchemy import or_, delete, select, func
import uuid
from datetime import datetime, timezone, timedelta

from app.models import Resume
from app.schemas.resume import SaveResumeRequest, SaveResumeResponse


def save_resume(db: Session, data: SaveResumeRequest, user_id: int):
    data = data.model_dump()

    new_resume = Resume()
    for key, value in data.items():
        setattr(new_resume, key, value)

    new_resume.user_id = user_id

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    return new_resume

def fetch_resume(db: Session, resume_id: int, user_id: int):
    return db.query(Resume)\
        .filter(Resume.id == resume_id,
                Resume.user_id == user_id).first()

def delete_resume(db: Session, resume_id: int, user_id: int):
    resume = db.query(Resume)\
        .filter(Resume.id == resume_id,
                Resume.user_id == user_id).first()

    db.delete(resume)
    db.commit()
