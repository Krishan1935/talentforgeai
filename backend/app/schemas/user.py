from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any
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
	last_login_at: datetime

	profile: Optional[ProfileResponse] = None

	model_config = ConfigDict(from_attributes=True)

class OAuthUserCreate(BaseModel):
	email: str
	fullname: str
	provider: str
	provider_id: str

class AuthBase(BaseModel):
	identifier : str
	password : str

class AuthResponse(BaseModel):
	user: UserResponse
	access_token: str
	token_type: str = "bearer"

class UserSession(BaseModel):
	user_id: int
	refresh_token_hash: str
	device_name: Optional[str] = None
	ip_address: str

class APIResponse(BaseModel):
	success: bool
	message: str
	data: Optional[Any] = None