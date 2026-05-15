from argon2 import PasswordHasher
ph = PasswordHasher()
# hash = ph.hash("my_secret_password")
# ph.verify(hash, "my_secret_password")  # Returns True or raises error



def hash_password(password: str) -> str:
	return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
	return ph.verify(plain_password, hashed_password)