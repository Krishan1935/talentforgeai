from app.config.redis import redis_client
from redis.exceptions import RedisError

OTP_EXPIRY=300

def save_otp(email: str, otp: str):
    try:
        redis_client.set(
            f"otp:{email}",
            ex=OTP_EXPIRY,
            value=otp
        )
        return True
    except RedisError as e:
        return False

def verify_otp(email: str, user_otp: str):
    try:
        stored_otp = redis_client.get(f"otp:{email}")

        if not stored_otp:
            return {
                "success":False,
                "message":"OTP Expired or not found"
            }
        
        if stored_otp != user_otp:
            return {
                "success":False,
                "message":"Invalid OTP"
            }
        
        redis_client.delete(f"otp:{email}")

        redis_client.set(
            f"verified:{email}",
            ex=600,
            value=1
        )
        return {
            "success":True,
            "message":"OTP Verified"
        }
    except RedisError as e:
        return {
            "success":False,
            "message":"Redis Server Error"
        }