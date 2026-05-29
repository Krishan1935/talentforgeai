from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime
from typing import Optional
from datetime import datetime, date

class UploadURLRequest(BaseModel):
    filename: str
    content_type: str
    file_size: int