from fastapi import Depends, HTTPException, status, Cookie, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from dotenv import load_dotenv
load_dotenv()
from typing import Optional
from app.schemas import TokenData
bearer_scheme = HTTPBearer()

def get_current_user(request: Request, talentforge_access_token: Optional[str] = Cookie(default=None)) -> TokenData:
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
            token,
            os.getenv("JWT_SECRET"),
            algorithms=["HS256"]
        )

        return TokenData(
            id=payload["id"],
            email=payload["email"],
            username=payload["username"],
            session_id=payload["session_id"]
        )
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=401, 
            content=jsonable_encoder(APIResponse(
            success=True,
            message="Token Expired",
            data=None
	    )))
    except Exception as e:
        print("Exception 1 : \n\n", e)  
        return JSONResponse(
            status_code=401,
            content=jsonable_encoder(APIResponse(
            success=True,
            message="Invalid token",
            data=None
	    )))
