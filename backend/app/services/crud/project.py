from sqlalchemy.orm import Session
from sqlalchemy import or_, delete, select, func
import uuid
from datetime import datetime, timezone, timedelta

from app.models import Project
from app.schemas import ProjectBase, ProjectResponse


def save_project(data: ProjectBase, user_id: int, db: Session):
    project_data =data.model_dump()

    new_project = Project()
    for key, value in project_data.items():
        setattr(new_project, key, value)

    new_project.user_id = user_id

    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

def update_project(data: ProjectBase, user_id: int, project_id: int, db: Session):
    project_data = data.model_dump(exclude_unset=True)

    existing_project = db.query(Project)\
        .filter(Project.id == project_id,
                Project.user_id == user_id)\
                    .first()

    if not existing_project:
        return None

    for key, value in project_data.items():
        setattr(existing_project, key, value)
    
    db.commit()
    db.refresh(existing_project)
    return existing_project

def fetch_projects(user_id: int, db: Session):
    return db.query(Project)\
        .filter(Project.user_id == user_id).all()


def delete_project(project_id: int, user_id: int, db: Session)-> bool:
    existing_project = db.query(Project)\
        .filter(Project.id == project_id,
                Project.user_id == user_id).first()

    if not existing_project: return False

    db.delete(existing_project)
    db.commit()
    return True