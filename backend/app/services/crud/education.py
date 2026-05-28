from sqlalchemy.orm import Session
from sqlalchemy import or_, delete, select, func
import uuid
from datetime import datetime, timezone, timedelta

from app.models import User, Education
from app.schemas import EducationBase, EducationResponse


def upload_education(db: Session, data: EducationBase, user_id: int) -> Education:
    new_education = Education(
        **data.model_dump(),
        user_id = user_id
    )

    db.add(new_education)
    db.commit()
    db.refresh(new_education)
    return new_education

def get_education( db: Session, user_id: int) -> list[Education]:
    return db.query(Education)\
        .filter(Education.user_id == user_id)\
            .order_by(Education.start_date.desc()).all()

def update_education( db: Session, data: EducationBase, education_id: int, user_id: int) -> Education:
    existing = db.query(Education)\
        .filter(Education.id == education_id,
                Education.user_id == user_id)\
                    .first()
    if not existing:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)
    return existing

def delete_education(db: Session, education_id: int, user_id: int) -> bool:
    existing = db.query(Education)\
        .filter(Education.id == education_id,
                Education.user_id == user_id)\
                    .first()
    if not existing:
        return False
    
    db.delete(existing)
    db.commit()
    return True