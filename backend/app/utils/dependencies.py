from fastapi import Depends, HTTPException, status, Cookie, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from typing import Optional

bearer_scheme = HTTPBearer()

def get_current_user(
    request: Request,
    talentforge_access_token: Optional[str] = Cookie(default=None)
) -> TokenData:
    token = None
    header = request.headers.get("Authorization")
    if header and header.startswith("Bearer "):
        token = header.split(" ")[1]

    if not token:
        token = talentforge_access_token

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:

        payload = jwt.decode(
            credentials.credentials,
            os.getenv("SECRET_KEY"),
            algorithms=["HS256"]
        )
        return TokenData(
            id=payload["id"],
            email=payload["email"],
            username=payload["username"]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")