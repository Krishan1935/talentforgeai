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

	model_config = ConfigDict(from_attributes=True)

class UserSession(BaseModel):
	user_id: int
	refresh_token_hash: str
	device_name: Optional[str] = None
	ip_address: str
	session_id: str

class TokenData(BaseModel):
	id: int
	email: str 
	username: str 
	session_id : str

class ForgotPasswordTokenRequest(BaseModel):
	email: str

class ForgotPasswordRequest(BaseModel):
	new_password: str
	confirm_password: str 

class ChangePasswordRequest(BaseModel):
	email: str
	old_password: str
	new_password: str
	confirm_password: str

class OTPRequest(BaseModel):
	email: str
	username: Optional[str] = None

class OTPVerify(OTPRequest):
	otp: str

from .user import UserResponse

AuthResponse.model_rebuild()