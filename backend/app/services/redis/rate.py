from app.config import redis_client

def track_rate_limit(key: str, expiry: int = 300):
    pipe = redis_client.pipeline()

    pipe.incr(key)
    pipe.expire(key, expiry, nx=True)

    result = pipe.execute()

    return result[0]