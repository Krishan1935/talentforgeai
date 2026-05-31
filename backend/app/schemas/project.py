from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional


class ProjectBase(BaseModel):
    title: str
    description: str
    project_url: Optional[str] = None
    skills_used: list[str] = None
    start_date: date
    end_date: Optional[date] = None
    institution: Optional[str] = None
    is_ongoing: bool

class ProjectResponse(ProjectBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)