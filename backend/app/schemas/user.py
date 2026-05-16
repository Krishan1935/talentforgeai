from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .profile import ProfileResponse
# USER SCHEMAS

class UserBase(BaseModel):
	fullname : str
	username: str
	email : str 
	password : str
class UserCreate(UserBase):
	pass 
class UserResponse(BaseModel):
	id : int
	fullname: str
	username: str
	email: str
	status: str
	is_active : bool
	role: str
	is_email_verified: bool
	is_phone_verified: bool
	created_at: datetime
	updated_at: datetime

	profile: Optional[ProfileResponse] = None



	model_config = ConfigDict(from_attributes=True)

class AuthBase(BaseModel):
	identifier : str
	password : str

class AuthResponse(BaseModel):
	user: UserResponse
	access_token: str
	token_type: str = "bearer"