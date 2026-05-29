from fastapi import APIRouter, Depends, HTTPException, Response, Request, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import datetime, timezone
import uuid
from dotenv import load_dotenv
import os
load_dotenv()

from app.config import get_db
from app.services import crud
from app.services.files.storage import get_signed_upload_url
from app.schemas.user import APIResponse
from app.schemas.auth import TokenData
from app.schemas.resume import UploadURLRequest
from app.utils import get_current_user
from app.config.Supabase import supabase

router = APIRouter()

ALLOWED_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}
MAX_SIZE = 5*1024*1024
@router.post("/upload-url", response_model=APIResponse)
def get_upload_url(body:UploadURLRequest, user : TokenData = Depends(get_current_user)):
    try:
        # print("\n\n URL HIT")
        # print("\n\n BODY: ", body)
        if body.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Invalid File Type"
            )
        
        if body.file_size > MAX_SIZE:
            raise HTTPException(
                400,
                "File too large. Max 5MB"
            )
        
        ext = body.filename.rsplit(".", 1)[-1]

        file_key = f"resumes/{user.id}/{uuid.uuid4()}.{ext}"

        url = get_signed_upload_url(os.getenv("SUPABASE_CV_BUCKET"), file_key)

        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(APIResponse(
                success=True,
                message="Signed URL",
                data=url
            ))
        )

    except HTTPException as e:
        # print(e)
        return JSONResponse(
            status_code=e.status_code,
            content=jsonable_encoder(APIResponse(
            success=False,
            message=f"{e.detail}"
        )))

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(APIResponse(
                success=False,
                message=f"Unexpected Error Occured: {str(e)}"
            ))
        )
