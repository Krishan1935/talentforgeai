from sqlalchemy.orm import Session
from sqlalchemy import or_, delete, select, func
import uuid
from datetime import datetime, timezone, timedelta

from app import models, schemas
from app.utils import hash_password, REFRESH_TOKEN_EXPIRE_DAYS
from app.models import User, Profile, UserSession, PasswordResetToken




def create_oauth_user(db: Session, user: schemas.OAuthUserCreate):

	base_username = user.fullname.lower().replace(" ", "_")  # "krishan_kumar"
	username =	f"{base_username}_{str(uuid.uuid4())[:6]}"
	db_user = User(
		email= user.email,
		fullname=user.fullname,
		username = username,
		provider=user.provider,
		provider_id = user.provider_id,
		password_hash= None,
		is_email_verified=True,
		last_login_at=datetime.utcnow(),
	)

	db_profile = Profile(
		display_name= db_user.fullname
	)
	db_user.profile = db_profile

	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	return db_user

def create_user_session(db: Session, user_session: schemas.UserSession):
	db_session = UserSession(
		user_id = user_session.user_id,
		refresh_token_hash = user_session.refresh_token_hash,
		device_name = user_session.device_name,
		ip_address = user_session.ip_address,
		is_revoked=False,
		expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
	)
	db.add(db_session)
	db.commit()

def delete_user_session(db: Session, user_id: int):
	session = db.query(UserSession)\
		.filter(UserSession.user_id == user_id)\
		.order_by(UserSession.created_at.desc())\
		.first()

	session.is_revoked = True
	session.revoked_at = func.now()
	db.commit()
	db.refresh(session)




def save_password_reset_token(db: Session, token: str, user_id: int):
	db_token = PasswordResetToken(
		user_id= user_id,
		token_hash= token,
		expires_at= datetime.utcnow() + timedelta(minutes=15)
	)

	db.add(db_token)
	db.commit()
	db.refresh(db_token)
	return db_token

def get_password_reset_token(db: Session, token: str):
	return db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token)\
	.first()


def update_password(db: Session, password: str, user: User, session_id: int):
    hashed = hash_password(password)

    user.password_hash = hashed
    user.password_changed_at = datetime.utcnow()

    db.query(PasswordResetToken).filter(PasswordResetToken.id == session_id)\
    .update({
        PasswordResetToken.used : True,
    })

    db.query(UserSession).filter(UserSession.user_id == user.id)\
    .update({
        UserSession.is_revoked: True,
        UserSession.revoked_at: datetime.utcnow()
    })

    db.commit()
    db.refresh(user)
    return user