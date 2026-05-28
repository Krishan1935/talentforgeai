from fastapi import APIRouter, Depends, HTTPException, Response, Request, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from sqlalchemy import func
from datetime import datetime, timezone
import uuid
import cloudinary

from app.config import get_db
from app.services import crud, redis
from app.schemas import ProfileBase, ProfileResponse, APIResponse, UserResponse, TokenData
from app.utils import get_current_user
from app.services.files import upload_avatar, delete_avatar

router = APIRouter()

@router.post("/update", response_model=APIResponse)
def update_profile(body: ProfileBase, db: Session = Depends(get_db), user: TokenData = Depends(get_current_user)):
    try:
        updated_profile = crud.upload_profile(db, body, user.id)
        
        # updated_user = crud.get_user_by_email(db, user.email)
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(APIResponse(
                success=True,
                message="Profile Updated",
                data=ProfileResponse.model_validate(updated_profile)
            ))
        )
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(APIResponse(
                success=True,
                message="Can not update profile"
            ))
        )
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(APIResponse(
                success=False,
                message="Internal Server Error"
            ))
        )

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_SIZE = 5 * 1024 * 1024
@router.post("/avatar")
async def update_avatar(file: UploadFile = File(...), user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    # print("FILE: ",file)
    # print("USER: ", user)

    if file.content_type not in ALLOWED_TYPES:
        return JSONResponse(
            status_code=400,
            content=jsonable_encoder(APIResponse(
                success=False,
                message="Only JPEG, PNG, WebP Allowed"
            ))
        )
    try:
        content = await file.read()
    except Exception:
        return JSONResponse(
            status_code=400,
            content=jsonable_encoder(APIResponse(
                success=False,
                message="Failed to read file"
            ))
        )
    # print("CONTENT: ", content)
    if len(content) > MAX_SIZE:
            return JSONResponse(
                status_code=400,
                content=jsonable_encoder(APIResponse(
                    success=False,
                    message="File too large. Max 5MB"
                ))
            )

    if len(content) == 0:
        return JSONResponse(
            status_code=400,
            content=jsonable_encoder(APIResponse(
                success=False,
                message="File is empty"
            ))
        )

    try:
        url = upload_avatar(content, user.id)
    except cloudinary.exceptions.Error as e:
        return JSONResponse(
            status_code=502,
            content=jsonable_encoder(APIResponse(
                success=False,
                message=f"Image upload failed: {str(e)}"
            ))
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(APIResponse(
                success=False,
                message=f"Unexpected error during upload"
            ))
        )

    try:
        updated_profile = ProfileBase(
            avatar_url = url
        )

        crud.upload_profile(db, updated_profile, user.id)
        # updated_user = crud.get_user_by_email(db, user.email)
    except Exception:
        delete_avatar(user.id)
        db.rollback()
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(APIResponse(
                success=False,
                message=f"Failed to update profile"
            ))
        )

    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(APIResponse(
            success=True,
            message="Avatar Updated",
            data=url
        ))
    )