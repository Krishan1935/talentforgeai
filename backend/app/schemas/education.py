from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime
from typing import Optional
from datetime import datetime, date

class EducationBase(BaseModel):
    institution: str
    degree: Optional[str] = None
    field_of_study:Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    grade: Optional[str] = None
    description: Optional[str] = None
    is_current: bool = False

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date cannot be before start_date")
        return self

class EducationResponse(EducationBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)