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
	github_link: Optional[str] = None
	linkedin_link: Optional[str] = None
	skills: Optional[list[str]] = None

class ProfileResponse(ProfileBase):
	id: int
	user_id: int
	profile_progress: int

	class Config: 
		from_attributes=True