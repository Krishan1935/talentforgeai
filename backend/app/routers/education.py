from fastapi import APIRouter, Depends, HTTPException, Response, Request, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import datetime, timezone


from app.config import get_db
from app.services.crud import upload_education, update_education, delete_education, get_education
from app.schemas.user import APIResponse
from app.schemas.auth import TokenData
from app.schemas.education import EducationResponse, EducationBase
from app.utils import get_current_user
from app.services.files import upload_avatar, delete_avatar

router = APIRouter()

@router.post("/add", response_model=APIResponse)
def add_education(data: EducationBase, user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        print("Data: ", data)
        education = upload_education(db, data, user.id)

        return JSONResponse(
            status_code=201,
            content=jsonable_encoder(APIResponse(
                success=True,
                message="Education Added",
                data = EducationResponse.model_validate(education)
            ))
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(APIResponse(
                success=False,
                message=f"Unexpected Error Occured {str(e)}"
            ))
        )