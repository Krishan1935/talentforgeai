from fastapi import Depends, HTTPException, status, Cookie, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from typing import Optional
from app.schemas import TokenData
from app.services import crud
from app.config import get_db
from app.utils import create_access_token
# bearer_scheme = HTTPBearer()

def get_current_user(request: Request, db: Session = Depends(get_db)) -> TokenData:
    token = None
    header = request.headers.get("Authorization")
    if header and header.startswith("Bearer "):
        token = header.split(" ")[1]

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET"),
            algorithms=["HS256"]
        )     

        if payload["type"] != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid Token Type"
            )
        print("SESSION ID : ", payload)
        session = crud.get_session(db, payload["session_id"])
        print('SESSION: ', session)
        if not session:
            raise HTTPException(
                status=401,
                detail="Session not found"
            )

        return TokenData(
            id=payload["id"],
            email=payload["email"],
            username=payload["username"],
            session_id=payload["session_id"],
            exp=payload["exp"],
            type=payload["type"]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token Expired"
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )
