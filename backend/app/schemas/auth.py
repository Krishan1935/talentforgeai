from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any
from .profile import ProfileResponse

class OAuthUserCreate(BaseModel):
	email: str
	fullname: str
	provider: str
	provider_id: str

class AuthBase(BaseModel):
	identifier : str
	password : str

class AuthResponse(BaseModel):
	user: "UserResponse"
	access_token: str
	token_type: str = "bearer"

class UserSession(BaseModel):
	user_id: int
	refresh_token_hash: str
	device_name: Optional[str] = None
	ip_address: str

class TokenData(BaseModel):
	id: int
	email: str 
	username: str 

class ForgotPasswordTokenRequest(BaseModel):
	email: str

class ForgotPasswordTokenResponse(BaseModel):
	id: int
	token_hash: str
	expires_at: datetime
	used: bool
	user_id: int

	model_config = ConfigDict(from_attributes=True)

class ForgotPasswordRequest(BaseModel):
	new_password: str
	confirm_password: str 

from .user import UserResponse

AuthResponse.model_rebuild()