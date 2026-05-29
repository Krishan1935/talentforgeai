from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime
from typing import Optional
from datetime import datetime, date

class UploadURLRequest(BaseModel):
    filename: str
    content_type: str
    file_size: int

class ConfirmUploadRequest(BaseModel):
    file_key: str

class SaveResumeRequest(BaseModel):
    title: str
    file_url: str
    is_primary: bool


class SaveResumeResponse(SaveResumeRequest):
    id: int
    created_at: datetime
    user_id: int

    model_config = ConfigDict(from_attributes=True)