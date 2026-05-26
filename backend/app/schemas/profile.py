from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from datetime import datetime, date

class ProfileBase(BaseModel):
	display_name: Optional[str] = None
	bio: Optional[str] = None
	avatar_url: Optional[str] = None
	date_of_birth: Optional[date] = None
	gender: Optional[str] = None

class ProfileCreate(ProfileBase):
	pass 

class ProfileResponse(ProfileBase):
	id: int
	user_id: int

	class Config: 
		from_attributes=True