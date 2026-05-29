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
from app.services.files.storage import (get_signed_upload_url, 
    confirm_upload_url, 
    get_signed_view_url,
    remove_file)
from app.schemas.user import APIResponse
from app.schemas.auth import TokenData
from app.schemas.resume import UploadURLRequest, ConfirmUploadRequest, SaveResumeRequest, SaveResumeResponse
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

@router.post("/confirm", response_model=APIResponse)
def confirm_upload(file: ConfirmUploadRequest, body: SaveResumeRequest,
user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        response = confirm_upload_url(os.getenv("SUPABASE_CV_BUCKET"), file.file_key)

        print("\n\n", file.file_key.split("/", 1)[0])
        if not response:
            raise HTTPException(
                404,
                "File not found in storage"
            )

        resume = crud.save_resume(db, body, user.id)

        view_url = get_signed_view_url(os.getenv("SUPABASE_CV_BUCKET"), file.file_key, 60*3)

        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(APIResponse(
                success=True,
                message="Resume Saved Succesfully",
                data={**SaveResumeResponse.model_validate(resume).model_dump(), 
                    "view_url":view_url}
            ))
        )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content=jsonable_encoder(APIResponse(
            success=False,
            message=f"{e.detail}"
        )))
    except IntegrityError:
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(APIResponse(
            success=False,
            message=f"Cannot save file to database"
        )))
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(APIResponse(
            success=False,
            message=f"Unexpected Error Occured: {str(e)}"
        )))


@router.delete("/delete/{resume_id}", response_model=APIResponse)
def delete_resume(resume_id: int, user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    try:

        resume = crud.fetch_resume(db, resume_id, user.id)

        if not resume:
            raise HTTPException(
                status_code=404,
                detail="Resume not found"
            )

        file_path = resume.file_url

        response = remove_file(os.getenv("SUPABASE_CV_BUCKET"), [file_path])

        if not response:
            raise HTTPException(
                status_code=500,
                detail="Could not delete file"
            )

        crud.delete_resume(db, resume_id, user.id)

        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(APIResponse(
                success=True,
                message="Resume Deleted"
            ))
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content=jsonable_encoder(APIResponse(
                success=False,
                message=e.detail
            ))
        )


@router.get("/fetch/{resume_id}", response_model=APIResponse)
def fetch_resume(resume_id: int, user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        resume = crud.fetch_resume(db, resume_id, user.id)

        if not resume:
            raise HTTPException(
                404,
                "Resume not found"
            )
        
        view_url = get_signed_view_url(os.getenv("SUPABASE_CV_BUCKET"), resume.file_url, 60*3)

        if not view_url:
            raise HTTPException(
                404,
                "Resume not found in storage"
            )
        
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=True,
                message="Resume Fetched",
                data=view_url
            )),
            200
        )
    
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content=jsonable_encoder(APIResponse(
                success=False,
                message=e.detail
            ))
        )