from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from datetime import datetime, date, UTC

from app.models import Experience
from app.schemas import ExperienceBase, ExperienceResponse

def save_experience(data: ExperienceBase, user_id: int, db: Session):
    exp_data = data.model_dump()

    new_exp = Experience()

    for key, value in exp_data.items():
        setattr(new_exp, key, value)

    new_exp.user_id = user_id

    db.add(new_exp)
    db.commit()
    db.refresh(new_exp)
    return new_exp

def update_experience(data: ExperienceBase, exp_id: int, user_id: int, db: Session):
    exp_data = data.model_dump(exclude_unset=True)

    existing = db.query(Experience)\
        .filter(Experience.id == exp_id,
                Experience.user_id == user_id)\
                    .first()

    if not existing: return None

    for key, value in exp_data.items():
        setattr(existing, key, value)

    if exp_data["is_present"]:
        existing.end_date = None

    db.commit()
    db.refresh(existing)
    return existing

def fetch_experiences(user_id: int, db: Session):
    return db.query(Experience)\
        .filter(Experience.user_id == user_id)\
            .all()

def delete_experience(exp_id: int, user_id: int, db: Session) -> bool:
    existing = db.query(Experience)\
        .filter(Experience.id == exp_id,
                Experience.user_id == user_id)\
                    .first()

    if not existing: return False

    db.delete(existing)
    db.commit()
    return True