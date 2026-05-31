from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime, date
from typing import Optional

class ExperienceBase(BaseModel):
    institution: str
    start_date: date
    end_date: Optional[date] = None
    is_present: bool
    role: str
    description: Optional[str] = None

class ExperienceResponse(ExperienceBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)