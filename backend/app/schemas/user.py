from pydantic import BaseModel, ConfigDict
from datetime import datetime
# USER SCHEMAS

class UserBase(BaseModel):
	fullname : str
	username: str
	email : str 
	password_hash : str
class UserCreate(UserBase):
	pass 
class User(BaseModel):
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



	model_config = ConfigDict(from_attributes=True)