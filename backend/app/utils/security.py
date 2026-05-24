from argon2 import PasswordHasher
import secrets
import hashlib
# hash = ph.hash("my_secret_password")
# ph.verify(hash, "my_secret_password")  # Returns True or raises error
import jwt
import os 
from dotenv import load_dotenv
from datetime import datetime,timedelta,timezone
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
ACCESS_TOKEN_EXPIRE_MINUTES= 15
REFRESH_TOKEN_EXPIRE_DAYS = 30
ALGORITHM = "HS256"

ph = PasswordHasher()

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is required")

def hash_password(password: str) -> str:
	return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
	return ph.verify(hashed_password, plain_password)

def create_access_token(data: dict) -> str:
	payload = data.copy()

	expire = datetime.now(timezone.utc)+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

	payload['exp'] = expire
	payload['type'] = 'access'

	token = jwt.encode(
		payload,
		JWT_SECRET,
		algorithm=ALGORITHM
	)

	return token 

def create_refresh_token(data: dict) -> str:
	payload = data.copy()

	expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

	payload['exp'] = expire
	payload['type'] = 'refresh'

	token = jwt.encode(
		payload,
		JWT_SECRET,
		algorithm=ALGORITHM
	)
	return token

def create_password_reset_token() -> str:
	token = secrets.token_urlsafe(32)

	token_hash = hashlib.sha256(token.encode()).hexdigest()
	return token, token_hash

def hash_password_reset_token(token: str)->str:
	return hashlib.sha256(token.encode()).hexdigest()

def hash_refresh_token(token: str) -> str:
	return ph.hash(token)